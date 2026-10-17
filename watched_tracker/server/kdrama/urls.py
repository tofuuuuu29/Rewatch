from django.urls import path
from kdrama.views import KdramaListCreateView, KdramaDetailView

urlpatterns = [
    path('', KdramaListCreateView.as_view(), name='kdrama-list'),
    path('<int:pk>/', KdramaDetailView.as_view(), name='kdrama-detail'),
]