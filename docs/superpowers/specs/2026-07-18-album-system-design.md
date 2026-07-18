# 相册系统设计文档

> 基于 plan.md 需求，经与用户逐项确认后整理。
> 日期：2026-07-18

---

## 一、需求确认汇总

| 维度 | 决策 |
|------|------|
| 场景定位 | 多用户图床平台（B 端管理、C 端浏览） |
| 前台用户 | 纯公开浏览，不开放注册 |
| 图片上传 | 后端接收 → Django 上传七牛云 Kodo |
| 分类层级 | 最多两级（父子自关联） |
| 批量改名 | 统一命名 + 自动编号(N) 两种模式 |
| 首页展示 | 相册封面网格 + 分页 |
| 响应式 | PC + 手机端全适配 |
| 部署架构 | Nginx → Django API + 前台 Vue(Vant) + 后台 Vue(Element Plus)，三服务独立 |
| 路由模式 | History 模式 |
| 访问控制 | 全部公开 |
| 管理员 | 超级管理员 admin/admin321（可新增/禁用用户） |
| 数据库 | SQLite |
| 后端框架 | Django + DRF（djangorestframework） |

---

## 二、总体架构

```
┌──────────────────────────────────────────────────┐
│                    Nginx (反向代理)                 │
│   api.xxx.com    → Django:8000                    │
│   admin.xxx.com  → Vue Admin SPA 静态文件          │
│   www.xxx.com    → Vue Public SPA 静态文件          │
└────────┬──────────────┬───────────────────────────┘
         │              │
    ┌────▼────┐   ┌─────▼──────┐   ┌──────────────┐
    │ Django  │   │ Vue Admin  │   │ Vue Public   │
    │ DRF API │   │ Element+   │   │ Vant + Pinia │
    │ :8000   │   │ Vite       │   │ Vite         │
    └───┬─────┘   └────────────┘   └──────────────┘
        │
   ┌────▼─────┐     ┌──────────┐
   │ SQLite   │     │ 七牛云    │
   │          │     │ Kodo     │
   └──────────┘     └──────────┘
```

### 项目目录结构

```
Xiangce/
├── backend/             # Django + DRF 项目
├── admin-frontend/      # Vue3 + Element Plus + TS + Pinia
├── public-frontend/     # Vue3 + Vant + TS + Pinia
└── docs/                # 设计文档
```

### 技术栈明细

| 层 | 技术 | 版本建议 |
|----|------|----------|
| 后端框架 | Django | 5.x |
| API 框架 | djangorestframework | 3.x |
| JWT 认证 | djangorestframework-simplejwt | 5.x |
| 七牛云 SDK | qiniu | 7.x |
| 图片处理 | Pillow | 10.x |
| CORS | django-cors-headers | 4.x |
| 后台前端 | Vue 3 + TypeScript + Element Plus + Pinia + Vite | latest |
| 前台前端 | Vue 3 + TypeScript + Vant 4 + Pinia + Vite | latest |

---

## 三、数据库模型

### User（后台用户）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| username | CharField(150) | 用户名，唯一 |
| password | CharField(128) | 密码哈希（Django User 模型内置） |
| is_active | BooleanField | 是否启用 |
| is_superuser | BooleanField | 是否超级管理员 |
| created_at | DateTimeField | 创建时间 |

> 直接继承 Django 的 `AbstractUser`，扩展 `created_at` 字段。

### Category（相册分类，两级）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| name | CharField(100) | 分类名称 |
| parent | FK(self), null=True | 父分类，null = 一级分类 |
| sort_order | IntegerField(default=0) | 排序序号 |
| created_at | DateTimeField | 创建时间 |

- 约束：parent 为 null 时为一级分类；parent 非 null 时为二级分类（代码层校验，不允许三级）
- 删除保护：有关联子分类或相册时禁止删除

### Album（相册）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| title | CharField(200) | 相册标题 |
| description | TextField(blank=True) | 相册描述 |
| category | FK(Category) | 所属分类 |
| cover | URLField(blank=True) | 封面图 URL（七牛云） |
| homepage_show | BooleanField(default=False) | 是否首页显示 |
| sort_order | IntegerField(default=0) | 排序序号 |
| photo_count | IntegerField(default=0) | 图片数量（冗余字段） |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

