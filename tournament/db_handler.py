from tournament.models import Bet, Match, Tournament
from django.contrib.auth.models import User

def bet_list(user = None, match = None):
    """
    Zwraca liste zakladow z tablicy Bet - jesli podamy usera to dla danego usera
    :param user:
    :return:
    """

    if (user is not None) and (match is None):
        return list(Bet.objects.filter(user=user))
    elif (user is not None) and (match is not None):
        return list(Bet.objects.filter(user=user, match=match))
    elif (user is None) and (match is not None):
        return list(Bet.objects.filter(match=match))
    else:
        return list(Bet.objects.all())


def match_list(tournament_name=None, round='All'):
    """
    Zwraca liste meczy z tablicy Match

    :param tournament_name:
    :param round:
    :return:
    """

    if tournament_name is not None:
        tournament = Tournament.objects.get(name=tournament_name)
        if round == 'All':
            return Match.objects.filter(tournament=tournament)
        else:
            return Match.objects.filter(tournament=tournament, round=round)
    else:
        if round == 'All':
            return Match.objects.all()
        else:
            return Match.objects.filter(round=round)

def get_tournament(tournament_name = None):

    if tournament_name is None:
        return Tournament.objects.all()
    else:
        return  Tournament.objects.get(name=tournament_name)

def get_user(user_name = None):

    if user_name is None:
        return User.objects.all()
    else:
        return  User.objects.get(username=user_name)

def get_users_email():

    emails = []
    for user in User.objects.all():
        emails.append(user.email)

    return emails

def does_user_exist(user_name):
    return User.objects.filter(username=user_name).exists()

def create_user(username, password, email=None):
    if email is None:
        User.objects.create_user(username=username, password=password)
    else:
        User.objects.create_user(username=username, password=password, email=email)

def get_match(mach_id):
    return Match.objects.get(id=mach_id)

def add_bet(user, match, expected_home_goals, expected_away_goals):

    m = Bet(user=user, match=match, expected_home_goals=expected_home_goals, expected_away_goals=expected_away_goals)
    m.save()

def update_goals_bet(bet_id, expected_home_goals, expected_away_goals):

    Bet.objects.filter(id=bet_id).update(expected_home_goals = expected_home_goals, expected_away_goals = expected_away_goals)

def update_score_bet(bet_id, score):

    Bet.objects.filter(id=bet_id).update(score=score)