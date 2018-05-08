from django import forms

class Vote(forms.Form):

    def __init__(self, *args, **kwargs):
        matches_to_bet = kwargs.pop('matches_to_bet')
        super(Vote, self).__init__(*args, **kwargs)

        for i, match in enumerate(matches_to_bet):
            self.fields["{}_{}".format(match.home_team.name, match.id)] = forms.DecimalField(max_digits=2)
            self.fields["{}_{}".format(match.away_team.name, match.id)] = forms.DecimalField(max_digits=2)

    def predicted_result(self):
        for name, value in self.cleaned_data.items():
            yield (name, value)

#czy bedzie dzialal jak bede dwa mecze tej samej druzyny?? sprawdzic...