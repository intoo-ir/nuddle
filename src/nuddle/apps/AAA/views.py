from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from . import forms
from . import helper

from .models import User


def register_view(request):
    form = forms.RegisterForm()
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            form = forms.RegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                otp = helper.get_random_otp()
                # helper.send_otp(user.phone_number, otp)
                print(otp)
                user.otp_code = otp
                user.is_active = False
                user.save()
                request.session['phone_number'] = user.phone_number
                return HttpResponseRedirect(reverse('verify'))
        else:
            otp = helper.get_random_otp()
            # helper.send_otp(phone_number, otp)
            print(otp)
            user.otp_code = otp
            user.save()
            request.session['phone_number'] = phone_number
            return HttpResponseRedirect(reverse('verify'))

    return render(request, 'register.html', {'form': form})


def verify_view(request):
    try:
        phone_number = request.session.get('phone_number')
        user = get_object_or_404(User, phone_number=phone_number)

        if request.method == 'POST':
            if not helper.check_otp_expiration(user.phone_number):
                messages.error(request, 'otp is expired,please try again!')
                return HttpResponseRedirect(reverse('verify'))

            entered_otp = int(request.POST.get('otp'))
            if user.otp_code != entered_otp:
                messages.error(request, 'otp is incorrect,please try again!')
                return HttpResponseRedirect(reverse('verify'))
            user.is_active = True
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('dashboard'))

        return render(request, 'verify.html', {"phone_number": phone_number, "otp": user.otp_code})

    except User.DoesNotExist:
        messages.error(request, 'we have an error!,please try again!')
        return HttpResponseRedirect(reverse('register'))


def dashboard_view(request):
    return render(request, 'dashboard.html')
