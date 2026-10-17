from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path('admin/', admin.site.urls),

    # Users
    path('api/users/', include('users.urls')),

    # Roles
    path('api/roles/', include('roles.urls')),

    # Anime
    path('api/anime/', include('anime.urls')),

    # Movies
    path('api/movies/', include('movies.urls')),

    # K-drama
    path('api/kdrama/', include('kdrama.urls')),

    # TV Series
    path('api/tvseries/', include('tvseries.urls')),

    # Type
    path('api/type/', include('type.urls')),

    # Watched (each user's own watch list)
    path('api/watched/', include('watched.urls')),

    # Online search for titles + posters (TMDB / Jikan)
    path('api/discover/', include('discover.urls')),

    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]