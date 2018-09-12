from django import forms

from tournament.models import Bet, Tournament, ROUND
from tournament.db_handler import get_user, match_list, get_users_email
from django.utils.translation import ugettext_lazy as _

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
                self.fields["{}_{}".format(match.home_team.name, match.id)] = forms.DecimalField(max_digits=2, min_value=0, required=False)
                self.fields["{}_{}".format(match.away_team.name, match.id)] = forms.DecimalField(max_digits=2, min_value=0, required=False)
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
            if (str(user) == "admin") or (str(user) == "guest") or not user.is_active:
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
        if 'ongoing_matches' in kwargs.keys():
            ongoing_matches = kwargs.pop('ongoing_matches')

        # TODO: w zakladam ze tylko z aktywnych turnieji
        super(ChooseMatch, self).__init__(*args, **kwargs)

        #default_choice = ('D', 'Wybierz mecz')
        #m_list = [default_choice]

        list = []
        for match in match_list():
            if ongoing_matches:
                if (match.home_goals is None) or (match.away_goals is None):
                    list.append((match.id, match.teams_to_string()))
            else:
                if (match.home_goals is not None) or (match.away_goals is not None):
                    list.append((match.id, match.teams_to_string()))

        if list:
            default_choice = ('D', 'Wybierz mecz')
            m_list = [default_choice]
            m_list.extend(list)

            self.fields["choose_match_field"] = forms.ChoiceField(choices=m_list,
                                                                  widget=MySelect(disabled_choices=default_choice,
                                                                                  selected_choices = default_choice,
                                                                                  attrs={"onChange": 'submit()'}),
                                                                  required=True)
        else:
            self.no_matches = True

class ChooseMatchResult(forms.Form):
    def __init__(self, *args, **kwargs):

        super(ChooseMatchResult, self).__init__(*args, **kwargs)

        self.fields["ht_goals"] = forms.DecimalField(max_digits=2, decimal_places=0)
        self.fields["at_goals"] = forms.DecimalField(max_digits=2, decimal_places=0)



class MySelect(forms.Select):

    def __init__(self, attrs=None, choices=(), disabled_choices=(), selected_choices=()):
        super(forms.Select, self).__init__(attrs, choices=choices)
        # disabled_choices is a list of disabled values
        self.disabled_choices = disabled_choices
        # selected_choices is a list of selected values
        self.selected_choices = selected_choices

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super(forms.Select, self).create_option(name, value, label, selected, index, subindex, attrs)
        if value in self.disabled_choices:
           option['attrs']['disabled'] = True
        if value in self.selected_choices:
           option['attrs']['selected'] = True
        return option

class EmailChangeForm(forms.Form):
    """
    A form that lets a user change set their email while checking for a change in the
    e-mail.
    """
    error_messages = {
        'email_mismatch': _("The two email addresses fields didn't match."),
        'not_changed': _("The email address is the same as the one already defined."),
        'already_exists': _("The email address already exists for another user."),
    }

    new_email1 = forms.EmailField(
        label=_("New email address"),
        widget=forms.EmailInput,
    )

    new_email2 = forms.EmailField(
        label=_("New email address confirmation"),
        widget=forms.EmailInput,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    def clean_new_email1(self):
        old_email = self.user.email
        new_email1 = self.cleaned_data.get('new_email1')
        if new_email1 and old_email:
            if new_email1 == old_email:
                raise forms.ValidationError(
                    self.error_messages['not_changed'],
                    code='not_changed',
                )
        if new_email1 in get_users_email():
                raise forms.ValidationError(
                    self.error_messages['already_exists'],
                    code='already_exists',
                )

        return new_email1

    def clean_new_email2(self):
        new_email1 = self.cleaned_data.get('new_email1')
        new_email2 = self.cleaned_data.get('new_email2')
        if new_email1 and new_email2:
            if new_email1 != new_email2:
                raise forms.ValidationError(
                    self.error_messages['email_mismatch'],
                    code='email_mismatch',
                )
        return new_email2

    def save(self, commit=True):
        email = self.cleaned_data["new_email1"]
        self.user.email = email
        if commit:
            self.user.save()
        return self.user