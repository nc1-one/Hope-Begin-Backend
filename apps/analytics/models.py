from django.db import models

class ExternalClick(models.Model):
    link_name = models.CharField(max_length=255, unique=True)
    clicks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.link_name}: {self.clicks}"


class DailyClick(models.Model):
    """
    The same counts per day (Manila date), so the admin dashboard can show a
    date range. No visitor details are stored, only the event name and count.
    """

    link_name = models.CharField(max_length=80)
    date = models.DateField()
    count = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['link_name', 'date'], name='unique_daily_click'),
        ]
        indexes = [models.Index(fields=['date'])]

    def __str__(self):
        return f"{self.date} {self.link_name}: {self.count}"
