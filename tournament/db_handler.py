from tournament.models import Bet, Match, Tournament
from django.contrib.auth.models import User

def bet_list(user = None):
    """
    Zwraca liste zakladow z tablicy Bet - jesli podamy usera to dla danego usera
    :param user:
    :return:
    """

    if user is not None:
        return list(Bet.objects.filter(user=user))
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


def get_user(user_name = None):

    if user_name is None:
        return User.objects.all()
    else:
        return  User.objects.get(username=user_name)
