from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ROLE_CHOICES = (
        ('admin', 'Super admin'),
        ('staff', 'Admin, no financials'),
        ('carrier', 'Carrier'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    email = models.EmailField(unique=True)
    is_approved = models.BooleanField(default=False)

    # Carrier specific fields
    phone = models.CharField(max_length=20, null=True, blank=True)
    church_community = models.CharField(max_length=255, null=True, blank=True)
    carrier_reason = models.TextField(null=True, blank=True)
    agreed_to_guidelines = models.BooleanField(default=False)

    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
