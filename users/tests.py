from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class UserAPITest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="test@test.com", password="test")

    # registration

    def test_registration_success(self) -> None:
        response = self.client.post(
            reverse("users:register"),
            {"email": "new@user.com", "password": "test"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@user.com").exists())

    def test_registration_already_exists(self) -> None:
        response = self.client.post(
            reverse("users:register"),
            {"email": "test@test.com", "password": "test"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.count() == 1)

    # token obtain pair

    def test_token_obtain_pair_success(self) -> None:
        response = self.client.post(
            reverse("users:token_obtain_pair"),
            {"email": "test@test.com", "password": "test"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("access") and response.data.get("refresh"))

    def test_token_obtain_pair_wrong_creds(self) -> None:
        response = self.client.post(
            reverse("users:token_obtain_pair"),
            {"email": "test@test.com", "password": "WRONG"},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(
            not response.data.get("access") and not response.data.get("refresh")
        )

    # token refresh

    def test_token_refresh_success(self) -> None:
        response = self.client.post(
            reverse("users:token_obtain_pair"),
            {"email": "test@test.com", "password": "test"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh_token = response.data.get("refresh")
        self.assertTrue(refresh_token)

        response = self.client.post(
            reverse("users:token_refresh"), {"refresh": refresh_token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("access"))

    def test_token_refresh_invalid_token(self) -> None:
        response = self.client.post(
            reverse("users:token_refresh"), {"refresh": "WRONG TOKEN"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data.get("access"))
