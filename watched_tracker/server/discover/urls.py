from django.urls import path

from discover.views import DiscoverView, TrendingView

urlpatterns = [
    path('', DiscoverView.as_view(), name='discover'),
    path('trending/', TrendingView.as_view(), name='discover-trending'),
]