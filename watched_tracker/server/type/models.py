from django.db import models
from anime.models import Anime
from movies.models import Movie
from kdrama.models import Kdrama
from tvseries.models import TvSeries


class Type(models.Model):
    anime = models.ForeignKey(
        Anime,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='anime_id'
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='movie_id'
    )

    tv_series = models.ForeignKey(
        TvSeries,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='tv_series_id'
    )

    kdrama = models.ForeignKey(
        Kdrama,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='kdrama_id'
    )

    class Meta:
        db_table = 'type'

    def __str__(self):
        return f"Type {self.id}"