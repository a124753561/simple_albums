from django.urls import path
from .views_public import (
    public_homepage_albums, public_albums,
    public_album_detail, public_categories,
)
from configs.views import public_contact

urlpatterns = [
    path("homepage-albums/", public_homepage_albums, name="public-homepage"),
    path("albums/", public_albums, name="public-albums"),
    path("albums/<int:album_id>/", public_album_detail, name="public-album-detail"),
    path("categories/", public_categories, name="public-categories"),
    path("contact/", public_contact, name="public-contact"),
]
