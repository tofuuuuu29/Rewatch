from django.urls import path
from anime.views import AnimeListCreateView, AnimeDetailView

urlpatterns = [
    path('', AnimeListCreateView.as_view(), name='anime-list'),
    path('<int:pk>/', AnimeDetailView.as_view(), name='anime-detail'),
]