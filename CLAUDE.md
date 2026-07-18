# CLAUDE.md — 相册系统

## 项目概览

三端分离的图片相册管理系统：
- **backend/** — Django DRF API 服务器 (Python 3.12+, Django 4.2, venv 位于 `backend/venv/`)
- **admin-frontend/** — 管理后台 SPA (Vue3 + Element Plus + Pinia, 端口 5173)
- **public-frontend/** — 展示前端 SPA (Vue3 + Vant4 + Pinia, 端口 5174)

## 常用命令

```bash
# === 后端 ===
cd backend
source venv/bin/activate
python manage.py runserver                    # 启动开发服务器
python manage.py migrate                      # 数据库迁移
python manage.py init_admin                   # 创建超级管理员 (admin/admin321)
python test_qiniu.py                          # 测试七牛云上传/下载

# === 管理后台 ===
cd admin-frontend
npm run dev                                   # 启动 (localhost:5173, proxy /api → :8000)
npm run build                                 # 生产构建
npx vue-tsc -b --noEmit                       # 类型检查

# === 展示前端 ===
cd public-frontend
npm run dev                                   # 启动 (localhost:5174, proxy /api → :8000)
npm run build                                 # 生产构建
npx vue-tsc -b --noEmit                       # 类型检查
```

## 后端架构

- **config/settings.py** — 核心配置 (dotenv、JWT、CORS、七牛云)
- **config/urls.py** — 根路由，已移除 admin，handler404 返回 JSON
- **users/** — 自定义 User 模型 + JWT 认证 (views_auth.py)
- **albums/models.py** — Category (2级自引用) / Album / Photo
- **albums/views.py** — CategoryViewSet / AlbumViewSet（统一 `{code, data, message}` 格式）
- **albums/views_photo.py** — photo_upload / photo_batch / photo_list / photo_update
- **albums/views_public.py** — 前台公开 API (AllowAny)
- **albums/qiniu_utils.py** — upload_image / validate_image
- **configs/** — SystemConfig key-value 模型
- **SQLite** — `backend/db.sqlite3`，自定义 User 后需 `manage.py migrate`

## API 响应格式

统一 `{code: number, data: any, message: string}`。code=0 表示成功。

## 前端关键模式

- **request.ts** — axios 实例，`baseURL` 从 `VITE_API_BASE_URL` 环境变量读取
- **router/index.ts** — `createWebHistory(VITE_ROUTER_BASE)`，login 路由标记 `noAuth`
- **stores/auth.ts** — JWT 状态管理，access token 存 localStorage
- **环境区分** — `.env.development` / `.env.production`，Vite 自动加载

## 七牛云

- 图片存储路径: `photos/{album_id}/{uuid}.{ext}`
- 上传方式: 大文件 `put_file`(v2), 小文件 `put_data`
- 访问: CDN 域名 (`tid2j37xr.hn-bkt.clouddn.com`)，注意仅支持 HTTP
- 凭证: `.env` 文件管理 (已在 .gitignore 中)

## 安全注意

- `.env`、`.envbak`、`*.local` 已加入 .gitignore
- `DEBUG=False` + 生产 SECRET_KEY 部署到线上
- 生产环境移除 `CORS_ALLOW_ALL_ORIGINS = DEBUG`
- admin 面板路由已移除 (`django.contrib.admin`)
