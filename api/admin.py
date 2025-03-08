from django.contrib import admin
from .models import DogReport, DogStatus, Comment


@admin.register(DogReport)
class DogReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'condition', 'latitude', 'longitude',
                    'location', 'created_at')  # Columns in the admin panel
    search_fields = ('condition', 'user__username',
                     'location')  # Enable search
    list_filter = ('condition', 'created_at')  # Add filters


@admin.register(DogStatus)
class DogStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'dog_report', 'vaccinated', 'rescued',
                    'updated_at')  # Display fields in admin panel
    list_filter = ('vaccinated', 'rescued', 'updated_at')  # Add filters
    # Search by DogReport ID and notes
    search_fields = ('dog_report__id', 'additional_notes')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'dog_report', 'user', 'text',
                    'created_at')  # Show in list view
    search_fields = ('user__username', 'text',
                     'dog_report__id')  # Enable search
    list_filter = ('created_at',)  # Add filtering options
