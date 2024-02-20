from kavenegar import *
import datetime
from nuddle.apps.AAA import models
from nuddle.envs.common import Kavenegar_API
from random import randint
from django.utils import timezone


def send_otp(phone_number, otp):
    phone_number = [phone_number, ]
    try:
        api = KavenegarAPI(Kavenegar_API)
        params = {
            'sender': '1000689696',  # optional
            'receptor': phone_number,  # multiple mobile numbers, split by comma
            'message': 'your otp is: {}'.format(otp),
        }
        response = api.sms_send(params)

        if response and response.status == 200:
            print("Sending OTP to:", phone_number)
            print("OTP Code:", otp)
            print("Kavenegar API response:", response)
        else:
            print("Failed to send OTP. Kavenegar API response:", response)

    except APIException as e:
        print("Kavenegar API exception:", e)
    except HTTPException as e:
        print("HTTP exception:", e)


def get_random_otp():
    return randint(1000, 9999)


def check_otp_expiration(phone_number):
    try:
        user = models.User.objects.get(phone_number=phone_number)
        now = timezone.now()
        otp_time = user.otp_creation_time
        otp_margin_time = now - otp_time
        print('OTP expiration time:', otp_margin_time.total_seconds())
        if otp_margin_time.total_seconds() > 120:
            return False
        else:
            return True
    except models.User.DoesNotExist:
        return False


def verify_otp(phone_number, entered_otp, otp_creation_time):
    try:
        user = models.User.objects.get(phone_number=phone_number)
        now = timezone.now()
        otp_time = otp_creation_time
        if not check_otp_expiration(phone_number):
            print('OTP is expired.')
            return False
        return user.otp_code == entered_otp
    except models.User.DoesNotExist:
        print('User does not exist.')
        return False
