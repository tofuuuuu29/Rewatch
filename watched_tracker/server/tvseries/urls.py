from django.urls import path
from tvseries.views import TvSeriesListCreateView, TvSeriesDetailView

urlpatterns = [
    path('', TvSeriesListCreateView.as_view(), name='tv-series-list'),
    path('<int:pk>/', TvSeriesDetailView.as_view(), name='tv-series-detail'),
]