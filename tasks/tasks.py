from celery import shared_task
from datetime import datetime, time
from django.utils import timezone
from .models import Notifications, Task
from django.contrib.auth.models import User

@shared_task
def send_notification(user_id, message):
    try:
        user = User.objects.get(id=user_id)
        Notifications.objects.create(user=user, message=message)
        print(f"Notification sent to user {user_id}: {message}")
    except Exception as e:
        print(f"Failed to send notification: {e}")

@shared_task
def send_task_reminder(task_id):
    """
    Sends a reminder to the user every 5 minutes until the task is marked as done or the due date is reached.
    """
    task = Task.objects.get(id=task_id)

    due_datetime = datetime.combine(task.due_date, time(23, 59, 59), tzinfo=timezone.get_current_timezone())
    
    # Check if the task is completed or due date has passed
    if task.status != 'Completed' and due_datetime > timezone.now():
        if task.assigned_user:
            Notifications.objects.create(
                user=task.assigned_user,
                message=f'Reminder: Please complete the task: {task.title}. The due date is {task.due_date}.'
            )

