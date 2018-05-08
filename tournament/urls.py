from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^info/$', views.info, name='info'),
    url(r'^my_results/$', views.my_results, name='my_results'),
    url(r'^tournament/(?P<tournament_name>.+)/$', views.tournament, name='tournament'),
    url(r'^vote_overview/$', views.vote_overview, name='vote_overview'),
    url(r'^vote_form/$', views.vote_form, name='vote_form'),
]
