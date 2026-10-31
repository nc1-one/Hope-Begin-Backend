from django.db import models
import uuid

class HopeJourney(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    # No longer asked for; older sign-ups may have one.
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)
    current_day = models.IntegerField(default=1)
    # The language the emails are written in, and where the visitor's phone
    # was, for their crisis line (blank if unknown).
    lang = models.CharField(max_length=2, default='en')
    country = models.CharField(max_length=2, blank=True, default='')
    is_active = models.BooleanField(default=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Hope Journey"
        verbose_name_plural = "Hope Journeys"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - Day {self.current_day}"


class HopefulBeginningCompletion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Hopeful Beginning Completion"
        verbose_name_plural = "Hopeful Beginning Completions"

    def __str__(self):
        return f"Completion {self.id} at {self.created_at}"


class EmailTemplate(models.Model):
    day_number = models.IntegerField(unique=True)
    subject = models.CharField(max_length=255)
    html_content = models.TextField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['day_number']
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"

    def __str__(self):
        return f"Day {self.day_number}: {self.subject}"
