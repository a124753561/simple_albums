from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .models import Album, Photo
from .qiniu_utils import upload_image, validate_image
from .serializers import PhotoSerializer


@api_view(["POST"])
@parser_classes([MultiPartParser])
def photo_upload(request, album_id):
    """批量上传图片到指定相册"""
    try:
        album = Album.objects.get(id=album_id)
    except Album.DoesNotExist:
        return Response({
            "code": 404, "data": None, "message": "相册不存在"
        }, status=status.HTTP_404_NOT_FOUND)

    files = request.FILES.getlist("files")
    if not files:
        return Response({
            "code": 400, "data": None, "message": "未选择文件"
        }, status=status.HTTP_400_BAD_REQUEST)

    photos = []
    errors = []
    max_sort = Photo.objects.filter(album=album).count()

    for i, file_obj in enumerate(files):
        try:
            validate_image(file_obj)
            url, file_size, width, height = upload_image(file_obj, album_id)
            photo = Photo.objects.create(
                album=album,
                name=file_obj.name.rsplit(".", 1)[0],
                url=url,
                file_size=file_size,
                width=width,
                height=height,
                sort_order=max_sort + i + 1,
            )
            photos.append(photo)
        except Exception as e:
            errors.append({"filename": file_obj.name, "error": str(e)})

    # 更新相册图片计数
    album.photo_count = Photo.objects.filter(album=album).count()

    # 自动设置封面为第一张图片
    if not album.cover and photos:
        album.cover = photos[0].url

    album.save()

    serializer = PhotoSerializer(photos, many=True)
    return Response({
        "code": 0,
        "data": {
            "photos": serializer.data,
            "errors": errors,
            "photo_count": album.photo_count,
            "cover": album.cover,
        },
        "message": f"成功上传 {len(photos)} 张" + (f"，{len(errors)} 张失败" if errors else ""),
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def photo_batch(request, album_id):
    """批量操作图片（改名 / 删除）"""
    try:
        album = Album.objects.get(id=album_id)
    except Album.DoesNotExist:
        return Response({
            "code": 404, "data": None, "message": "相册不存在"
        }, status=status.HTTP_404_NOT_FOUND)

    action = request.data.get("action")
    photo_ids = request.data.get("photo_ids", [])

    if not photo_ids:
        return Response({
            "code": 400, "data": None, "message": "请选择图片"
        }, status=status.HTTP_400_BAD_REQUEST)

    photos = Photo.objects.filter(id__in=photo_ids, album=album)

    if action == "rename":
        mode = request.data.get("mode", "manual")
        if mode == "auto":
            prefix = request.data.get("prefix", "")
            start = int(request.data.get("start", 1))
            for i, photo in enumerate(photos.order_by("sort_order")):
                photo.name = f"{prefix}{start + i}"
                photo.save()
        else:
            name = request.data.get("name", "")
            photos.update(name=name)

        serializer = PhotoSerializer(photos, many=True)
        return Response({
            "code": 0, "data": serializer.data, "message": f"已重命名 {photos.count()} 张图片"
        })

    elif action == "delete":
        count = photos.count()
        photos.delete()

        # 更新相册图片计数和封面
        remaining = Photo.objects.filter(album=album).order_by("sort_order")
        album.photo_count = remaining.count()
        album.cover = remaining.first().url if remaining.exists() else ""
        album.save()

        return Response({
            "code": 0, "data": {"photo_count": album.photo_count, "cover": album.cover},
            "message": f"已删除 {count} 张图片"
        })

    return Response({
        "code": 400, "data": None, "message": f"不支持的操作: {action}"
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def photo_list(request, album_id):
    """获取相册图片列表"""
    try:
        album = Album.objects.get(id=album_id)
    except Album.DoesNotExist:
        return Response({
            "code": 404, "data": None, "message": "相册不存在"
        }, status=status.HTTP_404_NOT_FOUND)

    photos = Photo.objects.filter(album=album).order_by("sort_order", "id")
    serializer = PhotoSerializer(photos, many=True)
    return Response({"code": 0, "data": serializer.data, "message": "ok"})


@api_view(["PATCH"])
def photo_update(request, album_id, photo_id):
    """更新单张图片（改名）"""
    try:
        photo = Photo.objects.get(id=photo_id, album_id=album_id)
    except Photo.DoesNotExist:
        return Response({
            "code": 404, "data": None, "message": "图片不存在"
        }, status=status.HTTP_404_NOT_FOUND)

    name = request.data.get("name")
    if name is None:
        return Response({
            "code": 400, "data": None, "message": "name 不能为空"
        }, status=status.HTTP_400_BAD_REQUEST)

    photo.name = name
    photo.save()
    serializer = PhotoSerializer(photo)
    return Response({"code": 0, "data": serializer.data, "message": "更新成功"})
