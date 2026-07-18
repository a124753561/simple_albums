from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, AlbumViewSet
from .views_photo import photo_upload, photo_batch, photo_list, photo_update
from .views import dashboard_stats

router = DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"albums", AlbumViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/stats/", dashboard_stats, name="dashboard-stats"),
    path("albums/<int:album_id>/photos/", photo_list, name="photo-list"),
    path("albums/<int:album_id>/photos/upload/", photo_upload, name="photo-upload"),
    path("albums/<int:album_id>/photos/<int:photo_id>/", photo_update, name="photo-update"),
    path("albums/<int:album_id>/photos/batch/", photo_batch, name="photo-batch"),
]
