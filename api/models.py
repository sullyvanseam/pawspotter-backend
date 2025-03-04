import os
import uuid
from django.db import models
from django.contrib.auth.models import User

def unique_filename(instance, filename):
    """Generates a unique filename for uploaded images"""
    ext = filename.split('.')[-1] 
    unique_name = f"{uuid.uuid4().hex}.{ext}"  
    return os.path.join("dog_reports/", unique_name) 


class DogReport(models.Model):
    """
    Stores reports of stray dogs, including location, condition, and optional images.
    Reports can be submitted by both logged-in users and anonymous users.
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = models.CharField(max_length=255, blank=True, null=True)  
    condition = models.CharField(
        max_length=20,
        choices=[
            ('Healthy', 'Healthy'),
            ('Injured', 'Injured'),
            ('Lost', 'Lost'),
        ]
    )
    image = models.ImageField(upload_to=unique_filename, blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.condition} dog spotted at ({self.latitude}, {self.longitude})"


class DogStatus(models.Model):
    """
    Stores additional status information about a dog report.
    Tracks whether the dog has been vaccinated or rescued.
    """
    dog_report = models.OneToOneField(DogReport, on_delete=models.CASCADE, related_name="status")  # One-to-One Relationship
    vaccinated = models.BooleanField(default=False)  
    rescued = models.BooleanField(default=False)  
    additional_notes = models.TextField(blank=True, null=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"Status for DogReport {self.dog_report.id}"



class Comment(models.Model):
    """
    Stores comments related to a specific dog report.
    Users (or anonymous) can leave comments to provide more details about a reported dog.
    """
    dog_report = models.ForeignKey(DogReport, on_delete=models.CASCADE, related_name="comments")  
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    text = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Comment by {self.user.username if self.user else 'Anonymous'} on Report {self.dog_report.id}"