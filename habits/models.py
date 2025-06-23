from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Habit(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habits")
    place = models.CharField(max_length=255)
    time = models.DateTimeField()
    action = models.CharField(max_length=255)
    is_pleasant = models.BooleanField(default=False)
    related_habit = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True
    )
    frequency = models.PositiveSmallIntegerField(default=1)
    reward = models.CharField(max_length=255, blank=True, null=True)
    execution_time = models.PositiveSmallIntegerField()
    is_public = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["owner"]),
            models.Index(fields=["is_pleasant"]),
            models.Index(fields=["is_public"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} at {self.place} at {self.time}"
