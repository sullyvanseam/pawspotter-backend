import requests
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import DogReport, DogStatus, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        # Hashes password automatically
        user = User.objects.create_user(**validated_data)
        return user


class DogReportSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()  # Ensure image URL is returned

    class Meta:
        model = DogReport
        fields = '__all__'

    def get_image(self, obj):
        """ Returns the full URL for the image """
        if obj.image:
            return obj.image.url
        return None

    def create(self, validated_data):
        """ Automatically fetch location name from coordinates before saving """
        latitude = validated_data.get("latitude")
        longitude = validated_data.get("longitude")

        if latitude and longitude:
            validated_data["location"] = self.get_location_from_coordinates(latitude, longitude)

        return DogReport.objects.create(**validated_data)

    def get_location_from_coordinates(self, latitude, longitude):
        """ Reverse geocode coordinates to fetch city/region """
        try:
            response = requests.get(
                f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json"
            )
            data = response.json()
            return data.get("address", {}).get("city") or \
                   data.get("address", {}).get("town") or \
                   data.get("address", {}).get("village") or \
                   data.get("address", {}).get("state", "Unknown Location")
        except Exception as e:
            print(f"Error fetching location: {e}")
        


class DogStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DogStatus
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
