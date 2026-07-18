from django.urls import path, include
from django.http import JsonResponse


def handler404(request, exception=None):
    return JsonResponse({"code": 404, "data": None, "message": "Not Found"}, status=404)


handler400 = handler404
handler403 = handler404
handler500 = handler404

urlpatterns = [
    path("api/auth/", include("users.urls_auth")),
    path("api/", include("users.urls")),
    path("api/", include("albums.urls")),
    path("api/", include("configs.urls")),
    path("api/public/", include("albums.urls_public")),
]
