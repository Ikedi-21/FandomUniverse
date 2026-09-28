from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import email_token_generator


def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_token_generator.make_token(user)
    link = request.build_absolute_uri(
        reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token})
    )
    body = render_to_string('accounts/email/verify_email.txt', {
        'user': user,
        'link': link,
        'expiry_hours': settings.PASSWORD_RESET_TIMEOUT // 3600,
    })
    send_mail('Verify your Fan Hub Plus account', body, None, [user.email])   # None = DEFAULT_FROM_EMAIL