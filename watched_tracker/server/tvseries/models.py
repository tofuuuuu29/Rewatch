from django.conf import settings
from django.db import models
from config.choices import STATUS_CHOICES, STATUS_WATCHING


class TvSeries(models.Model):
    tv_series = models.CharField(max_length=255)
    season = models.IntegerField(null=True, blank=True)
    episode = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_WATCHING
    )
    # picture shown on the card (filled in when a title is picked from the online search)
    poster_url = models.URLField(max_length=500, blank=True, default='')

    # every title belongs to the user who added it
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.tv_series

    class Meta:
        db_table = 'tv_series'