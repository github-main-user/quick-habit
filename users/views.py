from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import MeSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """Endpoint for user registration."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveUpdateDestroyAPIView):
    """API view to retrieve, update, or delete the authenticated user's account."""

    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user
