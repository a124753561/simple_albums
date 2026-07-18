from django.urls import path
from .views import config_list, config_update, config_upload

urlpatterns = [
    path("configs/", config_list, name="config-list"),
    path("configs/update/", config_update, name="config-update"),
    path("configs/upload/", config_upload, name="config-upload"),
]
