from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, permissions, generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken


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
    Allows new users to create an account and receive a JWT token.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]  # Publicly accessible

    def post(self, request):
        """
        Handles user registration and returns JWT tokens.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate JWT token for the new user
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "Registration successful",
                    "user": UserSerializer(user).data,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh)
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    """
    API view for user login.
    Authenticates users and returns user data with JWT token if successful.
    """
    permission_classes = [AllowAny] 

    def post(self, request):
        """
        Handles user authentication and login.
        """
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)  # Generate JWT tokens
            return Response(
                {
                    "message": "Login successful",
                    "user": UserSerializer(user).data,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh)
                },
                status=status.HTTP_200_OK,
            )
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.GenericAPIView):
    """
    API view for user logout.
    In a token-based system, logout is handled on the frontend by deleting tokens.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        The frontend should delete the stored token upon logout.
        """
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


# ------------------------------
# Dog Report API View
# ------------------------------

class DogReportViewSet(viewsets.ModelViewSet):
    """
    API view for managing dog reports.
    Allows users to create, view, update, and delete reports.
    """
    queryset = DogReport.objects.all().order_by('-created_at')
    serializer_class = DogReportSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['condition', 'user', 'created_at']

    def perform_create(self, serializer):
        """
        Assigns the report to the authenticated user if logged in.
        Otherwise, assigns the user from request data.
        """
        user = None

        if self.request.user.is_authenticated:
            user = self.request.user
        else:
            user_id = self.request.data.get("user")  # Get user ID from request body
            if user_id:
                try:
                    user = User.objects.get(id=user_id)  # Fetch user from DB
                except User.DoesNotExist:
                    return Response({"error": "User not found."}, status=400)

        serializer.save(user=user)  # Save report with user (or None if anonymous)


# ------------------------------
# Dog Status API View
# ------------------------------

class DogStatusViewSet(viewsets.ModelViewSet):
    """
    API view for managing dog statuses.
    """
    queryset = DogStatus.objects.all()
    serializer_class = DogStatusSerializer

    def perform_create(self, serializer):
        """
        Ensures that each dog report has only one status.
        """
        dog_report = serializer.validated_data.get("dog_report")

        if DogStatus.objects.filter(dog_report=dog_report).exists():
            raise ValidationError({"error": "Status already exists for this dog report."})


# ------------------------------
# User Comments API View
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