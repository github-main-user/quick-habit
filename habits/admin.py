from django.contrib import admin

from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = [
        "owner",
        "place",
        "time",
        "action",
        "is_pleasant",
        "execution_time",
        "is_public",
    ]
    list_filter = ["owner", "is_pleasant", "is_public"]
    search_fields = ["place", "time", "action"]
