from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-created_at")
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ("update", "partial_update"):
            return UserUpdateSerializer
        return UserSerializer

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
            "code": 0, "data": UserSerializer(serializer.instance).data, "message": "创建成功"
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "code": 0, "data": UserSerializer(serializer.instance).data, "message": "更新成功"
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == request.user.id:
            return Response({
                "code": 400, "data": None, "message": "不能删除自己"
            }, status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response({"code": 0, "data": None, "message": "删除成功"})
