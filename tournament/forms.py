from django import forms
from tournament.models import Bet, Tournament, ROUND
from tournament.db_handler import get_user, match_list

class Vote(forms.Form):

    def __init__(self, *args, **kwargs):

        if 'matches_to_bet' in kwargs.keys():
            ongoing_bets = None
            matches = kwargs.pop('matches_to_bet')
        elif 'ongoing_bets' in kwargs.keys():
            ongoing_bets = kwargs.pop('ongoing_bets')
            matches = [bet.match for bet in ongoing_bets]

        user = kwargs.pop('user')

        super(Vote, self).__init__(*args, **kwargs)

        if ongoing_bets is None:
            for i, match in enumerate(matches):
                self.fields["{}_{}".format(match.home_team.name, match.id)] = forms.DecimalField(max_digits=2, min_value=0)
                self.fields["{}_{}".format(match.away_team.name, match.id)] = forms.DecimalField(max_digits=2, min_value=0)
        else:
            for i, match in enumerate(matches):
                bet = Bet.objects.get(match=match, user=user)
                self.fields["{}_{}".format(match.home_team.name, match.id)] = forms.DecimalField(max_digits=2, min_value=0, initial= bet.expected_home_goals)
                self.fields["{}_{}".format(match.away_team.name, match.id)] = forms.DecimalField(max_digits=2, min_value=0, initial= bet.expected_away_goals)

    #def predicted_result(self):
    #    for name, value in self.cleaned_data.items():
    #        yield (name, value)

class ChooseUser(forms.Form):

    def __init__(self, *args, **kwargs):

        # TODO: w **kwargs dodac czy robimy to dla acive turnaments czy nie
        super(ChooseUser, self).__init__(*args, **kwargs)

        users = []
        for user in get_user():
            if (str(user) == "admin") or not user.is_active:
                continue

            #users.append((user,str(user)))
            users.append((user, user))

        #TODO: lista turnieji dostepna jest w context_processors dla kazej sesji - zamiast robic od nowa sciagnac z tamtad zmienna
        tournaments = []
        for tournament in list(Tournament.objects.all()):
            if tournament.active:
                tournaments.append((tournament, tournament))

        self.fields["choose_user_field"] = forms.ChoiceField(choices=users, widget=forms.Select(), required=True)
        self.fields["choose_tournament"] = forms.ChoiceField(choices=tournaments, widget=forms.Select(), required=True)
        self.fields["choose_round"] = forms.ChoiceField(choices=ROUND, widget=forms.Select(), required=True)

class ChooseMatch(forms.Form):

    def __init__(self, *args, **kwargs):

        # TODO: w zakladam ze tylko z aktywnych turnieji
        super(ChooseMatch, self).__init__(*args, **kwargs)

        m_list = []
        for match in match_list():
            m_list.append((match.id, match.teams_to_string()))

        self.fields["choose_match_field"] = forms.ChoiceField(choices=m_list, widget=forms.Select(), required=True)
