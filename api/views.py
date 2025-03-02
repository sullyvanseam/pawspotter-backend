from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, permissions, generics, status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import DogReport, DogStatus, Comment
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    DogReportSerializer,
    DogStatusSerializer,
    CommentSerializer,
)


# ------------------------------
# User Authentication Views
# ------------------------------

class RegisterView(generics.CreateAPIView):
    """
    API view for user registration.
    Allows new users to create an account.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]  # Publicly accessible


class LoginView(generics.GenericAPIView):
    """
    API view for user login.
    Authenticates users and returns user data if successful.
    """
    permission_classes = [AllowAny]  # Publicly accessible

    def post(self, request):
        """
        Handles user authentication and login.
        """
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return Response(
                {"message": "Login successful", "user": UserSerializer(user).data},
                status=status.HTTP_200_OK,
            )
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.GenericAPIView):
    """
    API view for user logout.
    Logs out the currently authenticated user.
    """
    permission_classes = [IsAuthenticated]  # Only logged-in users can log out

    def post(self, request):
        """
        Handles user logout.
        """
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


# ------------------------------
# Dog Report API View
# ------------------------------

class DogReportViewSet(viewsets.ModelViewSet):
    """
    API view for managing dog reports.
    Allows users to create, view, update, and delete reports.
    """
    queryset = DogReport.objects.all().order_by('-created_at')  # Newest reports first
    serializer_class = DogReportSerializer
    permission_classes = [permissions.AllowAny]  # Public access
    parser_classes = (MultiPartParser, FormParser)  # Allows file uploads

    # Enable filtering in API requests
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['condition', 'user', 'created_at']

    def perform_create(self, serializer):
        """
        Assigns the report to the authenticated user if logged in.
        Otherwise, allows anonymous users to submit reports.
        """
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save(user=None)  # Allows anonymous reporting


# ------------------------------
# Dog Status API View
# ------------------------------

class DogStatusViewSet(viewsets.ModelViewSet):
    """
    API view for managing dog statuses.
    Tracks vaccination, rescue status, and additional notes.
    """
    queryset = DogStatus.objects.all()
    serializer_class = DogStatusSerializer

    def perform_create(self, serializer):
        """
        Ensures that each dog report has only one status.
        """
        dog_report = serializer.validated_data.get("dog_report")

        if DogStatus.objects.filter(dog_report=dog_report).exists():
            return Response(
                {"error": "Status already exists for this dog report."},
                status=400
            )

        serializer.save()


# ------------------------------
# Comment API View
# ------------------------------

class CommentViewSet(viewsets.ModelViewSet):
    """
    API view for managing comments on dog reports.
    Users (or anonymous) can leave comments related to a report.
    """
    queryset = Comment.objects.all().order_by('-created_at')  # Sort comments by newest first
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]  # Allows both logged-in & anonymous users

    def perform_create(self, serializer):
        """
        Assigns the comment to the authenticated user if logged in.
        Otherwise, allows anonymous users to submit comments.
        """
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save(user=None)  # Allows anonymous comments