from django.db import models
from django.utils import timezone


class Holiday(models.Model):
    """Model representing a holiday or special date."""
    name = models.CharField(max_length=100)
    date = models.DateField()
    is_closed = models.BooleanField(default=False)
    artwork_path = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.date})"


class CalendarGeneration(models.Model):
    """Model representing a calendar generation job."""
    ROOM_CHOICES = [
        ('study', 'Study Room'),
        ('program', 'Program Room'),
    ]

    MONTH_CHOICES = [
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]

    room_type = models.CharField(max_length=10, choices=ROOM_CHOICES)
    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    pdf_file = models.FileField(upload_to='calendars/', blank=True, null=True)

    def __str__(self):
        month_name = dict(self.MONTH_CHOICES)[self.month]
        room_type_name = dict(self.ROOM_CHOICES)[self.room_type]
        return f"{room_type_name} Calendar - {month_name} {self.year}"
