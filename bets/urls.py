"""bets URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from registration.forms import RegistrationFormUniqueEmail
from registration.backends.hmac.views import RegistrationView

from tournament import views
from django.contrib.auth import views as auth_views

from tournament.views import EmailChange, EmailChangeDone, PasswordChange, PasswordChangeDone

urlpatterns = [
    #url(r'^$', views.index, name='index'),
    url(r'^$', views.Index.as_view(), name=''),
    url(r'^tournament/', include('tournament.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/password/reset/done/$', auth_views.password_reset_done,
            {'template_name': 'registration/reset_password_done.html'}, name='password_reset_done'),
    url(r'^password_reset/$', auth_views.password_reset,
            {'template_name': 'registration/reset_password_form.html',
             'email_template_name' : 'registration/reset_password_email.html'}, name='password_reset'),
    url(r'^accounts/password/change/done/$', PasswordChangeDone.as_view(), name='change_password_done'),
    url(r'^accounts/password/change/$', PasswordChange.as_view(), name='change_password'),
    url(r'^accounts/email_change/$', EmailChange.as_view(), name='change_email'),
    url(r'^accounts/email_change_done/$', EmailChangeDone.as_view(), name='change_email_done'),
    url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, {'template_name': 'registration/reset_password_confirm.html'}, name='password_reset_confirm'),
    url(r'^accounts/password/reset/complete/$', auth_views.password_reset_complete,
            {'template_name': 'registration/reset_password_complete.html'}, name='password_reset_complete'),

    url(r'^accounts/register/$',RegistrationView.as_view(form_class=RegistrationFormUniqueEmail),
        name='registration_register'),
    #url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^accounts/', include('registration.backends.hmac.urls')),
]
