from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import Album, Category
from .serializers import AlbumListSerializer, AlbumDetailSerializer, CategorySerializer


class PublicPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"


@api_view(["GET"])
@permission_classes([AllowAny])
def public_homepage_albums(request):
    """首页相册（homepage_show=true）"""
    albums = Album.objects.filter(homepage_show=True).order_by("sort_order", "-created_at")
    paginator = PublicPagination()
    page = paginator.paginate_queryset(albums, request)
    if page is not None:
        serializer = AlbumListSerializer(page, many=True)
        return Response({
            "code": 0,
            "data": {
                "results": serializer.data,
                "count": paginator.page.paginator.count,
                "page": paginator.page.number,
                "page_size": paginator.page_size,
            },
            "message": "ok",
        })
    serializer = AlbumListSerializer(albums, many=True)
    return Response({"code": 0, "data": serializer.data, "message": "ok"})


@api_view(["GET"])
@permission_classes([AllowAny])
def public_albums(request):
    """全部相册"""
    category = request.query_params.get("category")
    albums = Album.objects.all().order_by("sort_order", "-created_at")
    if category:
        albums = albums.filter(category_id=category)
    paginator = PublicPagination()
    page = paginator.paginate_queryset(albums, request)
    if page is not None:
        serializer = AlbumListSerializer(page, many=True)
        return Response({
            "code": 0,
            "data": {
                "results": serializer.data,
                "count": paginator.page.paginator.count,
                "page": paginator.page.number,
                "page_size": paginator.page_size,
            },
            "message": "ok",
        })
    serializer = AlbumListSerializer(albums, many=True)
    return Response({"code": 0, "data": serializer.data, "message": "ok"})


@api_view(["GET"])
@permission_classes([AllowAny])
def public_album_detail(request, album_id):
    """相册详情"""
    try:
        album = Album.objects.get(id=album_id)
    except Album.DoesNotExist:
        return Response({
            "code": 404, "data": None, "message": "相册不存在"
        }, status=status.HTTP_404_NOT_FOUND)
    serializer = AlbumDetailSerializer(album)
    return Response({"code": 0, "data": serializer.data, "message": "ok"})


@api_view(["GET"])
@permission_classes([AllowAny])
def public_categories(request):
    """分类树"""
    categories = Category.objects.filter(parent__isnull=True).order_by("sort_order", "id")
    serializer = CategorySerializer(categories, many=True)
    return Response({"code": 0, "data": serializer.data, "message": "ok"})
