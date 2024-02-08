from django.urls import path
from .views import *

app_name = "register"

urlpatterns = [
    path("", RegisterView.as_view(), name="register"),
]
