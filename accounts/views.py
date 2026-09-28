import time
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from .emails import send_verification_email
from .forms import RegisterForm            # your existing register form
from .tokens import email_token_generator
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from .forms import VerifiedAuthenticationForm
User = get_user_model()
RESEND_COOLDOWN = 60   # seconds


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.email_verified = False
            user.save()
            try:
                send_verification_email(request, user)
            except Exception:
                messages.warning(request, "Account created, but we couldn't send the email. Use 'resend' below.")
            return redirect('accounts:verify_sent')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def verify_sent_view(request):
    return render(request, 'accounts/verify_sent.html')


def verify_email_view(request, uidb64, token):
    try:
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and user.email_verified:
        return render(request, 'accounts/verify_email.html', {'status': 'already'})

    if user and email_token_generator.check_token(user, token):
        user.email_verified = True
        user.save(update_fields=['email_verified'])
        return render(request, 'accounts/verify_email.html', {'status': 'success'})

    return render(request, 'accounts/verify_email.html', {'status': 'invalid'})


def resend_verification_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        user = User.objects.filter(email=email, email_verified=False).first()
        last_sent = request.session.get('last_verification_sent', 0)
        if user and time.time() - last_sent > RESEND_COOLDOWN:
            try:
                send_verification_email(request, user)
                request.session['last_verification_sent'] = time.time()
            except Exception:
                pass
        # same message whether or not the account exists, so nobody can probe which emails are registered
        messages.success(request, "If that address belongs to an unverified account, a new link is on its way.")
        return redirect('accounts:verify_sent')
    return render(request, 'accounts/resend_verification.html')

# accounts/views.py


@ratelimit(key='ip', rate='5/h', method='POST')
def register_view(request):
    ...

@ratelimit(key='ip', rate='5/h', method='POST')
@ratelimit(key='post:email', rate='3/h', method='POST')
def resend_verification_view(request):
    ...

@method_decorator(ratelimit(key='ip', rate='10/m', method='POST'), name='dispatch')
@method_decorator(ratelimit(key='post:username', rate='5/m', method='POST'), name='dispatch')
class ThrottledLoginView(LoginView):
    authentication_form = VerifiedAuthenticationForm
    template_name = 'accounts/login.html'