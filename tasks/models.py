from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Task(models.Model):

    STATUS_CHOICE=[
        ('Pending','Pending'),
        ('In Progress','In Progress'),
        ('Completed','Completed'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(choices=STATUS_CHOICE, default='Pending')
    assigned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="task_user")
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_user")
    due_date = models.DateField()


class Notifications(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message