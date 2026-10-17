from django.urls import path

from watched.views import WatchedListCreateView, WatchedDetailView, WatchedStatsView

urlpatterns = [
    path('', WatchedListCreateView.as_view(), name='watched-list'),
    path('stats/', WatchedStatsView.as_view(), name='watched-stats'),
    path('<int:pk>/', WatchedDetailView.as_view(), name='watched-detail'),
]
