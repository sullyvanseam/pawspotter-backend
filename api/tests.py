from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import DogReport, DogStatus, Comment
from .factories import UserFactory, DogReportFactory, DogStatusFactory, CommentFactory


class DogReportTests(APITestCase):
    """
    Tests for dog reports using Factory Boy.
    """

    def setUp(self):
        """Set up test data using factories."""
        self.user = UserFactory()
        self.dog_report = DogReportFactory(user=self.user)

    def test_create_dog_report(self):
        """Ensure a user can create a dog report."""
        self.client.force_authenticate(user=self.user)
        data = {
            "latitude": -8.65,
            "longitude": 115.22,
            "condition": "Injured"
        }
        response = self.client.post("/api/dogs/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fetch_all_dog_reports(self):
        """Ensure the API returns all dog reports."""
        DogReportFactory.create_batch(5)  # Generate 5 test reports
        response = self.client.get("/api/dogs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 5)


class DogStatusTests(APITestCase):
    """
    Tests for dog statuses using Factory Boy.
    """

    def setUp(self):
        """Set up test data using factories."""
        self.dog_report = DogReportFactory()
        self.dog_status = DogStatusFactory(dog_report=self.dog_report)

    def test_create_dog_status(self):
        """Ensure a status can be created for a dog report."""
        DogStatus.objects.filter(dog_report=self.dog_report).delete() # Ensure one status exists
        data = {"dog_report": self.dog_report.id,
                "vaccinated": True, "rescued": False}
        response = self.client.post("/api/status/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CommentTests(APITestCase):
    """
    Tests for comments using Factory Boy.
    """

    def setUp(self):
        """Set up test data using factories."""
        self.dog_report = DogReportFactory()
        self.comment = CommentFactory(dog_report=self.dog_report)

    def test_create_comment(self):
        """Ensure a comment can be added to a dog report."""
        data = {"dog_report": self.dog_report.id,
                "text": "This dog needs help!"}
        response = self.client.post("/api/comments/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
