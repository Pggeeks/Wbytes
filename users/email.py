from .models import CustomUser
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

def send_forgot_email(request,username, email, link):
    # Sending email to user for password reset
    subject = "Reset Password"
    message = render_to_string('users/reset_forgot_password.html', {
        'request': request,
        'link':link,
        'user': username,
    })
    email = EmailMessage(
        subject, message,settings.EMAIL_HOST_USER,to=[email]
    )
    email.content_subtype = 'html'
    email.send()
    print(email)
    return True