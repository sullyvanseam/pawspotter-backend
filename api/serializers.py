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
    class Meta:
        model = DogReport
        fields = '__all__'

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


class DogStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DogStatus
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'dog_report', 'user', 'text', 'created_at']
        read_only_fields = ['created_at', 'user']

    def get_user(self, obj):
        """Return the username or 'Anonymous' if no user is attached"""
        return obj.user.username if obj.user else "Anonymous"