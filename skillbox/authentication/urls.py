from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.urls import path
from .views import *

app_name = "authentication"

urlpatterns = [
    path("", 
        LoginView.as_view(
        template_name='authentication/authentication.html',
        redirect_authenticated_user=True,
        authentication_form = AuthenticationForm
        ), 
        name="authentication"),
    path("logout/", logout_view, name="logout"),
]