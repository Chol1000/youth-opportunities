from django.db import models
from django.utils import timezone

class ServiceRequest(models.Model):
    SERVICE_TYPES = [
        ('mentorship', '1-on-1 Mentorship'),
        ('application', 'Application Guidance'),
        ('interview', 'Interview Preparation'),
        ('profile', 'Profile Optimization'),
        ('tips', 'Tips for Success'),
        ('cv', 'CV/Resume Review'),
        ('advertisement', 'Advertisement'),
        ('event', 'Event Promotion'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    people_count = models.PositiveIntegerField(default=1, help_text="Number of people attending")
    preferred_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    additional_info = models.TextField(blank=True, null=True)
    contact_info = models.CharField(max_length=200, blank=True, null=True)
    
    # For CV Review and Advertisement services
    file_upload = models.FileField(upload_to='service_files/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_service_type_display()} - {self.name}"
