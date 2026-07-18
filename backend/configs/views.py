from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import SystemConfig
from .serializers import SystemConfigSerializer


@api_view(["GET"])
def config_list(request):
    configs = SystemConfig.objects.all()
    data = {c.key: c.value for c in configs}
    return Response({"code": 0, "data": data, "message": "ok"})


@api_view(["PUT"])
def config_update(request):
    for key, value in request.data.items():
        SystemConfig.objects.update_or_create(
            key=key,
            defaults={"value": str(value) if value is not None else ""}
        )
    configs = SystemConfig.objects.all()
    data = {c.key: c.value for c in configs}
    return Response({"code": 0, "data": data, "message": "保存成功"})


@api_view(["GET"])
@permission_classes([AllowAny])
def public_contact(request):
    configs = SystemConfig.objects.filter(key__in=["wechat", "wechat_qrcode", "email", "phone", "about"])
    data = {c.key: c.value for c in configs}
    for key in ["wechat", "wechat_qrcode", "email", "phone", "about"]:
        if key not in data:
            data[key] = ""
    return Response({"code": 0, "data": data, "message": "ok"})


@api_view(["POST"])
@parser_classes([MultiPartParser])
def config_upload(request):
    """上传图片到七牛云，返回 URL"""
    file_obj = request.FILES.get("file")
    if not file_obj:
        return Response({
            "code": 400, "data": None, "message": "未选择文件"
        }, status=status.HTTP_400_BAD_REQUEST)

    from albums.qiniu_utils import upload_image, validate_image

    try:
        validate_image(file_obj)
        url, file_size, width, height = upload_image(file_obj, "config")
        return Response({
            "code": 0,
            "data": {"url": url, "file_size": file_size, "width": width, "height": height},
            "message": "上传成功",
        })
    except Exception as e:
        return Response({
            "code": 500, "data": None, "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
