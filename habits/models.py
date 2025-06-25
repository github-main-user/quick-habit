from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Habit(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habits")
    place = models.CharField(max_length=255)
    time = models.TimeField()
    action = models.CharField(max_length=255)
    is_pleasant = models.BooleanField(default=False)
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Related pleasant habit (can't be used if reward is set)",
    )
    frequency = models.PositiveSmallIntegerField(
        default=1, help_text="Frequency of habit execution in days"
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Rewad for completing the habit (can't be used with related habit)",
    )
    execution_time = models.PositiveSmallIntegerField(
        help_text="Execution time in seconds (<=120s)"
    )
    is_public = models.BooleanField(
        default=False, help_text="Public habits can be seen by all users"
    )

    class Meta:
        ordering = ("time",)
        indexes = (
            models.Index(fields=["owner"]),
            models.Index(fields=["is_pleasant"]),
            models.Index(fields=["is_public"]),
        )

    def __str__(self) -> str:
        return f"{self.action} at {self.time} in {self.place}"


class HabitNotification(models.Model):
    habit = models.ForeignKey(
        Habit, on_delete=models.CASCADE, related_name="notifications"
    )
    date = models.DateField()

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("habit", "date"), name="unique_notification_for_date"
            ),
        )
