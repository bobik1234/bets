"""
Zadaniem tego modulu jest ustawienie punktow (scores) dla danego zakladu (bet)
"""
from tournament.db_handler import bet_list, update_score_bet, match_list


def setup_score_for_bets(match):
    """
    Jezeli zmienilismy cos w ustawiniu meczu z pozimu administratora to ta funkcja sie wywola

    :param match:
    :return:
    """
    bets = bet_list(match=match)

    for bet in bets:
        score = calculate_score(bet, match)
        update_score_bet(bet.id, score)

def calculate_score(bet, match):
    """
    Sprawdza ile punktow zwrocic za zaklad (bet) i zwraca ta ilosc
    """

    if (match.home_goals is None) or (match.away_goals is None):
        return 0

    if (match.home_goals == bet.expected_home_goals) and (match.away_goals == bet.expected_away_goals):
        return 3
    elif _who_won(match.home_goals, match.away_goals) == _who_won(bet.expected_home_goals, bet.expected_away_goals):
        return 1
    else:
        return 0

def _who_won(home_goals, away_goals):
    """
    funkcja pomocnicza do powyzszej funkcji _calculate_score()
    """
    if home_goals > away_goals:
        return "home team won"
    elif home_goals == away_goals:
        return "duce"
    else:
        return "away team won"

