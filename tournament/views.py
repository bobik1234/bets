from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tournament.utils import get_finished_bets, get_points_per_user, get_ongoing_bets, vote_context
from django.template import RequestContext
from tournament.forms import Vote, ChooseUser
from tournament.models import Bet, Match
from tournament.db_handler import get_user

#TODO: dopisac ladna strone do zmiany hasla... po zmianie nie wraca do aplikacji...

@login_required(login_url='/accounts/login/')
def index(request):
    return render(request, 'tournament/index.html')

@login_required(login_url='/accounts/login/')
def info(request):
    return render(request, 'tournament/info.html')

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


@login_required(login_url='/accounts/login/')
def vote_overview(request):

    user = request.user
    #context, id_matches_to_bet, id_ongoing_bets = vote_context(user) #jest tak bo jest to JSON parsing problem trzy linijki nizej  request.session
    #request.session['id_matches_to_bet'] = id_matches_to_bet
    #request.session['id_ongoing_bets'] = id_ongoing_bets
    context, _, _ = vote_context(user)  # jest tak bo jest to JSON parsing problem trzy linijki nizej  request.session

    return render(request, 'tournament/vote_overview.html', context)


@login_required(login_url='/accounts/login/')
def vote_form(request):

    matches_to_bet = []

    user = request.user
    _, id_matches_to_bet, _ = vote_context(user)

    for id in id_matches_to_bet:
        matches_to_bet.append(Match.objects.get(pk=id))


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

        user = request.user
        context, _, _ = vote_context(user)
        return render(request, 'tournament/vote_overview.html', context)
    context = {'matches_to_bet' : matches_to_bet,
               'form': form}
    return render(request, 'tournament/vote_form.html', context,  RequestContext(request))

@login_required(login_url='/accounts/login/')
def vote_change_form(request):

    ongoing_bets = []

    user = request.user
    _, _, id_ongoing_bets = vote_context(user)  # pewnie nieoptymalne ale powyzsze trzeba bylo usunac bo nie odswiezal strony

    for bet_id in id_ongoing_bets:
        ongoing_bets.append(Bet.objects.get(pk=bet_id))

    form = Vote(request.POST or None, ongoing_bets=ongoing_bets, user=user)
    if form.is_valid():
        for bet in ongoing_bets:
            print(form.cleaned_data["{}_{}".format(bet.match.home_team.name,bet.match.id)]) #TODO: usunac - albo dac w trybie debug,
            # TODO: przerzucic handlowanie bazy db_handlera
            Bet.objects.filter(id=bet.id).update(
                expected_home_goals = form.cleaned_data["{}_{}".format(bet.match.home_team.name, bet.match.id)],
                expected_away_goals = form.cleaned_data["{}_{}".format(bet.match.away_team.name, bet.match.id)])

        user = request.user
        context, _, _ = vote_context(user)
        return render(request, 'tournament/vote_overview.html', context)
    context = {'ongoing_bets' : ongoing_bets,
               'form': form}
    return render(request, 'tournament/vote_change_form.html', context,  RequestContext(request))


@login_required(login_url='/accounts/login/')
def other_results(request):

    #TODO: get_finished_bets - tu by trzeba bylo dodac runde, z defaltu na All i dodac funckje get_ongoing_bets
    #TODO: other_result.html ma duzo wspolnego z my_results.html - moze jakos ujednolicic...
    #TODO: pomyslec jak zmergowac utils.py i view_utils w jedno

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