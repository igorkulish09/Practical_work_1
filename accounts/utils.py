from django.core.mail import send_mail
from django.conf import settings


def send_notification_email(subject, message, recipient_list=None):
    if not recipient_list:
        recipient_list = [admin[1] for admin in settings.ADMINS]

    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)
