from django.contrib.auth.views import LoginView
from django.urls import path
from . import views
from .forms import VerifiedAuthenticationForm

app_name = 'accounts'
urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', LoginView.as_view(authentication_form=VerifiedAuthenticationForm,
    template_name='accounts/login.html'), name='login'),
    path('verify/sent/', views.verify_sent_view, name='verify_sent'),
    path('verify/resend/', views.resend_verification_view, name='resend_verification'),
    path('verify/<uidb64>/<token>/', views.verify_email_view, name='verify_email'),
]