from django.contrib.auth.models import User, Permission
from django.utils import timezone

from bets import settings
from tournament.db_handler import bet_list, match_list, get_tournament
import operator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import os, json
from tournament.models import Match, Tournament
from tournament.scores import setup_score_for_bets, calculate_score

classification_file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'classification_file.json')


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
                           'GeneralClassification' : {user : score},
                                                       {user : score}}

        Po sortowaniu:
                {tournament : {'round' : [(user, score), (user, score)... ]...
                               'GeneralClassification' : [(user, score), (user, score)... ]}


    Potem dodajemy jeszcze miejsce w klasyfikacji --> zobacz funkcje
    """
    scores = {}

    for finished_bet in finished_bets:
        tournament_name = finished_bet['bet'].match.tournament.name
        if not (tournament_name in scores.keys()):
            scores[tournament_name] = {'GeneralClassification': {}}
        round = finished_bet['bet'].match.round
        if not (round in scores[tournament_name].keys()):
            scores[tournament_name][round] = {}

        user = finished_bet['bet'].user.__str__()
        if user in scores[tournament_name][round].keys():
            scores[tournament_name][round][user] += finished_bet['score']
        else:
            scores[tournament_name][round][user] = finished_bet['score']

        if user in scores[tournament_name]['GeneralClassification'].keys():
            scores[tournament_name]['GeneralClassification'][user] += finished_bet['score']
        else:
            scores[tournament_name]['GeneralClassification'][user] = finished_bet['score']

    sorted_rounds_results = _sort_dict(scores)

    return sorted_rounds_results


def _sort_dict(dictionary):
    """
    sortujemy ponizszy slownik wedlug punktow (score)
    {tournament : {'round' : [(user, score), (user, score)... ]...
                               'GeneralClassification' : [(user, score), (user, score)... ]}
    """

    sorted_rounds_results = {}
    for tournament_name, round_scores in dictionary.items():
        for round_name, results in round_scores.items():
            if not (tournament_name in sorted_rounds_results.keys()):
                sorted_rounds_results[tournament_name] = {}
            sorted_rounds_results[tournament_name][round_name] = sorted(results.items(), key=operator.itemgetter(1),
                                                                        reverse=True)

    return sorted_rounds_results


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


def get_finished_bets(user=None, tournament_name=None, active_tournaments=True, round='All', simulated_match=None):
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
            finished_bets.append({'bet': bet, 'score': int(bet.score)})
            continue

        # if (Time_To_Bet > bet.match.match_date): #TODO: chyba time_to_bed nie jest potrzebne, mozna by bylo zrobic ze wynik meczu nie jest None, spr..
        #    finished_bets.append({'bet': bet, 'score': int(bet.score)})

        if (bet.match.away_goals is not None) and (bet.match.home_goals is not None):
            finished_bets.append({'bet': bet, 'score': int(bet.score)})

    return finished_bets


def get_ongoing_bets(user=None, tournament_name=None, round='All', change_bet=False):
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

        if change_bet:
            if (Time_To_Bet < bet.match.match_date):
                ongoing_bets.append(bet)
                continue
        else:
            if (bet.match.away_goals is None) or (bet.match.home_goals is None):
                ongoing_bets.append(bet)

    return ongoing_bets


def _set_place(sorted_rounds_results):
    """
    Ustawia miejsce na posortowanych slownikach - ktore miejsce ma uzytkownik w danej rundzie

    Wejscie:
    {tournament : {'round' : [(user, score), (user, score)... ]...
                               'summary' : [(user, score), (user, score)... ]}

    Wyjscie:
    {tournament : {'round' : [(place,user, score), (place,user, score)... ]...
                               'summary' : [(place,"-", user, score), (place, "-", user, score)... ]}

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
                    # list.append(("-", user, score))
                    list.append((previous_place, "-", user, score))
                else:
                    list.append((i, "-", user, score))
                    previous_place = i
                    previous_score = score

            rounds_dict.update({round_name: list})

        sorted_rounds_results_with_place.update({tournament_name: rounds_dict})

    return sorted_rounds_results_with_place


def _set_classification_changes(points_per_user_with_place):
    """
    Ustaw zmiane w klasyfikacji
    """

    classification = {}

    try:
        with open(classification_file_name) as data_file:
            old_classification = json.load(data_file)

            for tournament_name, tournament_classification  in points_per_user_with_place.items():
                if tournament_name in old_classification.keys():
                    for round_name, round_classification in tournament_classification.items():
                        if round_name in old_classification[tournament_name].keys():
                            users_in_old_classification = [x for _,_,x,_ in old_classification[tournament_name][round_name]]
                            for place, _, user, points in round_classification:
                               if user in users_in_old_classification:

                                    old_place = [place for place,_, old_user, _ in old_classification[tournament_name][round_name] if old_user == user][0]
                                    changes = int(old_place) - int(place)

                                    if changes > 0:
                                        change_field = "\\u25B2" + str(changes)
                                    elif changes < 0:
                                        change_field = "\\u25BC" + str(abs(changes))
                                    else:
                                        change_field = "-"

                                    if tournament_name in classification.keys():
                                        if round_name in classification[tournament_name].keys():
                                           classification[tournament_name][round_name].append([place,change_field, user, points])
                                        else:
                                           classification[tournament_name][round_name] = [[place,change_field, user, points]]
                                    else:
                                        classification[tournament_name]  = {}
                                        classification[tournament_name][round_name] = [[place,change_field, user, points]]

                               else:
                                   change_field = "-"
                                   if tournament_name in classification.keys():
                                       if round_name in classification[tournament_name].keys():
                                            classification[tournament_name][round_name].append([place,change_field, user, points])
                                       else:
                                           classification[tournament_name][round_name] = [[place,change_field, user, points]]
                                   else:
                                       classification[tournament_name] = {}
                                       classification[tournament_name][round_name] = [[place,change_field, user, points]]
                        else:
                           classification[tournament_name][round_name] = points_per_user_with_place[tournament_name][round_name]
                else:
                    classification[tournament_name] = points_per_user_with_place[tournament_name]

    except EnvironmentError:
        pass
        # nic sie nie ustawia wszyscy maja "-"

    return classification


@receiver(post_save, sender=Match)
# @receiver(post_delete, sender=Match)
@receiver(post_save, sender=Tournament)
# @receiver(post_delete, sender=Tournament) #TODO: Czy nie trzeba by dodac tego dla tabeli BET??
def calculate_classification(sender, instance, created, **kwargs):
    """
    Kazda zmiana w tabeli Match i Tournament generuje na nowo plik w formacie JSON w ktorym trzymamy klasyfikacje
    Tylko dla aktywnych turnieji
    """
    if isinstance(instance, Match):
        setup_score_for_bets(instance)

    finished_bets = get_finished_bets()
    points_per_user = get_points_per_user(finished_bets)

    points_per_user_with_place = _set_place(points_per_user)

    classification = _set_classification_changes(points_per_user_with_place)

    with open(classification_file_name, 'w') as fp:
        json.dump(classification, fp)


def get_classification(tournament_name=None):
    """
    """

    try:
        with open(classification_file_name) as data_file:
            classification = json.load(data_file)
    except EnvironmentError:
        return {}

    # TODO: przerobic - bez sensu zeby wpisywac tournament_name
    if tournament_name is not None:
        if tournament_name in classification.keys():
            return {tournament_name: classification[tournament_name]}
        else:
            return {}  # turniej zakonczony albo nie istnieje
    else:
        return classification


def get_historical_classification(tournament_name):
    """

    :param tournament_name:
    :return:
    """

    dir_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'history')
    file_name = os.path.join(dir_name, tournament_name + ".json")
    print(file_name)
    try:
        with open(file_name) as data_file:
            return json.load(data_file)
            # return classification
    except EnvironmentError:
        return {}


def simulate_classification(match):
    """
    Updejtuj klasyfikacje o mecz

    Algorytm:
        1. konwertujemy slowniki - zobacz funkcje _convert_dict
        2. sprawdzamy kto obastawial symulowany mecz - zmienna bets
        3. updejtujemy slownik o nowo zdobyte punkty
        4. sortujemy po zdobytych punktach
        5. ustawimy miejsce w rankingu

    """

    try:
        with open(classification_file_name) as data_file:
            classification = json.load(data_file)
    except EnvironmentError:
        return None

    simulated_classification = _convert_dict(classification, match.tournament.name)

    # moze to byc pierwszy mecz w turnieju wiec turnieju jeszcze nie ma w kluczach
    if not (match.tournament.name in simulated_classification.keys()):
        simulated_classification.update({match.tournament.name: {}})
        simulated_classification[match.tournament.name].update({'GeneralClassification': {}})

    # moze to byc pierwszy mecz w rundzie wiec rundy jeszcze nie ma w kluczach
    if not (match.round in simulated_classification[match.tournament.name].keys()):
        simulated_classification[match.tournament.name].update({match.round: {}})

    bets = bet_list(match=match)

    # pierwszy mecz w turnieju, ktorego nikt jeszcze nie obstawił - nie ma co symulowac
    if not bets and not simulated_classification[match.tournament.name]['GeneralClassification']:
        return None

    for tournament_name, rounds in simulated_classification.items():
        if (tournament_name == match.tournament.name):
            for round, user_scores in rounds.items():
                for bet in bets:
                    user_name = str(bet.user)
                    if (round == match.round) or (round == 'GeneralClassification'):
                        score = calculate_score(bet, match)
                        if user_name in simulated_classification[tournament_name][round].keys():
                            # simulated_classification[tournament_name][round][user_name] += bet.score #zmiana na euro21
                            simulated_classification[tournament_name][round][user_name] += score
                        else:
                            # simulated_classification[tournament_name][round][user_name] = bet.score #zmiana na euro21
                            simulated_classification[tournament_name][round][user_name] = score

    sorted_rounds_results = _sort_dict(simulated_classification)
    sorted_rounds_results_with_place = _set_place(sorted_rounds_results)

    sorted_rounds_results_with_place = _set_classification_changes(sorted_rounds_results_with_place)

    return sorted_rounds_results_with_place


def _convert_dict(classification_dict, tournament):
    """
    Z formatu jaki mamy w pliku classification_file.json:

    {tournament : {'round' : [(place,user, score), (place,user, score)... ]...
                               'summary' : [(place, user, score), (place, user, score)... ]}

    na taka (taka sama jest tworzona w funkcji get_points_per_user):

    {tournament: {'round': {user: score, user: score)}...
                'GeneralClassification': {user: score}, {user: score}...}

    I zwracamy dla wybranego turnieju

    """
    # TODO: parametr tournament moze byc opcjonalny

    converted_dict = {}

    for tournament_name, rounds in classification_dict.items():
        if tournament != tournament_name:
            continue

        if not (tournament_name in converted_dict.keys()):
            converted_dict[tournament_name] = {'GeneralClassification': {}}

        for round, user_scores in rounds.items():
            if not (round in converted_dict[tournament_name].keys()):
                converted_dict[tournament_name][round] = {}

            for place, _, user, points in user_scores:
                converted_dict[tournament_name][round][user] = points

    return converted_dict


def player_results(user):
    """
    Potrzebne do zakladki moje wyniki - tak zebysmy widzieli swoje punkty i miejsce w klasyfikacji
    """

    results = {}
    for tournament_name, rounds in get_classification().items():
        for round, user_scores in rounds.items():
            # nie pokazuje rundy w zakladce my result jesli turniej ma ustawione general_classification_only
            if get_tournament(
                    tournament_name=tournament_name).general_classification_only and round != "GeneralClassification":
                pass
            else:
                for user_result in user_scores:
                    place, _,  user_name, score = user_result
                    if (user_name == user.__str__()):
                        if not (tournament_name in results.keys()):
                            results[tournament_name] = {}
                        results[tournament_name].update({round: [user_result]})  # TODO: ta lista jest slaba - zmienic

    return results


@receiver(post_save, sender=User)
def apply_permissions_to_new_user(sender, instance, created, **kwargs):
    """
    Create a Profile instance for all newly created User instances. We only
    run on user creation to avoid having to check for existence on each call
    to User.save.
    """

    if created and (str(instance) != "guest"):
        permission1 = Permission.objects.get(name='Can add bet')
        permission2 = Permission.objects.get(name='Can change bet')
        instance.user_permissions.add(permission1, permission2)
