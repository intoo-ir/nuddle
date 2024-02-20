# AAA/tasks.py
from celery import shared_task
from .helper import send_otp
from nuddle.envs.celery import app

@shared_task
@app.task(queue='smsOTP')
def send_otp_task(phone_number, otp_code):
    """
    Celery task to send OTP code to the given phone number.
    """
    send_otp(phone_number, otp_code)
