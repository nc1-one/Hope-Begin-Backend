from django.db import models
from django.utils import timezone
import uuid

class Donation(models.Model):
    TYPE_CHOICES = [
        ('ONE_TIME', 'One-Time'),
        ('MONTHLY', 'Monthly'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('MANUAL_BANK', 'Manual Bank Transfer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    covered_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    donation_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='ONE_TIME')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    # The day the gift arrived: today for Stripe, chosen for bank transfers.
    date = models.DateField(default=timezone.localdate)
    
    stripe_session_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - ₱{self.amount} ({self.status})"
