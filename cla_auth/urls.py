from django.urls import path
from .views import *

app_name = "cla_auth"
urlpatterns = [
    path('connexion', LoginAuthView.as_view(), name="login"),
    path('connexion/cla', HandleAuthView.as_view(), name="handle"),
    path('deconnexion', LogoutAuthView.as_view(), name="logout")
]