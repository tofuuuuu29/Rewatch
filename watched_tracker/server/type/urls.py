from django.urls import path
from type.views import TypeListCreateView, TypeDetailView

urlpatterns = [
    path('', TypeListCreateView.as_view(), name='type-list'),
    path('<int:pk>/', TypeDetailView.as_view(), name='type-detail'),
]