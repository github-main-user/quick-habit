from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        exclude = ("owner",)
        read_only_fields = ("id",)

    def validate_frequency(self, value):
        if not (1 <= value <= 7):
            raise serializers.ValidationError(
                "Execution frequency must be between 1 and 7 days"
            )
        return value

    def validate_execution_time(self, value):
        if value > 120:
            raise serializers.ValidationError(
                "Execution time must not exceed 120 seconds"
            )
        return value

    def validate(self, data):
        is_pleasant = data.get("is_pleasant")
        related_habit = data.get("related_habit")
        reward = data.get("reward")

        if related_habit and reward:
            raise serializers.ValidationError(
                "You cannot set both a related habit and a reward simultaneously."
            )

        if is_pleasant and (related_habit or reward):
            raise serializers.ValidationError(
                "A pleasant habit cannot have a related habit or a reward."
            )

        if related_habit and not getattr(related_habit, "is_pleasant", False):
            raise serializers.ValidationError("Related habit must be a pleasant habit.")

        return data
