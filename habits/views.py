from rest_framework import generics

from users.permissions import IsOwner

from .models import Habit


class HabitListCreateAPIView(generics.ListCreateAPIView):

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class HabitRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habit.objects.all()
    permission_classes = [IsOwner]
