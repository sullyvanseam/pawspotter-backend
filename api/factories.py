import factory
from django.contrib.auth.models import User
from .models import DogReport, DogStatus, Comment


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating test users.
    """
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
    password = factory.PostGenerationMethodCall("set_password", "testpassword")


class DogReportFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating test dog reports.
    """
    class Meta:
        model = DogReport

    user = factory.SubFactory(UserFactory)  # Creates a user for the report
    latitude = -8.65
    longitude = 115.22
    location = "Bali, Indonesia"
    condition = factory.Iterator(["Healthy", "Injured", "Lost"])
    created_at = factory.Faker("date_time_this_year")


class DogStatusFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating test dog statuses.
    """
    class Meta:
        model = DogStatus

    dog_report = factory.SubFactory(DogReportFactory)  # Links to a dog report
    vaccinated = factory.Faker("boolean")
    rescued = factory.Faker("boolean")
    additional_notes = factory.Faker("sentence")
    updated_at = factory.Faker("date_time_this_year")


class CommentFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating test comments.
    """
    class Meta:
        model = Comment

    dog_report = factory.SubFactory(DogReportFactory)  # Links to a dog report
    user = factory.SubFactory(UserFactory)
    text = factory.Faker("sentence")
    created_at = factory.Faker("date_time_this_year")