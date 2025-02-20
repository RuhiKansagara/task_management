from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
import logging


logger = logging.getLogger("django.test")
# Create your tests here.
class UserRegistrationTestCase(APITestCase):
    def test_user_registration_success(self):
        """Test user registration with valid data"""
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "TestPass123"
        }
        response = self.client.post("/api/user/register/", data)
        logger.debug(f"Test: User Registration Success | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "User registered successfully")

    def test_user_registration_failure(self):
        """Test user registration with missing fields"""
        data = {
            "username": "",
            "email": "invalid@example.com",
            "password": ""
        }
        response = self.client.post("/api/user/register/", data)
        logger.debug(f"Test: User Registration Failure | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

class LoginTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="TestPass123")

    def test_login_success(self):
        """Test login with correct credentials"""
        data = {
            "email": "testuser@example.com",
            "password": "TestPass123"
        }
        response = self.client.post("/api/login/", data)
        logger.debug(f"Test: User Login Success | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data["data"])

    def test_login_failure(self):
        """Test login with incorrect credentials"""
        data = {
            "email": "test@example.com",
            "password": "TestPass123"
        }
        response = self.client.post("/api/login/", data)
        logger.debug(f"Test: User Login Failure | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class LogoutTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="TestPass123")
        self.client.force_authenticate(user=self.user)
        self.refresh_token = str(RefreshToken.for_user(self.user))

    def test_logout_success(self):
        """Test successful logout"""
        data = {"refresh_token": self.refresh_token}
        response = self.client.post("/api/logout/", data)
        logger.debug(f"Test: User Logout Success | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Logged out successfully.")

    def test_logout_without_token(self):
        """Test logout without refresh token"""
        data = {}
        response = self.client.post("/api/logout/", data)
        logger.debug(f"Test: User Logout Failure | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh_token", response.data["error"])

class RetrieveUsersTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username="admin", email="admin@example.com", password="AdminPass123")
        self.normal_user = User.objects.create_user(username="user", email="user@example.com", password="UserPass123")

    def test_retrieve_users_as_admin(self):
        """Test retrieving users as an admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/user/details/")
        logger.debug(f"Test: Retrieve users list Success | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data["data"]) > 0)

    def test_retrieve_users_as_non_admin(self):
        """Test retrieving users as a normal user (should fail)"""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get("/api/user/details/")
        logger.debug(f"Test: Retrieve users list Failure | Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)