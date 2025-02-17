from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Task, Notifications
from .serializers import TaskSerializer, NotificationSerializer
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .tasks import send_notification, send_task_reminder
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only admin users to create and delete tasks.
    Normal users can only read the data.
    """

    def has_permission(self, request, view):
        # Allow GET, HEAD, and OPTIONS requests for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow all actions if the user is an admin
        return request.user.is_staff

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [DjangoModelPermissions]
    queryset = Task.objects.none()

    def get_queryset(self):
        """
        - Admin users can access all tasks.
        - Normal users can only access tasks assigned to them.
        """
        user = self.request.user

        if user.is_staff:
            return Task.objects.all()  # Admins see all tasks

        return Task.objects.filter(assigned_user=user)  # Normal users see only their tasks

    def get_permissions(self):
        """
        - Allow all actions for admins.
        - Restrict create and delete for normal users.
        """
        if self.action in ['create', 'destroy']:
            return [IsAdminOrReadOnly()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


    def create(self, request, *args, **kwargs):
        """
        Override create method to return a structured response.
        """
        if not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to create tasks.")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validation handled in the serializer

        self.perform_create(serializer)
        task = serializer.instance

        # Trigger notification if the task is assigned to a user
        if task.assigned_user:
            try:
                # Send immediate notification to the user
                message = f"You have been assigned a new task: '{task.title}'."
                send_notification.delay(task.assigned_user.id, message)  # Trigger Celery task for notification

                # Create periodic task for reminders
                schedule, created = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.MINUTES)
                periodic_task = PeriodicTask.objects.create(
                    interval=schedule,
                    name=f"send_task_reminder_{task.id}",
                    task='tasks.tasks.send_task_reminder',
                    args=f'["{task.id}"]',  # Pass the task id as argument
                )
            except Exception as e:
                # Log the exception or handle it as needed
                print(f"Failed to send notification: {e}")  

        return Response(
            {
                "status": status.HTTP_201_CREATED,
                "message": "Task created successfully.",
                "data": serializer.data,
                "error": {}
            },
            status=status.HTTP_201_CREATED
        )


    def destroy(self, request, *args, **kwargs):
        """
        Restrict task deletion to admin users only.
        """
        if not request.user.is_staff:
            return Response(
                {
                    "status": status.HTTP_403_FORBIDDEN,
                    "message": "You do not have permission to delete tasks.",
                    "data": {},
                    "error": {"detail": "Permission denied"}
                },
                status=status.HTTP_403_FORBIDDEN
            )

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "Task deleted successfully.",
                "data": {},
                "error": {}
            },
            status=status.HTTP_200_OK
        )

class ChangeTaskStatus(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request, *args, **kwargs):
        task_id = request.data.get("task_id")  
        new_status = request.data.get("status")

        if not task_id:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Task id is required.",
                    "data": {},
                    "error": {"task_id": "Task id is required."}
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate status choices
        valid_statuses = ["Pending", "In Progress", "Completed"]
        if new_status not in valid_statuses:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid status value.",
                    "data": {},
                    "error": {"detail": f"Allowed values: {valid_statuses}"}
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the task or return 404 if not found
        task = get_object_or_404(Task, id=task_id)

        # Ensure the user is assigned to the task
        if task.assigned_user != request.user:
            return Response(
                {
                    "status": status.HTTP_403_FORBIDDEN,
                    "message": "You can only change the status of your assigned tasks.",
                    "data": {},
                    "error": {"detail": "Permission denied"}
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Update the task status
        task.status = new_status
        task.save()

        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "Task status updated successfully.",
                "data": {"task_id": task.id, "new_status": task.status},
                "error": {}
            },
            status=status.HTTP_200_OK
        )

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.none()

    def get_queryset(self):
        return Notifications.objects.filter(user=self.request.user, is_read=False)