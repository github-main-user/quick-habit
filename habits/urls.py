from django.urls import path

from .apps import HabitsConfig
from .views import (
    HabitListCreateAPIView,
    HabitRetrieveUpdateDestroyAPIView,
    PublicHabitListAPIView,
)

app_name = HabitsConfig.name

urlpatterns = [
    path("public/", PublicHabitListAPIView.as_view(), name="habit-list-public"),
    path("", HabitListCreateAPIView.as_view(), name="habit-list"),
    path("<int:pk>/", HabitRetrieveUpdateDestroyAPIView.as_view(), name="habit-detail"),
]
