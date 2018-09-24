from tournament.models import Tournament

def menu(request):
    """
    Ustawia nazwy turnieji w menu gornym (patrz szablon base.html oraz ustawienia settings.py)

    :param request:
    :return:
    """
    tournaments = []
    for tournament in list(Tournament.objects.all()):
        if tournament.active:
            tournaments.append(tournament)
    return {
        'tournaments': tournaments,
    }