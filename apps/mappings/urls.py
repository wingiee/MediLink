from django.urls import path

from .views import MappingDetailView, MappingListCreateView

urlpatterns = [
    path("mappings/", MappingListCreateView.as_view(), name="mapping-list"),
    path("mappings/<int:pk>/", MappingDetailView.as_view(), name="mapping-detail"),
]
