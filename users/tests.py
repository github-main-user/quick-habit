from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class UserManagerTest(TestCase):
    def test_create_user_success(self):
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password="testpass123")

    def test_create_superuser_success(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", password="adminpass"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_create_superuser_with_wrong_flags_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="badadmin@example.com", password="adminpass", is_staff=False
            )

        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="badadmin2@example.com", password="adminpass", is_superuser=False
            )


class UserAPITest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="test@test.com", password="test")

    def authenticate(self, user) -> None:
        self.client.force_authenticate(user)

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

    # me/ retrieve

    def test_retrieve_me_unauthenticated(self) -> None:
        response = self.client.get(reverse("users:me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_me_owner(self) -> None:
        self.authenticate(self.user)
        response = self.client.patch(reverse("users:me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("email"), self.user.email)

    # me/ update

    def test_update_me_unauthenticated(self) -> None:
        response = self.client.patch(reverse("users:me"), {"email": "new@email.com"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_me_owner(self) -> None:
        self.authenticate(self.user)
        response = self.client.patch(reverse("users:me"), {"email": "new@email.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new@email.com")

    # me/ delete

    def test_delete_me_unauthenticated(self) -> None:
        response = self.client.delete(reverse("users:me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_me_owner(self) -> None:
        self.authenticate(self.user)
        response = self.client.delete(reverse("users:me"))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())
