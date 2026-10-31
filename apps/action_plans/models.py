from django.db import models


class PlanCheckIn(models.Model):
    """
    One email, a week after someone makes a plan, asking how they are doing.
    The address and name are cleared once the email is sent, so only the
    dates remain.
    """

    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=60, blank=True)
    lang = models.CharField(max_length=2, default='en')
    # Where the visitor's phone was, for their crisis line; blank if unknown.
    country = models.CharField(max_length=2, blank=True, default='')
    send_on = models.DateField()
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['sent_at', 'send_on'])]

    def __str__(self):
        return f'Plan check-in for {self.send_on}'
