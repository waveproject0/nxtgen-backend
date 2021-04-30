from django.contrib.auth import login
from account.models import User, EmailToken
from django.utils.encoding import force_text
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
from account.token import account_activation_token


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user_email_token = EmailToken.objects.get(id=user.emailtoken.id)        
        user_email_token.email_verified = True
        user.save()
        user_email_token.save()
        #login(request, user)
        return HttpResponse('Account is activated :) you can login know')
    else:
        return HttpResponse('Activation link is invalid!')