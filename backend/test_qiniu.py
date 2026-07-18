"""
七牛云上传/下载功能测试脚本

参考文档: https://developer.qiniu.com/kodo/1242/python

使用方法:
    cd backend && ./venv/bin/python test_qiniu.py
"""
import os
import sys
import uuid
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from qiniu import Auth, put_file, put_data, BucketManager, etag
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

AK = os.environ["QINIU_ACCESS_KEY"]
SK = os.environ["QINIU_SECRET_KEY"]
BUCKET = os.environ["QINIU_BUCKET_NAME"]
DOMAIN = os.environ["QINIU_DOMAIN"]
TEST_IMAGE = os.path.expanduser("~/Downloads/西班牙国旗.jpg")

auth = Auth(AK, SK)
bucket_mgr = BucketManager(auth)


def hr(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


# ── 1. put_file 上传本地文件 ────────────────────────────────────
hr("1. put_file — 上传本地文件")

key1 = f"test/putfile-{uuid.uuid4().hex[:8]}.jpg"
token = auth.upload_token(BUCKET, key1, 3600)
ret, info = put_file(token, key1, TEST_IMAGE, version="v2")

print(f"  status: {info.status_code}")
print(f"  key:    {ret['key']}")
print(f"  hash:   {ret['hash']}")
assert ret["key"] == key1
assert ret["hash"] == etag(TEST_IMAGE)
print(f"  [OK] key 和 hash 校验通过")
url1 = f"https://{DOMAIN}/{key1}"
print(f"  URL:    {url1}")


# ── 2. put_data 上传内存数据 ───────────────────────────────────────
hr("2. put_data — 上传内存数据")

with open(TEST_IMAGE, "rb") as f:
    img_data = f.read()

img = Image.open(BytesIO(img_data))
print(f"  尺寸: {img.size[0]}x{img.size[1]}  格式: {img.format}  大小: {len(img_data):,} bytes")

key2 = f"test/putdata-{uuid.uuid4().hex[:8]}.jpg"
token = auth.upload_token(BUCKET, key2, 3600)
ret, info = put_data(token, key2, img_data)

print(f"  status: {info.status_code}")
print(f"  key:    {ret['key']}")
print(f"  hash:   {ret['hash']}")
url2 = f"https://{DOMAIN}/{key2}"
print(f"  [OK] 上传成功")
print(f"  URL:    {url2}")


# ── 3. 列出文件 ────────────────────────────────────────────────────
hr("3. list — 列出 test/ 目录")

ret, eof, info = bucket_mgr.list(BUCKET, prefix="test/", limit=10)
if ret is None:
    print(f"[FAIL] {info}")
    sys.exit(1)
items = ret.get("items", [])
print(f"  共 {len(items)} 个文件:")
for item in items:
    print(f"    {item['key']:50s} {item['fsize']:>10,} bytes  {item['mimeType']}")


# ── 4. 文件信息 ────────────────────────────────────────────────────
hr("4. stat — 文件状态信息")

for label, key in [("put_file", key1), ("put_data", key2)]:
    ret, info = bucket_mgr.stat(BUCKET, key)
    if ret is None:
        print(f"[FAIL] {label}: {info}")
    else:
        print(f"[OK] {label}: fsize={ret['fsize']:,}  mime={ret['mimeType']}  hash={ret['hash']}")


# ── 5. 删除 ────────────────────────────────────────────────────────
# hr("5. delete — 清理测试文件")
#
# for label, key in [("put_file", key1), ("put_data", key2)]:
#     ret, info = bucket_mgr.delete(BUCKET, key)
#     ok = ret is not None or (info and info.status_code == 200)
#     print(f"[{'OK' if ok else 'FAIL'}] {label}: {key}")


# ── 总结 ────────────────────────────────────────────────────────────
hr("测试总结")
print(f"  ✓ put_file     — 上传本地文件（v2 API）")
print(f"  ✓ put_data     — 上传内存数据")
print(f"  ✓ list         — 列出桶内文件")
print(f"  ✓ stat         — 获取文件元信息")
# print(f"  ✓ delete       — 删除文件")
print()
print(f"  {url1}")
print(f"  {url2}")