- 封面默认为相册内第一张图片 URL，可在后台手动修改
- photo_count 在图片增删时同步更新

### Photo（图片）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| album | FK(Album), CASCADE | 所属相册 |
| name | CharField(200) | 图片名称 |
| url | URLField(500) | 七牛云存储 URL |
| file_size | BigIntegerField | 文件大小(字节) |
| width | IntegerField(default=0) | 图片宽度 |
| height | IntegerField(default=0) | 图片高度 |
| sort_order | IntegerField(default=0) | 排序序号 |
| created_at | DateTimeField | 创建时间 |

### SystemConfig（系统设置，key-value）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| key | CharField(100) | 配置键，唯一 |
| value | TextField | 配置值 |
| description | CharField(200) | 配置说明 |

- 预设 key：`wechat`（微信号）、`email`（邮箱）、`phone`（电话）、`about`（关于/简介）
- 可灵活扩展

---

## 四、API 接口设计

### 认证策略

- 后台所有接口（除 `/api/auth/` 外）需 JWT access token
- Access token 30 分钟，Refresh token 7 天
- 前台公开接口无需认证

### 认证接口

```
POST  /api/auth/login/         # { username, password } → { access, refresh }
POST  /api/auth/refresh/       # { refresh } → { access }
```

### 后台接口

#### 用户管理（需 admin 权限）

```
GET    /api/users/              # 用户列表
POST   /api/users/              # 新增用户
PATCH  /api/users/{id}/         # 修改用户（含 is_active 禁用/启用）
DELETE /api/users/{id}/         # 删除用户（不能删除自己）
```

#### 分类管理

```
GET    /api/categories/         # 树形结构；?flat=true 平铺返回
POST   /api/categories/         # { name, parent_id? }
PATCH  /api/categories/{id}/    # 修改名称、排序
DELETE /api/categories/{id}/    # 有子分类或关联相册时 400 拒绝
```

#### 相册管理

```
GET    /api/albums/             # 列表，支持 ?category=x & ?homepage_show=true & ?search=
POST   /api/albums/             # { title, description?, category_id, homepage_show, sort_order }
GET    /api/albums/{id}/        # 相册详情（含图片列表）
PATCH  /api/albums/{id}/        # 修改相册信息
DELETE /api/albums/{id}/        # 级联删除所有图片 + 七牛云文件
```

#### 图片管理

```
GET    /api/albums/{id}/photos/        # 图片列表
POST   /api/albums/{id}/photos/upload/  # 批量上传（multipart，多文件）
POST   /api/albums/{id}/photos/batch/   # 批量操作
```

批量操作请求体格式：

```json
// 统一命名
{ "action": "rename", "mode": "manual", "name": "统一名称", "photo_ids": [1, 2, 3] }

// 自动编号
{ "action": "rename", "mode": "auto", "prefix": "产品图-", "start": 1, "photo_ids": [1, 2, 3] }

// 批量删除
{ "action": "delete", "photo_ids": [1, 2, 3] }
```

#### 系统设置

```
GET    /api/configs/            # 获取所有配置（键值对）
PUT    /api/configs/            # 批量更新 { "wechat": "xxx", "email": "xxx" }
```

### 前台公开接口（无需认证）

```
GET    /api/public/homepage-albums/    # 首页相册（homepage_show=true），分页
GET    /api/public/albums/             # 全部相册，?category=x 筛选，分页
GET    /api/public/albums/{id}/        # 相册详情 + 图片列表（分页）
GET    /api/public/categories/         # 分类树
GET    /api/public/contact/            # 联系档案 { wechat, email, phone, about }
```

### 分页规范

- 前台：cursor pagination，每页 20 条
- 后台：PageNumber pagination，每页 20 条

### 七牛云上传流程

