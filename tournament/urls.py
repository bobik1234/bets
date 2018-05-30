from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^info/$', views.info, name='info'),
    url(r'^my_results/$', views.my_results, name='my_results'),
    url(r'^tournament/(?P<tournament_name>.+)/$', views.tournament, name='tournament'),
    url(r'^vote_overview/$', views.vote_overview, name='vote_overview'),
    url(r'^vote_form/$', views.vote_form, name='vote_form'),
    url(r'^vote_change_form/$', views.vote_change_form, name='vote_change_form'),
    url(r'^other_results/$', views.other_results, name='other_results'),
]
