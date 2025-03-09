from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, permissions, generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView



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
    API view to handle user registration.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user": UserSerializer(user).data  # Returns structured user details
            }, status=201)
        return Response(serializer.errors, status=400)
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not email or not password:
            return Response({"error": "All fields are required."}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken."}, status=400)

        user = User.objects.create(
            username=username,
            email=email,
            password= make_password(password)
        )
        token, created = Token.objects.get_or_create(user=user)

        return Response({"token": token.key, "user": {"id": user.id, "username": user.username}}, status=201)


class LoginView(ObtainAuthToken):
    """
    API view to handle user login.
    Returns a token and user details on successful authentication.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])
        user = token.user
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data  # Returns structured user details
        })


class LogoutView(APIView):
    """
    API view to log out a user by deleting their authentication token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()  # Deletes the token from the database
        return Response({"message": "Logged out successfully."}, status=200)


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
        
        return serializer.save()  
    



# ------------------------------
# User Comments API View
# ------------------------------

class CommentViewSet(viewsets.ModelViewSet):
    """
    API view for managing comments on dog reports.
    Users (or anonymous) can leave comments related to a report.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]  # Allows both logged-in & anonymous users

    def get_queryset(self):
        """
        Filters comments by dog_report if provided in query params.
        Otherwise, returns all comments sorted by newest first.
        """
        dog_report_id = self.request.query_params.get('dog_report', None)

        if dog_report_id is not None:
            return Comment.objects.filter(dog_report=dog_report_id).order_by('-created_at')

        return Comment.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        """
        Assigns the comment to the authenticated user if logged in.
        Otherwise, allows anonymous users to submit comments.
        """
        user = self.request.user if self.request.user.is_authenticated else None

        serializer.save(user=user)