```
客户端 → POST multipart (多文件) → Django
  → 校验（格式 jpg/png/gif/webp，≤20MB，单次≤50张）
  → Pillow 读取宽高
  → 七牛云 SDK 上传（按 /photos/{album_id}/{uuid}.{ext} 路径存储）
  → 返回 CDN URL
  → 批量写入 Photo 表
  → 更新 Album.photo_count
  → 若相册无封面，自动设第一张为封面
  → 返回图片列表
```

### 统一响应格式

```json
// 成功
{ "code": 0, "data": {...}, "message": "ok" }

// 分页
{ "code": 0, "data": { "results": [...], "count": 100, "next": "..." } }

// 错误
{ "code": 400, "data": null, "message": "错误描述" }
```

---

## 五、前台设计

Vue3 + Vant 4 + Pinia + Vite + TypeScript，History 模式。

### 页面路由

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | 首页 | 标记首页显示的相册封面网格，分页 |
| `/albums` | 全部相册 | 所有相册封面网格，支持分类筛选 |
| `/albums/:id` | 相册详情 | 图片浏览 |
| `/contact` | 联系档案 | 微信号、邮箱等 |

### 组件树

```
App.vue
├── AppHeader.vue              # 顶部固定导航（首页/相册/联系/分类下拉）
├── <router-view>
│   ├── HomePage.vue           # 首页
│   │   ├── AlbumCoverGrid.vue # 相册封面网格（复用）
│   │   │   └── AlbumCoverCard.vue
│   │   └── Pagination.vue     # 分页（复用）
│   │
│   ├── AlbumListPage.vue      # 全部相册
│   │   ├── CategoryFilter.vue # 分类筛选
│   │   ├── AlbumCoverGrid.vue
│   │   └── Pagination.vue
│   │
│   ├── AlbumDetailPage.vue    # 相册详情
│   │   ├── PhotoWaterfall.vue # 瀑布流图片布局
│   │   └── PhotoViewer.vue    # 点击放大/滑动浏览
│   │
│   └── ContactPage.vue        # 联系档案
└── AppFooter.vue
```

### Pinia Store

| Store | 职责 |
|-------|------|
| `useAlbumStore` | 首页相册、全部相册列表、当前相册详情 |
| `useCategoryStore` | 分类树（前台首次拉取后缓存） |
| `useContactStore` | 联系档案 |

### 响应式断点

| 断点 | 相册封面列数 | 图片网格列数 |
|------|-------------|-------------|
| <768px (手机) | 1 列 | 2-3 列 |
| 768-1024px (平板) | 2-3 列 | 3-4 列 |
| >1024px (PC) | 4-5 列 | 4-6 列 |

最大宽度 1200px 居中。

### 关键交互

- **相册封面卡片**：封面图 + 标题 + 图片数量，点击进入相册详情
- **图片查看器**：Vant ImagePreview，手势左右滑动切换
- **图片懒加载**：Vant Lazyload 指令
- **下拉刷新**：Vant PullRefresh
- **上拉加载更多**：Vant List 组件（配合分页光标）
- **分类筛选**：全部相册页可通过分类 dropdown 筛选
- **分类下拉导航**：顶部"相册分类"菜单，PC hover 展开，手机点击展开

---

## 六、后台设计

Vue3 + Element Plus + Pinia + Vite + TypeScript，History 模式。

### 页面路由

| 路径 | 页面 | 说明 |
|------|------|------|
| `/login` | 登录页 | 用户名密码登录 |
| `/dashboard` | 仪表盘 | 相册数/图片数/存储概览 |
| `/users` | 用户管理 | 列表 + 新增/编辑弹窗 |
| `/categories` | 分类管理 | 两级树形表格 |
| `/albums` | 相册管理 | 相册列表 |
| `/albums/:id/photos` | 图片管理 | 某相册的图片批量管理 |
| `/settings` | 系统设置 | 联系档案等配置 |

`/login` 免登录，其他路由全部需认证（路由守卫 + token 检查）。

### 布局

