from django.urls import path, include
from rest_framework.routers import DefaultRouter
from authentication.views import UserRegistrationView, LoginView, LogoutView, RetrieveUsers
from tasks.views import TaskViewSet, ChangeTaskStatus, NotificationViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("user/register/", UserRegistrationView.as_view(), name="user_register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("user/details/",RetrieveUsers.as_view(),name="user_details"),
    path('', include(router.urls)),
    path("task/change-status/", ChangeTaskStatus.as_view(), name="change_task_status"),
]