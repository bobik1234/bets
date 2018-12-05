from django.conf.urls import url, include
from django.contrib import admin
from django_registration.forms import RegistrationFormUniqueEmail
from django_registration.backends.activation.views import RegistrationView
from django.contrib.auth import views as auth_views
from tournament.views import EmailChange, EmailChangeDone, PasswordChange, PasswordChangeDone, Logout

urlpatterns = [
    url(r'^$', auth_views.LoginView.as_view(), name='login'),
    url(r'^tournament/', include('tournament.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^logout/', Logout.as_view(), name='logout'),
    url(r'^password_reset_done/$', auth_views.password_reset_done,
            {'template_name': 'registration/reset_password_done.html'}, name='password_reset_done'),
    url(r'^password_reset/$', auth_views.password_reset,
            {'template_name': 'registration/reset_password_form.html',
             'email_template_name' : 'registration/reset_password_email.html'}, name='password_reset'),
    url(r'^password_change_done/$', PasswordChangeDone.as_view(), name='change_password_done'),
    url(r'^password_change/$', PasswordChange.as_view(), name='change_password'),
    url(r'^email_change/$', EmailChange.as_view(), name='change_email'),
    url(r'^email_change_done/$', EmailChangeDone.as_view(), name='change_email_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm,
        {'template_name': 'registration/reset_password_confirm.html'}, name='password_reset_confirm'),
    url(r'^reset_done/$', auth_views.password_reset_complete,
            {'template_name': 'registration/reset_password_complete.html'}, name='password_reset_complete'),
    url(r'^accounts/register/$',RegistrationView.as_view(form_class=RegistrationFormUniqueEmail),
        name='registration_register'),
    url(r'^accounts/', include('django_registration.backends.activation.urls')),
]
