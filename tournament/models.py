from django.db import models
from django.conf import settings
from django_countries.fields import CountryField

ROUND = (('1','one'), ('2','two'), ('3','three'),
             ('QF', "Quarterfinal"), ('SF', "Semifinal"), ('F', "Final"), ('All', "All"))

class Tournament(models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    home_team = CountryField()
    away_team = CountryField()
    round = models.CharField(max_length=2, choices=ROUND, default='1')
    home_goals = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    away_goals = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    match_date = models.DateTimeField(blank=True, null=True)

    def final_result_to_str(self):
        return "{hg}:{ag}".format(hg=self.home_goals, ag=self.away_goals)

    def teams_to_string(self):
        return "{ht}:{at}".format(ht=self.home_team.name, at=self.away_team.name)

    def __str__(self):
        return '{} - {} {} Reslut: {} : {}'.format(self.home_team.name,
                                                   self.away_team.name,
                                                   self.match_date.strftime("%A, %d %B %Y, %H:%M"),
                                                   self.home_goals,
                                                   self.away_goals,)

class Bet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True)
    expected_home_goals = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    expected_away_goals = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)

    def expected_result_to_str(self):
        return "{hg}:{ag}".format(hg=self.expected_home_goals, ag=self.expected_away_goals)

    def __str__(self):
        return 'User: {} Match: {} - {} Bet: {} : {}'.format(self.user,
                                                             self.match.home_team.name,
                                                             self.match.away_team.name,
                                                             self.expected_home_goals,
                                                             self.expected_away_goals)


