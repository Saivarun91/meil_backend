import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

#from twilio.rest import Client

def generate_otp():
    return str(random.randint(100000, 999999))

def otp_expired(created_time, minutes=5):
    return timezone.now() > created_time + timedelta(minutes=minutes)


def send_email_otp(email, otp):
    subject = "Your OTP Code"
    message = f"Your OTP is {otp}. It is valid for 10 minutes."
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,   # 👈 sender email (from settings.py)
        [email],                       # 👈 recipient email (user who signed up)
        fail_silently=False,
    )


# def send_sms_otp(employee):
#     otp = generate_otp()
#     employee.phone_otp = otp
#     employee.phone_otp_created = timezone.now()
#     employee.save()

#     account_sid = 'TWILIO_SID'
#     auth_token = 'TWILIO_AUTH_TOKEN'
#     client = Client(account_sid, auth_token)

#     client.messages.create(
#         body=f"Your OTP is {otp}",
#         from_='+1234567890',
#         to=employee.phone_number
#     )
