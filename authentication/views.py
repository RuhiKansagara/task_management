from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import RegistrationSerializer, LoginSerializer
from django.contrib.auth.models import User
from django.http import JsonResponse


def check_server(request):
    """
    A simple view to verify that the server is working.
    """
    response_data = {
        "status": "ok",
        "message": "API is working"
    }
    return JsonResponse(response_data)

class UserRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "status": status.HTTP_201_CREATED,
                    "message": "User registered successfully",
                    "data": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    },
                    "error": {}
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Registration failed",
                "data": {},
                "error": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data.get("user")
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Login successful",
                    "data": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "access_token": str(refresh.access_token),
                        "refresh_token": str(refresh),
                    },
                    "error": {}
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Login failed",
                "data": {},
                "error": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")

            if not refresh_token:
                return Response(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Refresh token is required.",
                        "data": {},
                        "error": {"refresh_token": ["Refresh token is required."]}
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Logged out successfully.",
                    "data": {},
                    "error": {}
                },
                status=status.HTTP_200_OK
            )

        except Exception:
            raise PermissionDenied("Session expired. Please log in again.")

class RetrieveUsers(APIView):

    authentication_classes =[JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        
        users = User.objects.exclude(is_staff=True)  # Exclude admin users

        user_data = [{"id": user.id, "email": user.email} for user in users]  # Prepare user data

        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "Users retrieved successfully.",
                "data": user_data,  # Return the list of users
                "error": {}
            },
            status=status.HTTP_200_OK
        )