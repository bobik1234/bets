from django.contrib import admin
from django_registration.forms import RegistrationFormUniqueEmail
from django_registration.backends.activation.views import RegistrationView
from django.contrib.auth import views as auth_views
from tournament.views import EmailChange, EmailChangeDone, PasswordChange, PasswordChangeDone, Logout
from django.urls import path, re_path, include


urlpatterns = [
    re_path(r'^$', auth_views.LoginView.as_view(), name='login'),
    path('tournament/', include('tournament.urls')),
    path('admin/', admin.site.urls),
    path('logout/', Logout.as_view(), name='logout'),
    path('password_reset_done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/reset_password_done.html'),
        name='password_reset_done'),
    path('password_reset/',
        auth_views.PasswordResetView.as_view(template_name='registration/reset_password_form.html',
                                             email_template_name='registration/reset_password_email.html'),
        name='password_reset'),
    path('password_change_done/', PasswordChangeDone.as_view(), name='change_password_done'),
    path('password_change/', PasswordChange.as_view(), name='change_password'),
    path('email_change/', EmailChange.as_view(), name='change_email'),
    path('email_change_done/', EmailChangeDone.as_view(), name='change_email_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.PasswordResetConfirmView.as_view(template_name='registration/reset_password_confirm.html'),
            name='password_reset_confirm'),
    path('reset_done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/reset_password_complete.html'),
        name='password_reset_complete'),
    path('accounts/register/',RegistrationView.as_view(form_class=RegistrationFormUniqueEmail),
        name='registration_register'),
    path('accounts/', include('django_registration.backends.activation.urls')),
]