```
AdminLayout.vue
├── AdminSidebar.vue           # 左侧菜单，可折叠
│   ├── 仪表盘
│   ├── 用户管理（仅 admin 可见）
│   ├── 分类管理
│   ├── 相册管理
│   └── 系统设置
└── <router-view>
```

### 主要页面组件

```
AdminLayout.vue
├── LoginPage.vue
├── DashboardPage.vue           # 统计卡片 + 快捷入口
├── UserListPage.vue            # 表格 + 新增/编辑 Dialog
├── CategoryPage.vue            # el-table 树形数据 + Dialog
├── AlbumListPage.vue           # 搜索/筛选 + 表格 + 新增/编辑 Dialog
├── AlbumDetailPage.vue         # 相册信息 + 图片批量管理
│   ├── AlbumInfoForm.vue       # 相册标题/描述/分类/封面URL/首页显示
│   ├── PhotoUploader.vue       # el-upload 拖拽批量上传 + 进度条
│   └── PhotoList.vue           # 图片网格 + 多选 + 批量改名/删除工具栏
└── SettingsPage.vue            # el-form 系统配置
```

### Pinia Store

| Store | 职责 |
|-------|------|
| `useAuthStore` | 登录态、token 管理（localStorage 持久化）、自动 refresh |
| `useUserStore` | 用户列表、CRUD |
| `useCategoryStore` | 分类树、CRUD |
| `useAlbumStore` | 相册列表（分页）、CRUD |
| `usePhotoStore` | 当前相册图片列表、批量操作 |
| `useConfigStore` | 系统配置读写 |

### 关键交互

- **批量上传**：Element Plus Upload 组件，支持拖拽文件夹/多文件，缩略图预览队列，进度条。上传完成后自动设置封面（若无封面）
- **批量改名**：选中图片 → 弹出 Dialog → 选择模式（统一名称/自动编号）→ 提交
- **批量删除**：选中图片 → MessageBox 二次确认 → 提交（后端同步删七牛云）
- **首页显示开关**：相册列表行内 el-switch，乐观更新
- **分类树形表格**：el-table 的 tree-props 展示两级，内联新增/编辑
- **拖拽排序**：图片列表和相册列表支持行拖拽排序（vuedraggable）

### Axios 拦截器

```
请求拦截：自动附加 Authorization: Bearer <access_token>
响应拦截：
  - 401 → 尝试 POST /api/auth/refresh/
    - 成功 → 更新 token，重放原始请求
    - 失败 → 清除 login state，router.push('/login')
  - 其他错误 → 统一 toast 提示
```

---

## 七、安全性设计

- **密码**：Django 内置 PBKDF2 哈希，不做明文存储
- **JWT**：access token 30 分钟，refresh token 7 天，密钥存环境变量
- **上传校验**：服务端校验文件 MIME 类型（Pillow 读取真实类型）、文件大小、扩展名白名单
- **CORS**：仅允许配置中的来源域名
- **SQL 注入**：DRF ORM 查询，无原生 SQL
- **XSS**：前后端均不渲染用户输入为 HTML，Vue 默认转义
- **七牛云密钥**：存 Django settings 环境变量，不上传前端
- **admin 账号**：首次启动通过 Django management command 自动创建 admin/admin321

---

## 八、验证方式

完成后通过以下方式验证：

1. **后台功能验证**：
   - 登录 admin/admin321 → 创建分类 → 创建相册 → 批量上传图片 → 批量改名/删除 → 标记首页显示
   - 新增用户 → 用新用户登录 → 验证权限
   - 修改系统设置 → 前台查看联系档案是否更新

2. **前台功能验证**：
   - 访问首页 → 看到标记的相册 → 分页正常
   - 访问全部相册 → 分类筛选正常 → 点击进入相册详情
   - 图片查看器滑动/放大正常
   - 手机端响应式布局正常

3. **安全验证**：
   - 未登录直接访问后台 API → 返回 401
   - Token 过期后操作 → 自动 401 跳登录

4. **边界验证**：
   - 上传超大文件（>20MB）→ 后端拒绝
   - 删除有关联子分类的分类 → 拒绝并提示
   - 空相册访问 → 显示"暂无图片"
