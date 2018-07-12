from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from tournament.utils import get_finished_bets, get_points_per_user, get_ongoing_bets, vote_context, get_matches_to_bet, calculate_score
from tournament.forms import Vote, ChooseUser, ChooseMatch, ChooseMatchResult
from tournament.db_handler import get_user, bet_list, get_match, add_bet, update_bet
from django.views.generic import TemplateView, FormView
from django.utils.decorators import method_decorator

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


#TODO: dopisac ladna strone do zmiany hasla... po zmianie nie wraca do aplikacji, trzeba recznie wrocic...


@method_decorator(login_required, name='dispatch')
class Index(TemplateView):
    template_name = 'tournament/index.html'

@method_decorator(login_required, name='dispatch')
class Info(TemplateView):
    template_name = 'tournament/info.html'

@method_decorator(login_required, name='dispatch')
class VoteDone(TemplateView):
    template_name = 'tournament/vote_done.html'

@method_decorator(login_required, name='dispatch')
class VoteChangeDone(TemplateView):
    template_name = 'tournament/vote_change_done.html'


@method_decorator(login_required, name='dispatch')
class MyResults(TemplateView):

    template_name = 'tournament/my_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        finished_bets = get_finished_bets(user=self.request.user)
        points_per_user = get_points_per_user(finished_bets)
        context['finished_bets'] = finished_bets
        context['points_per_user'] = points_per_user
        return context

#TODO: ponizsza klase mozna by bylo zrobic z DetailView i zastosowac w modelu slug'a
@method_decorator(login_required, name='dispatch')
class Tournament(TemplateView):

    template_name = 'tournament/tournament.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        finished_bets = get_finished_bets(tournament_name=self.kwargs['tournament_name'])
        points_per_user = get_points_per_user(finished_bets)
        context['tournament_name'] = self.kwargs['tournament_name']
        context['points_per_user'] = points_per_user
        return context



#TODO: to juz chyba nie uzywane, usunac...
@login_required(login_url='/accounts/login/')
def vote_overview(request):

    user = request.user
    context = vote_context(user)

    return render(request, 'tournament/vote_overview.html', context)

#TODO: Czy da sie przerobic FormView na CreateView i obstawiac pojedynczo??
class VoteForm(FormView):

    template_name = 'tournament/vote_form.html'
    form_class = Vote
    success_url = '/tournament/vote_done'

    def get_form(self):
        return self.form_class(self.request.POST or None, matches_to_bet=self.matches_to_bet, user=self.request.user)

    def form_valid(self, form):
        for match in self.matches_to_bet:
            expected_home_goals = form.cleaned_data["{}_{}".format(match.home_team.name, match.id)]
            expected_away_goals = form.cleaned_data["{}_{}".format(match.away_team.name, match.id)]
            add_bet(self.request.user, match, expected_home_goals, expected_away_goals)
        return super(VoteForm, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.matches_to_bet, _ = get_matches_to_bet(self.request.user)
        return super(VoteForm, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['matches_to_bet'] = self.matches_to_bet
        return context

#TODO: Czy VoteChangeForm nie jest taki sam jak VoteForm tylko wypelniony initial data?? Mamy metody initial w generic..
class VoteChangeForm(FormView):

    template_name = 'tournament/vote_change_form.html'
    form_class = Vote
    success_url = '/tournament/vote_change_done'

    def get_form(self):
        return self.form_class(self.request.POST or None, ongoing_bets=self.ongoing_bets, user=self.request.user)

    def form_valid(self, form):
        for bet in self.ongoing_bets:
            expected_home_goals = form.cleaned_data["{}_{}".format(bet.match.home_team.name, bet.match.id)]
            expected_away_goals = form.cleaned_data["{}_{}".format(bet.match.away_team.name, bet.match.id)]
            update_bet(bet.id, expected_home_goals, expected_away_goals)
        return super(VoteChangeForm, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.ongoing_bets = get_ongoing_bets(user=self.request.user)
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

@method_decorator(login_required, name='dispatch')
class SeeOngoingMatchBets(FormView):

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
            score = calculate_score(bet, match)
            results.append((str(bet.user), bet.expected_home_goals, bet.expected_away_goals, score))

        context = self.get_context_data()
        context['match'] = match
        context['results'] = results

        return render(self.request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = None
        return context


@method_decorator(login_required, name='dispatch')
class TooLateToBet(TemplateView):

    template_name = 'tournament/too_late_to_bet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _, too_late = get_matches_to_bet(self.request.user)
        context['too_late'] = too_late
        return context

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

        finished_bets = get_finished_bets(tournament_name=match.tournament.name, simulated_match=match)
        points_per_user = get_points_per_user(finished_bets)

        context = self.get_context_data()
        context['tournament_name'] = match.tournament.name
        context['points_per_user'] = points_per_user
        context['finished_bets'] = finished_bets

        return render(self.request, self.template_name, context)


#TODO: Mozna by lepiej rozkminic autentykacje i obyc sie bez ponizszych view do zmiany hasla. IMPROVEMENT

@login_required(login_url='/accounts/login/')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            #messages.success(request, 'Your password was successfully updated!')
            return render(request, 'registration/change_password_done.html')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password_form.html', {
        'form': form
    })


@login_required(login_url='/accounts/login/')
def change_password_done(request):
    return render(request, 'registration/change_password_done.html')

