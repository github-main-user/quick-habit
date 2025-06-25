from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from requests import HTTPError
from rest_framework import status
from rest_framework.test import APITestCase

from habits.services import send_telegram_message

from .models import Habit

User = get_user_model()


class HabitAPITest(APITestCase):
    def setUp(self) -> None:
        self.owner = User.objects.create_user(email="test@test.com", password="test")
        self.other_user = User.objects.create_user(
            email="other@other.com", password="other"
        )

        self.pleasant = Habit.objects.create(
            **self.habit_data(owner=self.owner, is_pleasant=True)
        )
        self.habit_with_reward = Habit.objects.create(
            **self.habit_data(
                owner=self.owner, is_pleasant=False, reward="eat a piece of chocolate"
            )
        )
        self.habit_with_related = Habit.objects.create(
            **self.habit_data(
                owner=self.owner, is_pleasant=False, related_habit=self.pleasant
            )
        )

        Habit.objects.create(
            **self.habit_data(owner=self.owner, is_pleasant=True, is_public=True)
        )
        Habit.objects.create(
            **self.habit_data(owner=self.other_user, is_pleasant=True, is_public=True)
        )
        Habit.objects.create(
            **self.habit_data(
                owner=self.owner,
                is_pleasant=False,
                reward="order coffee from favorite place",
                is_public=True,
            )
        )

    def authenticate(self, user) -> None:
        self.client.force_authenticate(user)

    def habit_data(self, **overrides) -> dict:
        data = {
            "place": "home",
            "time": "20:00",
            "action": "take a bubble bath",
            "frequency": 1,
            "execution_time": 10,
        }
        data.update(overrides)
        return data

    # list public

    def test_list_public_unauthenticated(self) -> None:
        response = self.client.get(reverse("habits:habit-list-public"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNone(response.data.get("results"))

    def test_list_public_success(self) -> None:
        self.authenticate(self.owner)

        response = self.client.get(reverse("habits:habit-list-public"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("count"), Habit.objects.filter(is_public=True).count()
        )

    # list

    def test_list_unauthenticated(self) -> None:
        response = self.client.get(reverse("habits:habit-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNone(response.data.get("results"))

    def test_list_success(self) -> None:
        self.authenticate(self.owner)

        response = self.client.get(reverse("habits:habit-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("count"), Habit.objects.filter(owner=self.owner).count()
        )

    # create

    def test_create_habit_unauthenticated(self) -> None:
        response = self.client.post(
            reverse("habits:habit-list"),
            self.habit_data(is_pleasant=False, reward="play computer"),
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_habit_with_bad_frequency_failure(self) -> None:
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("habits:habit-list"),
            self.habit_data(is_pleasant=False, reward="play computer", frequency=0),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            reverse("habits:habit-list"),
            self.habit_data(is_pleasant=False, reward="play computer", frequency=8),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_with_bad_execution_time_failure(self) -> None:
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("habits:habit-list"),
            self.habit_data(
                is_pleasant=False, reward="play computer", execution_time=-1
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            reverse("habits:habit-list"),
            self.habit_data(
                is_pleasant=False, reward="play computer", execution_time=121
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_with_both_reward_and_related_habit_failure(self) -> None:
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("habits:habit-list"),
            self.habit_data(
                is_pleasant=False, reward="play computer", related_habit=self.pleasant
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_pleasant_habit_with_related_habit_failure(self) -> None:
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("habits:habit-list"),
            self.habit_data(is_pleasant=True, related_habit=self.pleasant.id),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_pleasant_habit_with_reward_failure(self) -> None:
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("habits:habit-list"),
            self.habit_data(is_pleasant=True, reward="play computer"),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_with_not_pleasant_related_habit_failure(self) -> None:
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("habits:habit-list"),
            self.habit_data(is_pleasant=True, related_habit=self.habit_with_reward),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_pleasant_habit_success(self) -> None:
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("habits:habit-list"), self.habit_data(is_pleasant=True)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        habit = Habit.objects.get(id=response.data.get("id"))
        self.assertEqual(habit.owner, self.owner)

    def test_create_habit_with_related_pleasant_success(self) -> None:
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("habits:habit-list"),
            self.habit_data(is_pleasant=False, related_habit=self.pleasant.id),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        habit = Habit.objects.get(id=response.data.get("id"))
        self.assertEqual(habit.owner, self.owner)
        self.assertEqual(habit.related_habit, self.pleasant)

    def test_create_habit_with_reward_success(self) -> None:
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("habits:habit-list"),
            self.habit_data(is_pleasant=False, related_habit=self.pleasant.id),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        habit = Habit.objects.get(id=response.data.get("id"))
        self.assertEqual(habit.owner, self.owner)
        self.assertEqual(habit.related_habit, self.pleasant)

    # retrieve
    def test_retrieve_habit_not_found(self) -> None:
        self.authenticate(self.owner)

        reponse = self.client.get(reverse("habits:habit-detail", args=[0]))
        self.assertEqual(reponse.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_habit_unauthenticated(self) -> None:
        reponse = self.client.get(
            reverse("habits:habit-detail", args=[self.pleasant.id])
        )
        self.assertEqual(reponse.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_habit_owner_success(self) -> None:
        self.authenticate(self.owner)

        reponse = self.client.get(
            reverse("habits:habit-detail", args=[self.pleasant.id])
        )
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)

    def test_retrieve_habit_foreign_failure(self) -> None:
        self.authenticate(self.other_user)

        reponse = self.client.get(
            reverse("habits:habit-detail", args=[self.pleasant.id])
        )
        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)

    # update
    def test_update_habit_not_found(self) -> None:
        self.authenticate(self.owner)

        reponse = self.client.patch(reverse("habits:habit-detail", args=[0]))
        self.assertEqual(reponse.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_habit_unauthenticated(self) -> None:
        reponse = self.client.patch(
            reverse("habits:habit-detail", args=[self.pleasant.id]), {"action": "UPD"}
        )
        self.assertEqual(reponse.status_code, status.HTTP_401_UNAUTHORIZED)
        self.pleasant.refresh_from_db()
        self.assertNotEqual(self.pleasant.action, "UPD")

    def test_update_habit_owner_success(self) -> None:
        self.authenticate(self.owner)

        reponse = self.client.patch(
            reverse("habits:habit-detail", args=[self.pleasant.id]), {"action": "UPD"}
        )
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        self.pleasant.refresh_from_db()
        self.assertEqual(self.pleasant.action, "UPD")

    def test_update_habit_foreign_failure(self) -> None:
        self.authenticate(self.other_user)

        reponse = self.client.patch(
            reverse("habits:habit-detail", args=[self.pleasant.id]), {"action": "UPD"}
        )
        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)
        self.pleasant.refresh_from_db()
        self.assertNotEqual(self.pleasant.action, "UPD")

    # delete

    def test_delete_habit_not_found(self) -> None:
        self.authenticate(self.owner)

        reponse = self.client.delete(reverse("habits:habit-detail", args=[0]))
        self.assertEqual(reponse.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Habit.objects.filter(id=self.pleasant.id).exists())

    def test_delete_habit_unauthenticated(self) -> None:
        reponse = self.client.delete(
            reverse("habits:habit-detail", args=[self.pleasant.id])
        )
        self.assertEqual(reponse.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Habit.objects.filter(id=self.pleasant.id).exists())

    def test_delete_habit_owner_success(self) -> None:
        self.authenticate(self.owner)

        reponse = self.client.delete(
            reverse("habits:habit-detail", args=[self.pleasant.id])
        )
        self.assertEqual(reponse.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(id=self.pleasant.id).exists())

    def test_delete_habit_foreign_failure(self) -> None:
        self.authenticate(self.other_user)

        reponse = self.client.delete(
            reverse("habits:habit-detail", args=[self.pleasant.id])
        )
        self.assertEqual(reponse.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Habit.objects.filter(id=self.pleasant.id).exists())


class SendTelegramMessageTest(TestCase):
    @override_settings(TELEGRAM_BOT_TOKEN="dummy_token")
    @patch("habits.services.requests.post")
    def test_send_message_successfully(self, mock_post: Mock) -> None:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        send_telegram_message(123456, "test message")

        mock_post.assert_called_once_with(
            "https://api.telegram.org/botdummy_token/sendMessage",
            {"chat_id": 123456, "text": "test message"},
        )
        mock_response.raise_for_status.assert_called_once()

    @override_settings(TELEGRAM_BOT_TOKEN=None)
    @patch("habits.services.requests.post")
    def test_does_nothing_with_missing_token(self, mock_post: Mock) -> None:
        send_telegram_message(123456, "test message")

        mock_post.assert_not_called()

    @override_settings(TELEGRAM_BOT_TOKEN="dummy_token")
    @patch("habits.services.requests.post")
    def test_raises_on_bad_status(self, mock_post: Mock) -> None:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("Bad Request")
        mock_post.return_value = mock_response

        with self.assertRaises(HTTPError):
            send_telegram_message(123456, "test message")
