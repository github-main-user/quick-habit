from rest_framework import generics

from users.permissions import IsOwner

from .models import Habit
from .paginators import HabitPaginator
from .serializers import HabitSerializer


class PublicHabitListAPIView(generics.ListAPIView):
    """List endpoint for public habits."""

    serializer_class = HabitSerializer
    pagination_class = HabitPaginator
    queryset = Habit.objects.filter(is_public=True)


class HabitListCreateAPIView(generics.ListCreateAPIView):
    """
    List/Create endpoint for habits.
    Returns only habits that belong to curent user.
    """

    serializer_class = HabitSerializer
    pagination_class = HabitPaginator

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class HabitRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve/Update/Destroy endpoint for user's habits.
    Allows performing actions only if user is owner of object.
    """

    serializer_class = HabitSerializer

    queryset = Habit.objects.all()
    permission_classes = [IsOwner]
