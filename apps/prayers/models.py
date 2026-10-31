from django.db import models
from django.conf import settings
import uuid

class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Prayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CATEGORY_CHOICES = [
        ('GENERAL', 'General'),
        ('ANXIETY_FEAR', 'Anxiety & Fear'),
        ('HEALTH', 'Health'),
        ('FINANCE', 'Finance'),
        ('RELATIONSHIP', 'Relationship'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('ASSIGNED', 'Assigned'),
        ('ON_PROGRESS', 'On Progress'),
        ('COMPLETED', 'Completed'),
    ]

    # Name of the person asking for prayer
    title = models.CharField(max_length=255)
    email = models.EmailField()
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='GENERAL')
    is_anonymous = models.BooleanField(default=False)
    share_first_name = models.BooleanField(default=True)
    wants_follow_up = models.BooleanField(default=False)
    # The language of the page the request came from, for the email back,
    # and where the phone was, for its crisis line (blank if unknown).
    lang = models.CharField(max_length=2, default='en')
    country = models.CharField(max_length=2, blank=True, default='')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    
    # Optional link to an organization
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prayers'
    )
    
    # The carrier assigned to this prayer
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_prayers'
    )
    
    # If the user was logged in when submitting (optional)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prayers'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.category} ({self.status})"

class PrayerResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prayer = models.ForeignKey(Prayer, on_delete=models.CASCADE, related_name='responses')
    content = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.prayer.id} by {self.user.email}"
