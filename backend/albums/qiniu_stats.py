import json
from datetime import date, timedelta
from urllib.parse import urlparse

import requests
from django.conf import settings
from qiniu import Auth


FUSION_HOST = "fusion.qiniuapi.com"


def _qbox_token(method, url_str, body):
    """使用 Qiniu SDK 生成 Fusion API 所需的 QBox 鉴权 token"""
    auth = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
    token = auth.token_of_request(url_str, body=body, content_type="application/json")
    return token


def get_top_count_urls(days=7):
    """获取访问次数最多的 Top 100 URL"""
    domain = settings.QINIU_DOMAIN
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    url = f"https://{FUSION_HOST}/v2/tune/loganalyze/topcounturl"
    body = json.dumps({
        "domains": [domain],
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "region": "global",
    })

    token = _qbox_token("POST", url, body)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"QBox {token}",
    }

    resp = requests.post(url, data=body, headers=headers, timeout=15)
    data = resp.json()
    if data.get("code") == 200:
        return data["data"]
    return None


def get_top_photos(limit=10):
    """获取访问量 Top 图片列表，匹配本地 Photo 记录"""
    data = get_top_count_urls(days=7)
    if not data:
        return []

    from .models import Photo

    urls = data.get("urls", [])
    counts = data.get("count", [])
    url_count = {}
    for i, u in enumerate(urls):
        if i < len(counts):
            path = urlparse(u).path
            url_count[path] = counts[i]

    photos = list(Photo.objects.select_related("album").all())
    matched = []
    for photo in photos:
        photo_path = urlparse(photo.url).path
        if photo_path in url_count:
            matched.append({
                "id": photo.id,
                "name": photo.name,
                "url": photo.url,
                "view_count": url_count[photo_path],
                "album_id": photo.album_id,
                "album_title": photo.album.title,
            })

    matched.sort(key=lambda x: x["view_count"], reverse=True)
    return matched[:limit]


def get_uv_data(days=7):
    """获取每日独立访客数 (UV) 趋势数据"""
    domain = settings.QINIU_DOMAIN
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    url = f"https://{FUSION_HOST}/v2/tune/loganalyze/uniquevisitor"
    body = json.dumps({
        "domains": [domain],
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "freq": "1day",
    })

    token = _qbox_token("POST", url, body)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"QBox {token}",
    }

    resp = requests.post(url, data=body, headers=headers, timeout=15)
    data = resp.json()
    if data.get("code") == 200:
        return {
            "points": data["data"].get("points", []),
            "values": data["data"].get("uvCount", []),
        }
    return {"points": [], "values": []}


def get_top_albums(limit=10):
    """获取访问量 Top 相册列表，按相册内所有图片访问量汇总排名"""
    data = get_top_count_urls(days=7)
    if not data:
        return []

    from .models import Photo

    urls = data.get("urls", [])
    counts = data.get("count", [])
    url_count = {}
    for i, u in enumerate(urls):
        if i < len(counts):
            path = urlparse(u).path
            url_count[path] = counts[i]

    # 聚合每个相册的访问量
    album_stats = {}  # album_id → {album_title, cover, total_views}
    photos = Photo.objects.select_related("album").all()
    for photo in photos:
        photo_path = urlparse(photo.url).path
        if photo_path in url_count:
            if photo.album_id not in album_stats:
                album_stats[photo.album_id] = {
                    "id": photo.album_id,
                    "title": photo.album.title,
                    "cover": photo.album.cover or photo.url,
                    "total_views": 0,
                }
            album_stats[photo.album_id]["total_views"] += url_count[photo_path]

    result = sorted(album_stats.values(), key=lambda x: x["total_views"], reverse=True)
    return result[:limit]
