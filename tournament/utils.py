from django.utils import timezone
from tournament.db_handler import bet_list, match_list
import operator


def vote_context(user):
    """
    Doprecyzujmy co znaczy:
    'ongoing_bets'     --> mecze ktore sie juz obstawilismy ale mozna jeszcze zmienic ich wynik
    'matches_to_bet'   --> mecze nie obstawione ale ktore mozna obstawiac
    'too_late_to_bet'  --> mecze nie obstawione, ktore juz sie rozpoczely albo zakonczyly
    'finished_bets'    --> mecze ktore obstawialismy i nie mozna zmienic ich wyniku - tocza sie albo juz sie zakonczyly

    :param user:
    :return:
    """

    matches_to_bet, too_late_to_bet = get_matches_to_bet(user)

    context = {'ongoing_bets': get_ongoing_bets(user=user),
               'matches_to_bet': matches_to_bet,
               'too_late_to_bet': too_late_to_bet,
               'finished_bets': get_finished_bets(user)}

    return context

def get_points_per_user(finished_bets):
    """

    :param finished_bets:  - lista slownikow {bet:..., score=...} - patrz ponizsza funkcja get_finished_bets
    :return: Lista slownikow i to zagniezdzonych

        Zmienna scores ma strukture:
            {tournament : {'round' : {user : score,
                                      user : score)}...
                           'General Classification' : {user : score},
                                                       {user : score}}

        Po sortowaniu i finalnie mamy:
                {tournament : {'round' : [(user, score), (user, score)... ]...
                               'General_Classification' : [(user, score), (user, score)... ]}



    """

    scores = {}

    for finished_bet in finished_bets:
        tournament_name = finished_bet['bet'].match.tournament.name
        if not (tournament_name in scores.keys()):
            scores[tournament_name] = {'General Classification' : {}}
        round = finished_bet['bet'].match.round
        if not (round in scores[tournament_name].keys()):
            scores[tournament_name][round] = {}

        user = finished_bet['bet'].user.__str__()
        if user in scores[tournament_name][round].keys():
            scores[tournament_name][round][user] += finished_bet['score']
        else:
            scores[tournament_name][round][user] = finished_bet['score']

        if user in scores[tournament_name]['General Classification'].keys():
            scores[tournament_name]['General Classification'][user] += finished_bet['score']
        else:
            scores[tournament_name]['General Classification'][user] = finished_bet['score']


    #sortujemy slowniki

    sorted_rounds_results = {}
    for tournament_name, round_scores in scores.items():
        for round_name, results in round_scores.items():
            if not (tournament_name in sorted_rounds_results.keys()):
                sorted_rounds_results[tournament_name] = {}
            sorted_rounds_results[tournament_name][round_name] = sorted(results.items(), key=operator.itemgetter(1),
                                                                        reverse=True)
    #TODO: _set_place nie dziala dla my_results --> jak mamy tylko jednego usera z finished bets to miejsce zawsze bedzie pierwsze, mozna to usprawnic
    sorted_rounds_results_with_place = _set_place(sorted_rounds_results)

    return sorted_rounds_results_with_place

def get_bets_for_match(match):
    """
    Zwraca wszystkie obstawienia dla konkretnego meczu
    :param match:
    :return:
    """


def get_matches_to_bet(user):
    """
    Zwraca mecze do obstawienia przez usera oraz informuje ktore sa juz za pozno do obstawienia

    :param user:
    :return:
    """
    user_bets = []
    Time_To_Bet = timezone.localtime(timezone.now()) + timezone.timedelta(hours=1)

    for bet in bet_list(user):
        user_bets.append(bet)

    matches_to_bet = []
    too_late_to_bet = []
    matches_already_bet = [m.match for m in user_bets]

    for match in match_list():
        if match not in matches_already_bet:
            if Time_To_Bet > match.match_date:
                too_late_to_bet.append(match)
            else:
                matches_to_bet.append(match)


    return matches_to_bet, too_late_to_bet


def get_finished_bets(user = None, tournament_name = None, active_tournaments = True, round = 'All', simulated_match = None):
    """
    Wyniki z zakonczonych meczy, mozna po uzytkowniku i po statusie turnieju, zwraca liste slownikow
    {bet:..., score=...}

    Ustawienie tournament_name ignoruje ustawienie  active_tournaments

    simulated_match - dla symulowania wyniku meczu
    """

    finished_bets = []
    user_bet_list = bet_list(user)
    Time_To_Bet = timezone.localtime(timezone.now()) + timezone.timedelta(hours=1)

    for bet in user_bet_list:

        if tournament_name is not None:
            if not (tournament_name == bet.match.tournament.name):
                continue

        if (bet.match.tournament.active is not active_tournaments):
            continue

        if not (round == 'All'):
            if not (round == bet.match.round):
                continue

        if (simulated_match is not None) and (bet.match == simulated_match):
            finished_bets.append({'bet': bet, 'score': calculate_score(bet, simulated_match)})
            continue

        if (Time_To_Bet > bet.match.match_date): #TODO: chyba time_to_bed nie jest potrzebne, mozna by bylo zrobic ze wynik meczu nie jest None, spr..
            finished_bets.append({'bet': bet, 'score': calculate_score(bet, bet.match)})

    return finished_bets


def get_ongoing_bets(user=None, tournament_name=None, round='All'):
    """
    Obstawione wyniki meczy, ktore jeszcze sie nie zakonczyly. Zwraca liste zakladow:
    [bet1,bet2,...]

    """

    ongoing_bets = []
    user_bet_list = bet_list(user)
    Time_To_Bet = timezone.localtime(timezone.now()) + timezone.timedelta(hours=1)

    for bet in user_bet_list:

        if tournament_name is not None:
            if not (tournament_name == bet.match.tournament.name):
                continue
            if (not bet.match.tournament.active):
                continue

        if not (round == 'All'):
            if not (round == bet.match.round):
                continue

        if (bet.match.home_goals is not None) or (bet.match.away_goals is not None):
            continue

        if (Time_To_Bet < bet.match.match_date):
            ongoing_bets.append(bet)

    return ongoing_bets

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
            previous_place = None

            for i, user_and_score in enumerate(round_data, start=1):
                user, score = user_and_score

                if score == previous_score:
                    #list.append(("-", user, score))
                    list.append((previous_place, user, score))
                else:
                    list.append((i, user, score))

                previous_score = score
                previous_place = i

            rounds_dict.update({round_name : list})

        sorted_rounds_results_with_place.update({tournament_name : rounds_dict })

    return sorted_rounds_results_with_place

