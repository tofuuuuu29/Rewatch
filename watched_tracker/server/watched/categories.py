from anime.models import Anime
from kdrama.models import Kdrama
from movies.models import Movie
from tvseries.models import TvSeries

# category key (used by the API) -> the model, the column on the Type table, and the title column
CATEGORIES = {
    'anime': {'model': Anime, 'field': 'anime', 'name': 'anime_name'},
    'movies': {'model': Movie, 'field': 'movie', 'name': 'movie_name'},
    'kdrama': {'model': Kdrama, 'field': 'kdrama', 'name': 'kdrama_name'},
    'tvseries': {'model': TvSeries, 'field': 'tv_series', 'name': 'tv_series'},
}


def category_of(type_obj):
    """Which category (anime / movies / kdrama / tvseries) a Type row points to."""
    for key, cfg in CATEGORIES.items():
        if getattr(type_obj, f"{cfg['field']}_id") is not None:
            return key
    return None
