from django.urls import path
from roles.views import RoleListCreateView, RoleDetailView

urlpatterns = [
    path('', RoleListCreateView.as_view(), name='role-list'),
    path('<int:pk>/', RoleDetailView.as_view(), name='role-detail'),
]