from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Task, Notifications
from django_celery_beat.models import PeriodicTask
import logging


logger = logging.getLogger("django.test")

User = get_user_model()

class TaskTests(APITestCase):
    def setUp(self):
        """Set up users and tasks before each test"""
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.normal_user = User.objects.create_user(
            username="user", email="user@example.com", password="userpass"
        )
        
        self.task = Task.objects.create(
            title="Sample Task",
            description="Test Task Description",
            assigned_user=self.normal_user,
            assigned_by=self.admin_user,
            status="Pending",
            due_date="2025-02-18"
        )

    def test_admin_can_create_task(self):
        """Ensure admin can create a task"""
        self.client.force_authenticate(user=self.admin_user)
        url = "/api/tasks/"
        data = {
            "title": "New Task",
            "description": "Test Description",
            "assigned_user": self.normal_user.id,
            "due_date":"2025-02-18",
        }
        response = self.client.post(url, data, format="json")
        logger.debug(f"Test: Admin Can Create Task | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_missing_fields(self):
        """Test create task with missing fields"""
        self.client.force_authenticate(user=self.admin_user)
        url = "/api/tasks/"
        data = {
            "title": "New Task",
            "description": "Test Description",
            "assigned_user": self.normal_user.id,
            "due_date":"",
        }
        response = self.client.post(url, data, format="json")
        logger.debug(f"Test: Task Creation Failure with missing fields | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_normal_user_cannot_create_task(self):
        """Ensure normal users cannot create tasks"""
        self.client.force_authenticate(user=self.normal_user)
        url = "/api/tasks/"
        data = {
            "title": "Unauthorized Task",
            "description": "Should not be allowed"
        }
        response = self.client.post(url, data, format="json")
        logger.debug(f"Test: Normal User Cannot Create Task | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_task(self):
        """Ensure admin can delete tasks"""
        self.client.force_authenticate(user=self.admin_user)
        url = f"/api/tasks/{self.task.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        logger.debug(f"Test: Admin Can Delete Task | Status: {response.status_code}")
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_normal_user_cannot_delete_task(self):
        """Ensure normal users cannot delete tasks"""
        self.client.force_authenticate(user=self.normal_user)
        url = f"/api/tasks/{self.task.id}/"
        response = self.client.delete(url)
        logger.debug(f"Test: Normal User Cannot Delete Task | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_user_can_view_assigned_tasks(self):
        """Ensure normal users can only see their assigned tasks"""
        self.client.force_authenticate(user=self.normal_user)
        url = "/api/tasks/"
        response = self.client.get(url)
        logger.debug(f"Test: Normal User Can View Assigned Tasks | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_view_all_tasks(self):
        """Ensure admin can view all tasks"""
        self.client.force_authenticate(user=self.admin_user)
        url = "/api/tasks/"
        response = self.client.get(url)
        logger.debug(f"Test: Admin Can View All Tasks | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
class ChangeTaskStatusTests(APITestCase):
    def setUp(self):
        """Set up users and a task"""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass")
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.task = Task.objects.create(
            title="Test Task",
            description="Change status",
            assigned_user=self.user,
            assigned_by=self.admin_user,
            status="Pending",
            due_date="2025-02-18"
        )
        self.url = "/api/task/change-status/"

    def test_assigned_user_can_change_status(self):
        """Ensure only assigned user can change task status"""
        self.client.force_authenticate(user=self.user)
        data = {"task_id": self.task.id, "status": "Completed"}
        response = self.client.post(self.url, data, format="json")
        logger.debug(f"Test: Assigned User Can Change Status | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "Completed")
    
    def test_other_user_cannot_change_status(self):
        """Ensure other user cannot change task status"""
        self.client.force_authenticate(user=self.other_user)
        data= {"task_id":self.task.id, "status": "In Progress"}
        response = self.client.post(self.url, data, format="json")
        logger.debug(f"Test: Other User Cannot Change Status | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_missing_task_id(self):
        """Ensure missing task id"""
        self.client.force_authenticate(user=self.user)
        data = {"status": "Completed"}
        response = self.client.post(self.url, data, format="json")
        logger.debug(f"Test: Missing Task ID | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_other_status_value(self):
        """Ensure other status is not accepted"""
        self.client.force_authenticate(user=self.user)
        data = {"task_id":self.task.id, "status":"UnknownStatus"}
        response = self.client.post(self.url, data, format="json")
        logger.debug(f"Test: Other Status Value Not Accepted | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class NotificationTests(APITestCase):
    def setUp(self):
        """Set up users and notifications"""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.notification = Notifications.objects.create(
            user=self.user,
            message="You have a new task assigned.",
            is_read=False
        )
        self.url = "/api/notifications/"

    def test_user_can_fetch_notifications(self):
        """Ensure user can fetch unread notifications"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        logger.debug(f"Test: User Can Fetch Notifications | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_cannot_fetch_other_users_notifications(self):
        """Ensure user cannot see another user's notifications"""
        other_user = User.objects.create_user(username="otheruser", password="testpass")
        self.client.force_authenticate(user=other_user)
        response = self.client.get(self.url)
        logger.debug(f"Test: User Cannot Fetch Other User's Notifications | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
