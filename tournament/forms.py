from django import forms
from tournament.models import Bet

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


