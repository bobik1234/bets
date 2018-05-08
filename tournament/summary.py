from tournament.models import Bet, Match

def get_points_per_user(finished_bets):
    """

    :param finished_bets:  - lista slownikow {bet:..., score=...} - patrz ponizsza funkcja get_finished_bets
    :return: Lista slownikow i to zagniezdzonych
            {tournament : {'round' : {user : score,
                                      user : score)}...
                           'summary' : {user : score},
                                       {user : score}}
    """

    scores = {}

    for finished_bet in finished_bets:
        tournament_name = finished_bet['bet'].match.tournament.name
        if not (tournament_name in scores.keys()):
            scores[tournament_name] = {'summary' : {}}
        round = finished_bet['bet'].match.round
        if not (round in scores[tournament_name].keys()):
            scores[tournament_name][round] = {}

        user = finished_bet['bet'].user.__str__()
        if user in scores[tournament_name][round].keys():
            scores[tournament_name][round][user] += finished_bet['score']
        else:
            scores[tournament_name][round][user] = finished_bet['score']

        if user in scores[tournament_name]['summary'].keys():
            scores[tournament_name]['summary'][user] += finished_bet['score']
        else:
            scores[tournament_name]['summary'][user] = finished_bet['score']

    return scores

    #sortujemy slowniki

    sorted_rounds_results = {}
    for tournament in scores.items():
        for round, results in tournament.items():
            sorted_rounds_results[round] = sorted(results.items(), key=operator.itemgetter(1)) #, reverse=True)

    return sorted_rounds_results


def get_finished_bets(user = None, tournament_name = None, active_tournaments = True):
    """
    Wyniki z zakonczonych meczy, mozna po uzytkowniku i po statusie turnieju, zwraca liste slownikow
    {bet:..., score=...}

    Ustawienie tournament_name ignoruje ustawienie  active_tournaments
    """

    overview_results = []
    bets_list = list(Bet.objects.all())

    for match in list(Match.objects.all()):
        if (match.home_goals is None) or (match.away_goals is None):
            continue

        if tournament_name is not None:
            if not (tournament_name == match.tournament.name):
                continue
        elif (match.tournament.active is not active_tournaments):
             continue

        for bet in bets_list: #trzeba by to bylo czytelniej zaifowac
            if match == bet.match:
                if user and (user == bet.user):
                    overview_results.append({'bet': bet, 'score': _calculate_score(bet, match)})
                elif user is None:
                    overview_results.append({'bet': bet, 'score': _calculate_score(bet, match)})
                else:
                    continue
    return overview_results


def _calculate_score(bet, match):
    """
    Sprawdza ile punktow zwrocic za zaklad (bet) i zwraca ta ilosc
    """
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


