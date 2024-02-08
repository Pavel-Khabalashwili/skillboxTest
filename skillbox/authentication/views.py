from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.contrib.auth import logout, login, authenticate
from django.urls import reverse
import pyotp

def logout_view(request: HttpRequest):
    totp = pyotp.TOTP(pyotp.random_base32())
    request.session['otp_secret'] = totp.secret

    logout(request)
    return redirect(reverse("authentication:authentication"))

def login_view(request: HttpRequest):
    otp_required = False

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.requires_otp:
                otp_required = True
            else:
                login(request, user)
                return redirect(reverse("some_other_view"))
    return render(request, 'authentication/authentication.html', {'otp_required': otp_required})