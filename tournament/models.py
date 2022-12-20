from django.db import models
from django.conf import settings
from django_countries.fields import CountryField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

#ROUND = (('1','one'), ('2','two'), ('3','three'), ('QF', "Quarterfinal"), ('SF', "Semifinal"), ('F', "Final"), ('All', "All"))
ROUND = (('All', "All"),('1','one'), ('2','two'), ('3','three'), ('CP', "Faza Pucharowa"))

class Tournament(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    general_classification_only = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Match(models.Model):
    id = models.AutoField(primary_key=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    home_team = CountryField()
    away_team = CountryField()
    round = models.CharField(max_length=3, choices=ROUND, default='1')
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
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True)
    expected_home_goals = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    expected_away_goals = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    score = models.DecimalField(max_digits=1, decimal_places=0, blank=True, null=True)

    def expected_result_to_str(self):
        return "{hg}:{ag}".format(hg=self.expected_home_goals, ag=self.expected_away_goals)

    def __str__(self):
        return 'User: {} Match: {} - {} Bet: {} : {} Score: {}'.format(self.user,
                                                                self.match.home_team.name,
                                                                self.match.away_team.name,
                                                                self.expected_home_goals,
                                                                self.expected_away_goals,
                                                                self.score)



#https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    notifications = models.BooleanField(default=False)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.player.save()

