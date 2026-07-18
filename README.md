# 相册系统 (Xiangce)

Django DRF 后端 + Vue3 管理后台 + Vue3 展示前端，图片存储使用七牛云 Kodo。

## 项目结构

```
Xiangce/
├── backend/           # Django DRF API (Python 3.12+)
├── admin-frontend/    # 管理后台 (Vue3 + Element Plus + TypeScript)
├── public-frontend/   # 展示前端 (Vue3 + Vant4 + TypeScript)
├── docs/              # 设计文档
└── plan.md            # 原始需求
```

## 快速开始

```bash
# 后端
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 编辑 .env 填入七牛云密钥
python manage.py migrate
python manage.py init_admin   # 创建 admin/admin321
python manage.py runserver

# 管理后台 (localhost:5173)
cd admin-frontend
npm install && npm run dev

# 展示前端 (localhost:5174)
cd public-frontend
npm install && npm run dev
```

## 生产环境

```bash
# 后端 — 使用 gunicorn
gunicorn config.wsgi:application -b 127.0.0.1:8000 -w 4

# 前端 — 构建静态文件
cd admin-frontend && npm run build   # dist/ 部署到 /admin/
cd public-frontend && npm run build  # dist/ 部署到 /

# 环境变量（生产）
# .env.production 中配置: VITE_API_BASE_URL, VITE_ROUTER_BASE
```

## 技术栈

| 层 | 技术 |
|---|------|
| 后端框架 | Django 4.2 + Django REST Framework |
| 认证 | SimpleJWT (access/refresh token) |
| 对象存储 | 七牛云 Kodo (python SDK) |
| 管理前端 | Vue 3 + Element Plus + Pinia + Axios |
| 展示前端 | Vue 3 + Vant 4 + Pinia + Axios |
| 构建工具 | Vite |
| 数据库 | SQLite (开发) / 可改为 PostgreSQL (生产) |

## API 路由

- `/api/auth/` — JWT 认证
- `/api/users/` — 用户管理
- `/api/categories/` — 分类管理
- `/api/albums/` — 相册管理
- `/api/albums/{id}/photos/` — 图片管理
- `/api/configs/` — 系统设置
- `/api/public/` — 前台公开 API (无需认证)

## 环境变量

### 后端 (.env)
| 变量 | 说明 |
|------|------|
| `DJANGO_SECRET_KEY` | Django 密钥 |
| `DJANGO_DEBUG` | 调试模式 (True/False) |
| `QINIU_ACCESS_KEY` | 七牛云 AK |
| `QINIU_SECRET_KEY` | 七牛云 SK |
| `QINIU_BUCKET_NAME` | 存储桶名称 |
| `QINIU_DOMAIN` | CDN 域名 |

### 前端 (.env.production)
| 变量 | 说明 |
|------|------|
| `VITE_API_BASE_URL` | 后端 API 地址 |
| `VITE_ROUTER_BASE` | 路由前缀 |
