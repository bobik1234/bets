from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^info/$', views.Info.as_view(), name='info'),
    url(r'^my_results/$', views.MyResults.as_view(), name='my_results'),
    url(r'^tournament/(?P<tournament_name>.+)/$', views.Tournament.as_view(), name='tournament'),
    url(r'^vote_overview/$', views.vote_overview, name='vote_overview'),
    url(r'^vote_done/$', views.VoteDone.as_view(), name='vote_done'),
    url(r'^vote_form/$', views.VoteForm.as_view(), name='vote_form'),
    url(r'^vote_change_form/$', views.VoteChangeForm.as_view(), name='vote_change_form'),
    url(r'^vote_change_done/$', views.VoteChangeDone.as_view(), name='vote_change_done'),
    url(r'^other_results/$', views.OtherResultForm.as_view(), name='other_results'),
    url(r'^too_late_to_bet/$', views.TooLateToBet.as_view(), name='too_late_to_bet'),
    url(r'^ongoing_match_bets/$', views.SeeOngoingMatchBets.as_view(), name='ongoing_match_bets'),
    url(r'^finished_match_bets/$', views.SeeFinishedMatchBets.as_view(), name='finished_match_bets'),
    url(r'^simulation/$', views.SimulationForm.as_view(), name='simulation'),
]
