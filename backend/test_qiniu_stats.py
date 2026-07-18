"""
七牛云 Fusion 运营统计 API 测试脚本

API 文档: https://developer.qiniu.com/fusion/13366/fusion-api-analytics

使用方法:
    cd backend && ./venv/bin/python test_qiniu_stats.py
"""
import os
import sys
from datetime import date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from albums.qiniu_stats import get_top_count_urls, get_top_photos


def hr(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


# ── 1. 测试 Top URL API ─────────────────────────────────────────
hr("1. topcounturl — 获取 Top 100 URL")

data = get_top_count_urls(days=7)
if data is None:
    print("[FAIL] 请求失败，请检查 AK/SK 和域名配置")
    sys.exit(1)

urls = data.get("urls", [])
counts = data.get("count", [])
print(f"[OK] 返回 {len(urls)} 个 URL")
print(f"  Top 5:")
for i in range(min(5, len(urls))):
    print(f"    {i+1}. count={counts[i]:>8,}  {urls[i]}")


# ── 2. 测试匹配本地图片 ─────────────────────────────────────────
hr("2. get_top_photos — 匹配本地 Photo 记录")

photos = get_top_photos(limit=10)
print(f"[OK] 匹配到 {len(photos)} 张本地图片")
for i, p in enumerate(photos):
    print(f"  {i+1}. view_count={p['view_count']:>8,}  [{p['album_title']}]  {p['name']}")
    print(f"      {p['url']}")


# ── 总结 ─────────────────────────────────────────────────────────
hr("测试总结")
print(f"  ✓ topcounturl  — 七牛 Fusion API 正常")
print(f"  ✓ get_top_photos — 本地图片匹配正常")
print()
print(f"  如果有本地图片未被匹配，可能是 CDN 最近 {len(photos)} 天内该图片无访问量")
