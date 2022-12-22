from bets import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.utils import translation

from tournament.utils import get_finished_bets, get_ongoing_bets, player_results, \
    get_matches_to_bet, get_classification, get_historical_classification, simulate_classification, get_stats_classification

from tournament.forms import Vote, ChooseUser, ChooseMatch, ChooseMatchResult, EmailChangeForm, NotificationChangeForm
from tournament.db_handler import get_user, bet_list, get_match, add_bet, update_goals_bet, does_user_exist, create_user, \
    get_tournament
from django.views.generic import TemplateView, FormView
from django.utils.decorators import method_decorator

from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.forms import PasswordChangeForm


class LoginHandling:
    """
    Generalnie sprawdza ktora stona jest dosteppna dla Guset a ktora nie
    """
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.has_perm('tournament.add_bet'):  # TODO: permission - moze ladniej jakos zrobiz zeby handlowac guest'a
            # return redirect('/tournament/not_allowed')
            return HttpResponseRedirect(reverse('not_allowed'))
        return super().dispatch(request, *args, **kwargs)

    class Meta:
        abstract = True


class LoginAsGuest(TemplateView):
    template_name = 'tournament/index.html'

    def dispatch(self, request, *args, **kwargs): #TODO: user_name i passwd przerzucic do settings albo .env
        if not does_user_exist(user_name="guest"):
            create_user("guest", "ball1234")
        user = authenticate(username="guest", password="ball1234")
        login(request, user)
        return super(LoginAsGuest, self).dispatch(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class Index(TemplateView):
    template_name = 'tournament/index.html'

@method_decorator(login_required, name='dispatch')
class Info(TemplateView):
    template_name = 'tournament/info.html'

@method_decorator(login_required, name='dispatch')
class NotAllowed(TemplateView):
    template_name = 'tournament/not_allowed.html'

@method_decorator(login_required, name='dispatch')
class VoteDone(TemplateView):
    template_name = 'tournament/vote_done.html'

@method_decorator(login_required, name='dispatch')
class VoteChangeDone(TemplateView):
    template_name = 'tournament/vote_change_done.html'

@method_decorator(login_required, name='dispatch')
class History(TemplateView):
    template_name = 'tournament/history.html'

@method_decorator(login_required, name='dispatch')
class PasswordChangeDone(TemplateView):
    template_name = 'registration/change_password_done.html'

@method_decorator(login_required, name='dispatch')
class EmailChangeDone(TemplateView):
    template_name = 'registration/email_change_done.html'

@method_decorator(login_required, name='dispatch')
class NotificationChangeDone(TemplateView):
    template_name = 'registration/notification_change_done.html'

class Logout(TemplateView):
    template_name = 'registration/logout.html'

    def dispatch(self, request, *args, **kwargs):
        #self.request.session.flush()
        self.request.session.clear()
        return super().dispatch(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class TournamentHistory(TemplateView):
    template_name = 'tournament/tournament_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tournament_name'] = self.kwargs['tournament_name']
        context['points_per_user'] = get_historical_classification(tournament_name=self.kwargs['tournament_name'])
        return context

@method_decorator(login_required, name='dispatch')
class Stats(TemplateView):
    template_name = 'tournament/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['tournament_name'] = self.kwargs['tournament_name']
        context['stats'] = get_stats_classification()
        return context

@method_decorator(login_required, name='dispatch')
class MyResults(TemplateView):

    template_name = 'tournament/my_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        finished_bets = get_finished_bets(user=self.request.user)
        points_per_user = player_results(self.request.user)
        #points_per_user = get_points_per_user(finished_bets)
        context['finished_bets'] = finished_bets
        context['points_per_user'] = points_per_user
        return context

#TODO: ponizsza klase mozna by bylo zrobic z DetailView i zastosowac w modelu slug'a.
@method_decorator(login_required, name='dispatch')
class Tournament(TemplateView):

    template_name = 'tournament/tournament.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tournament_name'] = self.kwargs['tournament_name']
        context['general_classification_only'] = get_tournament(self.kwargs['tournament_name']).general_classification_only
        context['points_per_user'] = get_classification(tournament_name=self.kwargs['tournament_name'])
        return context


