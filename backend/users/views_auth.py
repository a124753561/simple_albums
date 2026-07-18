from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if not username or not password:
        return Response({
            "code": 400, "data": None, "message": "用户名和密码不能为空"
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if not user:
        return Response({
            "code": 401, "data": None, "message": "用户名或密码错误"
        }, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({
            "code": 403, "data": None, "message": "账号已被禁用"
        }, status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(user)
    return Response({
        "code": 0,
        "data": {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "is_superuser": user.is_superuser,
            }
        },
        "message": "登录成功",
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_view(request):
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({
            "code": 400, "data": None, "message": "refresh token 不能为空"
        }, status=status.HTTP_400_BAD_REQUEST)
    try:
        refresh = RefreshToken(refresh_token)
        return Response({
            "code": 0,
            "data": {"access": str(refresh.access_token)},
            "message": "ok",
        })
    except Exception:
        return Response({
            "code": 401, "data": None, "message": "refresh token 无效或已过期"
        }, status=status.HTTP_401_UNAUTHORIZED)
