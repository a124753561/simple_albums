from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .models import Category, Album, Photo
from users.models import User
from .serializers import (
    CategorySerializer, CategoryFlatSerializer,
    CategorySimpleSerializer,
    AlbumListSerializer, AlbumDetailSerializer, AlbumCreateSerializer,
)


# ─── Category ────────────────────────────────────────────────────────────────

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            flat = self.request.query_params.get("flat")
            if flat and flat.lower() == "true":
                return CategoryFlatSerializer
            return CategorySerializer
        return CategorySerializer

    def list(self, request, *args, **kwargs):
        flat = request.query_params.get("flat")
        if flat and flat.lower() == "true":
            queryset = self.filter_queryset(self.get_queryset().order_by("sort_order", "id"))
            serializer = self.get_serializer(queryset, many=True)
            return Response({"code": 0, "data": serializer.data, "message": "ok"})
        # Tree mode: only top-level
        queryset = self.get_queryset().filter(parent__isnull=True).order_by("sort_order", "id")
        serializer = self.get_serializer(queryset, many=True)
        return Response({"code": 0, "data": serializer.data, "message": "ok"})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "code": 0, "data": CategorySerializer(serializer.instance).data, "message": "创建成功"
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "code": 0, "data": CategorySerializer(serializer.instance).data, "message": "更新成功"
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.children.exists():
            return Response({
                "code": 400, "data": None, "message": "该分类下有子分类，无法删除"
            }, status=status.HTTP_400_BAD_REQUEST)
        if instance.albums.exists():
            return Response({
                "code": 400, "data": None, "message": "该分类下有相册，无法删除"
            }, status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response({"code": 0, "data": None, "message": "删除成功"})

    @action(detail=False, methods=["get"])
    def simple(self, request):
        categories = Category.objects.all().order_by("sort_order", "id")
        serializer = CategorySimpleSerializer(categories, many=True)
        return Response({"code": 0, "data": serializer.data, "message": "ok"})


# ─── Album ───────────────────────────────────────────────────────────────────

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.select_related("category").all()

    def get_serializer_class(self):
        if self.action == "create":
            return AlbumCreateSerializer
        if self.action in ("update", "partial_update"):
            return AlbumCreateSerializer
        if self.action == "retrieve":
            return AlbumDetailSerializer
        return AlbumListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category_id=category)
        homepage = self.request.query_params.get("homepage_show")
        if homepage and homepage.lower() == "true":
            qs = qs.filter(homepage_show=True)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(title__icontains=search)
        return qs.order_by("sort_order", "-created_at")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"code": 0, "data": serializer.data, "message": "ok"})

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"code": 0, "data": serializer.data, "message": "ok"})

    def get_paginated_response(self, data):
        return Response({
            "code": 0,
            "data": {
                "results": data,
                "count": self.paginator.page.paginator.count,
                "page": self.paginator.page.number,
                "page_size": self.paginator.page_size,
            },
            "message": "ok",
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "code": 0, "data": AlbumDetailSerializer(serializer.instance).data, "message": "创建成功"
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "code": 0, "data": AlbumDetailSerializer(serializer.instance).data, "message": "更新成功"
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"code": 0, "data": None, "message": "删除成功"})


# ─── Dashboard ────────────────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    return Response({
        "code": 0,
        "data": {
            "albums": Album.objects.count(),
            "photos": Photo.objects.count(),
            "users": User.objects.count(),
        },
        "message": "ok",
    })
