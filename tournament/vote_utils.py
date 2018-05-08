from django.utils import timezone
from tournament.models import Bet, Match

def vote_context(user):

    user_bets = []
    for bet in list(Bet.objects.filter(user=user)):
        user_bets.append(bet)

    matches_to_bet = []
    id_matches_to_bet = []
    too_late_to_bet = []
    matches_already_bet = [m.match for m in user_bets]
    ongoing_bets = [bet for bet in user_bets if bet.match.home_goals == None]
    finished_bets = [bet for bet in user_bets if bet.match.home_goals is not None]
    now = timezone.now()
    for match in list(Match.objects.all()):
        if match not in matches_already_bet:
            if now > match.match_date:
                too_late_to_bet.append(match)
            else:
                matches_to_bet.append(match)
                id_matches_to_bet.append(match.id)

    context = {'ongoing_bets' : ongoing_bets,
               'matches_to_bet' : matches_to_bet,
               'too_late_to_bet' : too_late_to_bet,
               'finished_bets' : finished_bets}

    return context, id_matches_to_bet