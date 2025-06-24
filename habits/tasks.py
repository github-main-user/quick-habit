from celery import shared_task
from django.utils import timezone
from requests.exceptions import RequestException

from .models import Habit, HabitNotification
from .services import send_telegram_message


@shared_task
def check_habits() -> None:
    """
    Checks which habits are scheduled for now or earlier today,
    sends reminders to their owners if not already sent.
    """

    now = timezone.now()
    habits = Habit.objects.filter(time__le=now.time())

    for habit in habits:
        last_notification = habit.notifications.order_by("-date").first()

        if last_notification:
            days_since_last = (now.date() - last_notification.date).days
            if days_since_last < habit.frequency:
                continue

        chat_id = habit.owner.chat_id
        if not chat_id:
            continue

        message = (
            "🔔 Habit Reminder!\n"
            f"Hey, it’s time to: {habit.action} at {habit.time} in {habit.place}.\n"
            f"⏳ You have {habit.execution_time} seconds to make it."
        )

        try:
            send_telegram_message(chat_id, message)
        except RequestException:
            pass
        else:
            HabitNotification.objects.create(habit=habit, date=now.date())
