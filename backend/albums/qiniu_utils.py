import uuid
from io import BytesIO
from django.conf import settings
from PIL import Image
from qiniu import Auth, put_data, put_file


def _get_qiniu_auth():
    return Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)


def upload_image(file_obj, album_id):
    """上传单个图片到七牛云，返回 (url, file_size, width, height)"""
    auth = _get_qiniu_auth()

    ext = file_obj.name.split(".")[-1].lower() if "." in file_obj.name else "jpg"
    key = f"photos/{album_id}/{uuid.uuid4().hex}.{ext}"
    token = auth.upload_token(settings.QINIU_BUCKET_NAME, key, 3600)

    # 大文件已落盘时直接用 put_file v2 上传，避免二次读入内存
    temp_path = getattr(file_obj, "temporary_file_path", None)
    if callable(temp_path):
        temp_path = temp_path()

    if temp_path:
        ret, info = put_file(token, key, temp_path, version="v2")
        file_size = file_obj.size
        content = file_obj.read()
        file_obj.seek(0)
    else:
        content = file_obj.read()
        file_size = len(content)
        ret, info = put_data(token, key, content)

    if ret is None:
        raise Exception(f"七牛云上传失败: {info}")

    img = Image.open(BytesIO(content))
    width, height = img.size

    url = f"http://{settings.QINIU_DOMAIN}/{key}"
    return url, file_size, width, height


def validate_image(file_obj, max_size=None):
    """校验图片文件"""
    if max_size is None:
        max_size = settings.MAX_UPLOAD_SIZE

    if file_obj.size > max_size:
        raise ValueError(f"文件大小不能超过 {max_size // (1024 * 1024)}MB")

    content = file_obj.read()
    file_obj.seek(0)
    img = Image.open(BytesIO(content))
    mime = Image.MIME.get(img.format, "")
    if mime not in settings.ALLOWED_IMAGE_TYPES:
        raise ValueError(f"不支持的图片格式: {mime}")
