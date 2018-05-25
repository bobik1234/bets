from tournament.models import Bet, Match
import operator

def get_points_per_user(finished_bets):
    """

    :param finished_bets:  - lista slownikow {bet:..., score=...} - patrz ponizsza funkcja get_finished_bets
    :return: Lista slownikow i to zagniezdzonych

        Zmienna scores ma strukture:
            {tournament : {'round' : {user : score,
                                      user : score)}...
                           'summary' : {user : score},
                                       {user : score}}

        Po sortowaniu i finalnie mamy:
                {tournament : {'round' : [(user, score), (user, score)... ]...
                               'summary' : [(user, score), (user, score)... ]}



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
    #return scores

    #sortujemy slowniki

    sorted_rounds_results = {}
    for tournament_name, round_scores in scores.items():
        for round_name, results in round_scores.items():
            if not (tournament_name in sorted_rounds_results.keys()):
                sorted_rounds_results[tournament_name] = {}
            sorted_rounds_results[tournament_name][round_name] = sorted(results.items(), key=operator.itemgetter(1),
                                                                        reverse=True)

    sorted_rounds_results_with_place = _set_place(sorted_rounds_results)

    return sorted_rounds_results_with_place


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


def _set_place(sorted_rounds_results):
    """
    Ustawia miejsce na posortowanych slownikach - ktore miejsce ma uzytkownik w danej rundzie


    {tournament : {'round' : [(user, score), (user, score)... ]...
                               'summary' : [(user, score), (user, score)... ]}

    :param sorted_rounds_results:
    :return:
    """

    sorted_rounds_results_with_place = {}


    for tournament_name, tournament_data in sorted_rounds_results.items():

        rounds_dict = {}

        for round_name, round_data in tournament_data.items():

            list = []
            previous_score = None

            for i, user_and_score in enumerate(round_data, start=1):
                user, score = user_and_score

                if score == previous_score:
                    list.append(("-", user, score))
                else:
                    list.append((i, user, score))

                previous_score = score

            rounds_dict.update({round_name : list})

        sorted_rounds_results_with_place.update({tournament_name : rounds_dict })

    return sorted_rounds_results_with_place





