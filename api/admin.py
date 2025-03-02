from django.contrib import admin
from .models import DogReport, DogStatus

@admin.register(DogReport)
class DogReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'condition', 'latitude', 'longitude', 'location', 'created_at')  # Columns in the admin panel
    search_fields = ('condition', 'user__username', 'location')  # Enable search
    list_filter = ('condition', 'created_at')  # Add filters

@admin.register(DogStatus)
class DogStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'dog_report', 'vaccinated', 'rescued', 'updated_at')  # Display fields in admin panel
    list_filter = ('vaccinated', 'rescued', 'updated_at')  # Add filters
    search_fields = ('dog_report__id', 'additional_notes')  # Search by DogReport ID and notes