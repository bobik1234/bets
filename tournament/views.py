from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tournament.summary import get_finished_bets, get_points_per_user
from django.template import RequestContext
from tournament.forms import Vote
from tournament.vote_utils import vote_context
from tournament.models import Bet, Match

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
    context, id_matches_to_bet = vote_context(user)
    request.session['id_matches_to_bet'] = id_matches_to_bet

    return render(request, 'tournament/vote_overview.html', context)


@login_required(login_url='/accounts/login/')
def vote_form(request):

    matches_to_bet = []
    for id in request.session['id_matches_to_bet']:
        matches_to_bet.append(Match.objects.get(pk=id))

    form = Vote(request.POST or None, matches_to_bet=matches_to_bet)
    if form.is_valid():
        for match in matches_to_bet:
            print(form.cleaned_data["{}_{}".format(match.home_team.name,match.id)])
            m = Bet(user=request.user,
                    match = match,
                    expected_home_goals = form.cleaned_data["{}_{}".format(match.home_team.name, match.id)],
                    expected_away_goals = form.cleaned_data["{}_{}".format(match.away_team.name, match.id)])
            m.save()

        user = request.user
        context, _ = vote_context(user)
        return render(request, 'tournament/vote_overview.html', context)
    context = {'matches_to_bet' : matches_to_bet,
               'form': form}
    return render(request, 'tournament/vote_form.html', context,  RequestContext(request))

