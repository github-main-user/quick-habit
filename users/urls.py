from django.urls import path

from .apps import UsersConfig
from .views import RegisterView

app_name = UsersConfig.name


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
]
