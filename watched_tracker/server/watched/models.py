from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from type.models import Type


class WatchEntry(models.Model):
    """One user's record of one title: status, rating, progress and notes."""

    STATUS_CHOICES = [
        ('watching', 'Watching'),
        ('completed', 'Completed'),
        ('plan_to_watch', 'Plan to watch'),
        ('dropped', 'Dropped'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='watched',
        db_column='user_id'
    )

    # the title (anime / movie / kdrama / tv series) is reached through the Type table
    type = models.ForeignKey(
        Type,
        on_delete=models.CASCADE,
        db_column='type_id'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='plan_to_watch'
    )
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    season = models.PositiveIntegerField(null=True, blank=True)
    episode = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    date_started = models.DateField(null=True, blank=True)
    date_finished = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'watched'
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'type'], name='unique_user_type')
        ]

    def __str__(self):
        return f"{self.user} - {self.type} ({self.status})"
