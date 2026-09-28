from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from . import views
from .forms import StyledPasswordResetForm

app_name = 'accounts'
urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.ThrottledLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/sent/', views.verify_sent_view, name='verify_sent'),
    path('verify/resend/', views.resend_verification_view, name='resend_verification'),
    path('verify/<uidb64>/<token>/', views.verify_email_view, name='verify_email'),
    path('password-reset/', PasswordResetView.as_view(form_class=StyledPasswordResetForm, template_name='password-reset.html', email_template_name='email/password_reset_email.html', success_url='/accounts/password-reset/done/'), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='password-reset-done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='password-reset-confirm.html', success_url='/accounts/reset/done/'), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='password-reset-complete.html'), name='password_reset_complete'),
]
