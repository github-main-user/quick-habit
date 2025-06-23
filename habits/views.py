from rest_framework import generics

from users.permissions import IsOwner

from .models import Habit
from .serializers import HabitSerializer


class HabitListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = HabitSerializer

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class HabitRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitSerializer

    queryset = Habit.objects.all()
    permission_classes = [IsOwner]
