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
        user = User.objects.create_user(**validated_data)  # Hashes password automatically
        return user
    
class DogReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DogReport
        fields = '__all__' 

class DogStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DogStatus
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__' 