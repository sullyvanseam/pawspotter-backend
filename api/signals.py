from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DogReport, DogStatus

@receiver(post_save, sender=DogReport)
def create_dog_status(sender, instance, created, **kwargs):
    if created:
        DogStatus.objects.create(dog_report=instance)
