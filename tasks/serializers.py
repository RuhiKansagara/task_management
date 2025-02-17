from rest_framework import serializers
from .models import Task, Notifications

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'assigned_user', 'assigned_by', 'due_date']
        extra_kwargs = {'assigned_by': {'read_only': True}}

    def validate(self, data):
        """
        Ensure that no task with the same title exists for the same user.
        """
        assigned_user = data.get("assigned_user")
        task_title = data.get("title")

        if Task.objects.filter(title=task_title, assigned_user=assigned_user).exists():
            raise serializers.ValidationError(
                {"title": "A task with the same title already exists for this user."}
            )

        return data

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = ['id', 'message', 'created_at', 'is_read']
        read_only_fields = ['id', 'created_at']