class VoteForm(LoginHandling, FormView):

    template_name = 'tournament/vote_form.html'
    form_class = Vote
    success_url = reverse_lazy('vote_done')

    def get_form(self):
        return self.form_class(self.request.POST or None, matches_to_bet=self.matches_to_bet, user=self.request.user)

    def form_valid(self, form):
        for match in self.matches_to_bet:
            expected_home_goals = form.cleaned_data["{}_{}".format(match.home_team.name, match.id)]
            expected_away_goals = form.cleaned_data["{}_{}".format(match.away_team.name, match.id)]
            if (expected_away_goals is not None) and (expected_home_goals is not None):
                add_bet(self.request.user, match, expected_home_goals, expected_away_goals)
        return super(VoteForm, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        self.matches_to_bet, _ = get_matches_to_bet(self.request.user)
        return super(VoteForm, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['matches_to_bet'] = self.matches_to_bet
        return context

#TODO: Czy VoteChangeForm nie jest taki sam jak VoteForm tylko wypelniony initial data?? Mamy metody initial w generic..
class VoteChangeForm(LoginHandling, FormView):

    template_name = 'tournament/vote_change_form.html'
    form_class = Vote
    success_url = reverse_lazy('vote_change_done')

    #TODO: czy nie lepiej uzyc get_form_kwargs()
    def get_form(self):
        return self.form_class(self.request.POST or None, ongoing_bets=self.ongoing_bets, user=self.request.user)

    def form_valid(self, form):
        for bet in self.ongoing_bets:
            expected_home_goals = form.cleaned_data["{}_{}".format(bet.match.home_team.name, bet.match.id)]
            expected_away_goals = form.cleaned_data["{}_{}".format(bet.match.away_team.name, bet.match.id)]
            update_goals_bet(bet.id, expected_home_goals, expected_away_goals)
        return super(VoteChangeForm, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        self.ongoing_bets = get_ongoing_bets(user=self.request.user, change_bet = True)
        return super(VoteChangeForm, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ongoing_bets'] = self.ongoing_bets
        return context


#TODO: w ponizszej klasie tym return render obchodzimy troche success_url - moze trzeba to poprawic??
@method_decorator(login_required, name='dispatch')
class OtherResultForm(FormView):

    template_name = 'tournament/other_results.html'
    form_class = ChooseUser

    def form_valid(self, form):
        user_name = form.cleaned_data["choose_user_field"]
        tournament_name = form.cleaned_data["choose_tournament"]
        round_name = form.cleaned_data["choose_round"]
        user = get_user(user_name=user_name)
        self.finished_bets = get_finished_bets(user=user, tournament_name=tournament_name, active_tournaments=True,
                                          round=round_name)
        self.ongoing_bets = get_ongoing_bets(user=user, tournament_name=tournament_name, round=round_name)

        context = self.get_context_data()
        context['finished_bets'] = self.finished_bets
        context['ongoing_bets'] = self.ongoing_bets

        return render(self.request, 'tournament/other_results.html', context)

    # ustawiam finished_bets i ongoing_bets tylko dlatego zeby rozróznić w html'u warosc None
    # Funkcje get_finished_bets i  get_ongoing_bets jak sa wywolywane i nic nie znajda zwracja pusty slownik
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['finished_bets'] = None
        context['ongoing_bets'] = None
        return context

@method_decorator(login_required, name='dispatch')
class SeeOngoingMatchBets(FormView):
    """
    W Menu Podglad -> Mecze nierozegrane
    """

    form_class = ChooseMatch
    template_name = 'tournament/ongoing_match_bets.html'

    def get_form(self):
        return self.form_class(self.request.POST or None, ongoing_matches = True)

    def form_valid(self, form):
        match_id = form.cleaned_data["choose_match_field"]
        match = get_match(match_id)
        bets = bet_list(match=match)

        context = self.get_context_data()
        context['match'] = match
        context['bets'] = bets

        return render(self.request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bets'] = None
        return context

@method_decorator(login_required, name='dispatch')
class SeeFinishedMatchBets(FormView):
    """
    W Menu Podglad -> Mecze zakonczone
    """

    form_class = ChooseMatch
    template_name = 'tournament/finished_match_bets.html'

    def get_form(self):
        return self.form_class(self.request.POST or None, ongoing_matches = False)

    def form_valid(self, form):
        match_id = form.cleaned_data["choose_match_field"]
        match = get_match(match_id)
        bets = bet_list(match=match)

        results = []

        for bet in bets:
            results.append((str(bet.user), bet.expected_home_goals, bet.expected_away_goals, bet.score))

        context = self.get_context_data()
        context['match'] = match
        context['results'] = results

        return render(self.request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = None
        return context


class TooLateToBet(LoginHandling,TemplateView):

    template_name = 'tournament/too_late_to_bet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _, too_late = get_matches_to_bet(self.request.user)
        context['too_late'] = too_late
        return context

#TODO: zamienic dwie ponizsze klasy na jedna i jakos to spojnie zrobic... np. tak zeby z SETTINGS zaczytwal mozliwe jezyki itp. itd.
class LanguageChange_Pl(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        language_code = 'pl'
        translation.activate(language_code)
        self.request.session[translation.LANGUAGE_SESSION_KEY] = language_code
        if (str(self.request.user) == 'AnonymousUser'):
            return HttpResponseRedirect(reverse('login'))
            # return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect(reverse('index'))

        #return super(LanguageChange_Pl, self).dispatch(request, *args, **kwargs)

class LanguageChange_En(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        language_code = 'en'
        translation.activate(language_code)
        self.request.session[translation.LANGUAGE_SESSION_KEY] = language_code
        if (str(self.request.user) == 'AnonymousUser'):
            return HttpResponseRedirect(reverse('login'))
        else:
            return HttpResponseRedirect(reverse('index'))


@method_decorator(login_required, name='dispatch')
class SimulationChooseMatchForm(FormView):

    template_name = 'tournament/simulation_choose_match.html'
    form_class = ChooseMatch


    def get_form(self):
        return self.form_class(self.request.POST or None, ongoing_matches=True)

    def form_valid(self, form):
        match_id = form.cleaned_data["choose_match_field"]
        match = get_match(match_id)
        self.request.session['match_id'] = match_id
        self.request.session['home_team'] = match.home_team.name
        self.request.session['away_team'] = match.away_team.name
        return HttpResponseRedirect(reverse('simulation_choose_result'))


@method_decorator(login_required, name='dispatch')
class SimulationChooseResultForm(FormView):

    template_name = 'tournament/simulation_choose_result.html'
    form_class = ChooseMatchResult


    def form_valid(self, form):
        match_id = self.request.session['match_id']
        match = get_match(match_id)
        match.home_goals = form.cleaned_data["ht_goals"]
        match.away_goals = form.cleaned_data["at_goals"]

        points_per_user = simulate_classification(match)

        #to jest stary kod przelicza cala baze i klasyfikacje od zera - ciagle dziala. Zastapiony przez funkcje simulate_classification
        #finished_bets = get_finished_bets(tournament_name=match.tournament.name, simulated_match=match)
        #points_per_user = get_points_per_user(finished_bets)

        context = self.get_context_data()
        context['tournament_name'] = match.tournament.name
        context['points_per_user'] = points_per_user

        return render(self.request, self.template_name, context)

    #ustawiam points_per_user tylko dlatego zeby rozróznić w html'u (simulated_choose_result.html)
    #warosc None zwracaną przez simulate_classification() a pustym sownikiem generowanym na poczatku strony
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['points_per_user'] = {}
        return context


class PasswordChange(LoginHandling, FormView):
    """
    """
    template_name = 'registration/change_password_form.html'
    form_class = PasswordChangeForm

    def get_form(self):
        return self.form_class(self.request.user, self.request.POST or None)

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        return HttpResponseRedirect(reverse('change_password_done'))


class EmailChange(LoginHandling, FormView):
    """
    """
    template_name = 'registration/email_change.html'
    form_class = EmailChangeForm

    def get_form(self):
        return self.form_class(self.request.user, self.request.POST or None)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse('change_email_done'))

class NotificationChange(LoginHandling, FormView):
    """
    """
    template_name = 'registration/notification_change.html'
    form_class = NotificationChangeForm

    def get_form(self):
        return self.form_class(self.request.user, self.request.POST or None)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse('change_notification_done'))


