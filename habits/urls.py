from django.urls import path

from .apps import HabitsConfig
from .views import HabitListCreateAPIView, HabitRetrieveUpdateDestroyAPIView

app_name = HabitsConfig.name

urlpatterns = [
    path("", HabitListCreateAPIView.as_view(), name="habit-list"),
    path("<int:pk>/", HabitRetrieveUpdateDestroyAPIView.as_view(), name="habit-detail"),
]
