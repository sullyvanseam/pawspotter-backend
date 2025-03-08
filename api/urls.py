from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DogReportViewSet, RegisterView, LoginView, LogoutView, DogStatusViewSet, CommentViewSet


router = DefaultRouter()
router.register(r'dogs', DogReportViewSet)  # Creates routes for all CRUD operations
router.register(r'status', DogStatusViewSet)  # API for dog statuses
router.register(r'comments', CommentViewSet, basename="comments")   # API for comments

urlpatterns = [
    path('', include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]