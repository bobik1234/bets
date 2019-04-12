from django.contrib import admin
from django.views.generic import TemplateView
from django_registration.forms import RegistrationFormUniqueEmail
from django_registration.backends.activation.views import RegistrationView
from django.contrib.auth import views as auth_views
from tournament.views import EmailChange, EmailChangeDone, PasswordChange, PasswordChangeDone, Logout, \
    LanguageChange_Pl, LanguageChange_En
from django.urls import path, re_path, include
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
]

urlpatterns += i18n_patterns(
    re_path(r'^$', auth_views.LoginView.as_view(), name='login'),
    re_path(r'^accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('tournament/', include('tournament.urls')),
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
    path('language_change/', TemplateView.as_view(template_name='tournament/language_change.html'), name='language_change'),
    path('language_change_pl/', LanguageChange_Pl.as_view(), name='language_change_pl'),
    path('language_change_en/', LanguageChange_En.as_view(), name='language_change_en'),
)