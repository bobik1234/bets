from django.utils import timezone
from tournament.models import Bet, Match

"""
Doprecyzujmy co znaczy:
'ongoing_bets'     --> mecze ktore sie juz obstawilismy ale mozna jeszcze zmienic ich wynik
'matches_to_bet'   --> mecze nie obstawione ale ktore mozna obstawiac (nawet na minute przed meczem)
'too_late_to_bet'  --> mecze nie obstawione, ktore juz sie rozpoczely albo zakonczyly
'finished_bets'    --> mecze ktore obstawialismy i nie mozna zmienic ich wyniku - tocza sie albo juz sie zakonczyly
"""

def vote_context(user):

    now = timezone.now()
    user_bets = []
    for bet in list(Bet.objects.filter(user=user)):
        user_bets.append(bet)

    matches_to_bet = []
    id_matches_to_bet = []
    id_ongoing_bets = []
    too_late_to_bet = []
    matches_already_bet = [m.match for m in user_bets]
    #ongoing_bets = [bet for bet in user_bets if bet.match.home_goals == None]
    ongoing_bets = [bet for bet in user_bets if now < bet.match.match_date]
    for bet in ongoing_bets:
        id_ongoing_bets.append(bet.id)


    #finished_bets = [bet for bet in user_bets if bet.match.home_goals is not None]
    finished_bets = [bet for bet in user_bets if (bet.expected_away_goals is not None) and (now > bet.match.match_date)]
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

    return context, id_matches_to_bet, id_ongoing_bets


# do przemyslenia - powyzsza funkcje rozdzielic na trzy zeby zwracaly trzy rozne parametry
