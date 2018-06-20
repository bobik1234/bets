from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tournament.utils import get_finished_bets, get_points_per_user, get_ongoing_bets, vote_context, get_matches_to_bet
from django.template import RequestContext
from tournament.forms import Vote, ChooseUser, ChooseMatch, ChooseMatchResult
from tournament.models import Bet, Match
from tournament.db_handler import get_user, bet_list, get_match


from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect


#TODO: dopisac ladna strone do zmiany hasla... po zmianie nie wraca do aplikacji, trzeba recznie wrocic...

@login_required(login_url='/accounts/login/')
def index(request):
    return render(request, 'tournament/index.html')

@login_required(login_url='/accounts/login/')
def info(request):
    return render(request, 'tournament/info.html')

@login_required(login_url='/accounts/login/')
def simulation(request):
    return render(request, 'tournament/simulation.html')

@login_required(login_url='/accounts/login/')
def my_results(request):
    finished_bets = get_finished_bets(user=request.user)
    points_per_user = get_points_per_user(finished_bets)
    context = {'finished_bets': finished_bets,
               'points_per_user': points_per_user}
    return render(request, 'tournament/my_results.html', context)

@login_required(login_url='/accounts/login/')
def tournament(request, tournament_name):
    finished_bets = get_finished_bets(tournament_name=tournament_name)
    points_per_user = get_points_per_user(finished_bets)

    context = {'tournament_name' : tournament_name,
               'points_per_user': points_per_user,
               'finished_bets' : finished_bets}

    return render(request, 'tournament/tournament.html', context)


#TODO: to juz chyba nie uzywane, usunac...
@login_required(login_url='/accounts/login/')
def vote_overview(request):

    user = request.user
    context = vote_context(user)

    return render(request, 'tournament/vote_overview.html', context)


@login_required(login_url='/accounts/login/')
def vote_form(request):

    user = request.user
    matches_to_bet, _ = get_matches_to_bet(user)

    form = Vote(request.POST or None, matches_to_bet=matches_to_bet, user=user)
    if form.is_valid():
        for match in matches_to_bet:
            print(form.cleaned_data["{}_{}".format(match.home_team.name,match.id)])
            #TODO: przerzucic handlowanie bazy db_handlera
            m = Bet(user=request.user,
                    match = match,
                    expected_home_goals = form.cleaned_data["{}_{}".format(match.home_team.name, match.id)],
                    expected_away_goals = form.cleaned_data["{}_{}".format(match.away_team.name, match.id)])
            m.save()

        return render(request, 'tournament/vote_done.html')
    context = {'matches_to_bet' : matches_to_bet,
               'form': form}
    return render(request, 'tournament/vote_form.html', context,  RequestContext(request))

@login_required(login_url='/accounts/login/')
def vote_change_form(request):

    user = request.user
    ongoing_bets = get_ongoing_bets(user=user)

    form = Vote(request.POST or None, ongoing_bets=ongoing_bets, user=user)
    if form.is_valid():
        for bet in ongoing_bets:
            print(form.cleaned_data["{}_{}".format(bet.match.home_team.name,bet.match.id)]) #TODO: usunac - albo dac w trybie debug,
            # TODO: przerzucic handlowanie bazy db_handlera
            Bet.objects.filter(id=bet.id).update(
                expected_home_goals = form.cleaned_data["{}_{}".format(bet.match.home_team.name, bet.match.id)],
                expected_away_goals = form.cleaned_data["{}_{}".format(bet.match.away_team.name, bet.match.id)])

        return render(request, 'tournament/vote_change_done.html')
    context = {'ongoing_bets' : ongoing_bets,
               'form': form}
    return render(request, 'tournament/vote_change_form.html', context,  RequestContext(request))


@login_required(login_url='/accounts/login/')
def other_results(request):

    #TODO: get_finished_bets - tu by trzeba bylo dodac runde, z defaltu na All i dodac funckje get_ongoing_bets
    #TODO: other_result.html ma duzo wspolnego z my_results.html - moze jakos ujednolicic...

    form = ChooseUser(request.POST or None)

    context = {'form': form}

    if form.is_valid():
        user_name = form.cleaned_data["choose_user_field"]
        tournament_name = form.cleaned_data["choose_tournament"]
        round_name = form.cleaned_data["choose_round"]
        user = get_user(user_name = user_name)

        finished_bets = get_finished_bets(user = user, tournament_name = tournament_name, active_tournaments = True, round = round_name)
        ongoing_bets = get_ongoing_bets(user = user, tournament_name = tournament_name, round = round_name)

        context = {'form'          : form,
                   'finished_bets' : finished_bets,
                   'ongoing_bets'  : ongoing_bets}

        return render(request, 'tournament/other_results.html', context)

    return render(request, 'tournament/other_results.html',context, RequestContext(request))


@login_required(login_url='/accounts/login/')
def match_bets(request):

    form = ChooseMatch(request.POST or None)
    context = {'form': form}

    if form.is_valid():
        match_id = form.cleaned_data["choose_match_field"]
        match = get_match(match_id)

        bets = bet_list(match = match)

        context = {'form': form,
                   'match': match,
                   'bets': bets}

        return render(request, 'tournament/match_bets.html', context)

    return render(request, 'tournament/match_bets.html', context)

@login_required(login_url='/accounts/login/')
def too_late_to_bet(request):

    user = request.user
    _, too_late = get_matches_to_bet(user)

    context = {'too_late': too_late}

    return render(request, 'tournament/too_late_to_bet.html', context)

@login_required(login_url='/accounts/login/')
def simulation(request):

    form = ChooseMatchResult(request.POST or None)
    context = {'form': form}

    if form.is_valid():

        match_id = form.cleaned_data["choose_match_field"]
        match = get_match(match_id)
        match.home_goals = form.cleaned_data["ht_goals"]
        match.away_goals = form.cleaned_data["at_goals"]

        finished_bets = get_finished_bets(tournament_name=match.tournament.name, simulated_match=match)

        points_per_user = get_points_per_user(finished_bets)

        context = {'form': form,
                   'tournament_name': match.tournament.name,
                   'points_per_user': points_per_user,
                   'finished_bets': finished_bets}

        return render(request, 'tournament/simulation.html', context)

    return render(request, 'tournament/simulation.html', context)




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

