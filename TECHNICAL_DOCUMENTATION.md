# Misicheng B2B 独立站完整技术文档

文档日期：2026-07-21  
项目目录：`D:\suibian\Downloads\dulizhan2-vue-flask`  
项目定位：面向海外客户的排插、电源转换器、充电设备类 B2B 展示与询盘平台。

> 说明：本文档用于项目展示、交接和二次开发说明，不包含服务器密码、数据库密码、AccessKey、管理员明文密码等敏感信息。

## 1. 项目概述

Misicheng B2B 独立站是一套前后端分离的多语言外贸独立站系统，核心目标是完成“产品展示 -> 加入询盘 -> 客户提交需求 -> 后台报价与消息沟通 -> 商家入驻与商品审核”的完整闭环。

系统覆盖三个主要使用端：

- 前台访客 / 客户端：浏览首页、产品列表、产品详情、服务、FAQ、博客、联系我们，注册登录后可提交询盘、查看询盘记录、收藏产品、修改密码。
- 商家端：商家注册和入驻申请，审核通过后可管理自己的商品、提交商品审核、维护独立媒体库、修改密码。
- 管理员后台：管理商品、分类、Banner、商家入驻审核、商品审核、询盘报价、联系消息、多语言、媒体库、客户账号、管理员账号和权限。

系统支持 8 种语言路由：

```text
en, zh, ja, ko, fr, de, es, ar
```

阿拉伯语页面会根据路由自动切换为 RTL 方向。

## 2. 技术栈

### 2.1 前端技术栈

| 类型 | 技术 | 当前用途 |
| --- | --- | --- |
| 框架 | Vue 3.5 | 单页应用、组合式 API、组件化页面 |
| 构建工具 | Vite 7 | 开发服务器、生产构建、代码拆分 |
| 路由 | Vue Router 4 | 多语言路由、前台 / 后台 / 商家端页面 |
| 状态管理 | Pinia 3 | 询盘篮、收藏夹、语言/货币 UI 状态 |
| HTTP 客户端 | Axios | 统一请求 Flask API |
| 样式 | Tailwind CSS 4 + 自定义 CSS | 响应式页面、后台管理界面、组件样式 |
| 动画 | GSAP + ScrollTrigger | 首页滚动动效、产品页交互、列表动效 |
| 图标 | lucide-vue-next | 导航、按钮、后台菜单图标 |
| 图片优化 | loading="lazy"、decoding="async"、缩略图 URL | 降低首屏和列表加载压力 |

前端入口：

```text
frontend/src/main.js
frontend/src/App.vue
frontend/src/router.js
frontend/src/api.js
```

### 2.2 后端技术栈

| 类型 | 技术 | 当前用途 |
| --- | --- | --- |
| Web 框架 | Flask 3.1 | REST API、文件访问、应用工厂 |
| ORM | Flask-SQLAlchemy 3 | MySQL 数据模型和查询 |
| 数据库驱动 | PyMySQL | Python 连接 MySQL |
| 跨域 | Flask-CORS | 本地开发和线上域名跨域 |
| 密码哈希 | Werkzeug Security | 用户密码哈希与校验 |
| WSGI | Gunicorn | Docker 生产运行后端 |
| 图片处理 | Pillow | 上传图片压缩、尺寸限制、格式优化 |
| OSS SDK | oss2 | 阿里云 OSS 上传、删除、读取 |

后端入口：

```text
backend/run.py
backend/app/__init__.py
backend/app/routes.py
backend/app/models.py
```

### 2.3 数据库和部署技术栈

| 类型 | 技术 | 当前用途 |
| --- | --- | --- |
| 数据库 | MySQL 8.0 | 商品、分类、用户、询盘、报价、消息等业务数据 |
| 容器编排 | Docker Compose | 一键启动 MySQL、后端、前端 Nginx |
| 前端服务 | Nginx | 静态资源、Vue History 路由回退、`/api` 反向代理 |
| 对象存储 | 本地上传目录 / 阿里云 OSS | 媒体库图片存储，可通过环境变量切换 |
| CDN / DNS | Cloudflare / 域名解析 | HTTPS、缓存、代理、防护 |

生产容器：

```text
misicheng-mysql
misicheng-backend
misicheng-frontend
```

## 3. 系统架构

### 3.1 线上请求链路

```text
用户浏览器
  |
  | HTTPS
  v
Cloudflare / DNS / CDN
  |
  v
服务器 Nginx 或前端容器端口
  |
  | 静态资源 / Vue App
  v
frontend Nginx container
  |
  | /api/*
  v
backend Flask container
  |
  | SQLAlchemy / PyMySQL
  v
MySQL 8.0

媒体资源：
  本地模式：/api/uploads/*
  OSS 模式：MEDIA_PUBLIC_BASE_URL + media/*
```

### 3.2 前后端职责划分

前端负责：

- 页面渲染和交互。
- 多语言路由和语言包加载。
- 询盘篮、收藏夹、登录态在 `localStorage` 的持久化。
- 商品图片拖拽排序、商品列表拖拽排序、媒体库选择器等复杂交互。
- 调用后端 REST API。

后端负责：

- 商品、分类、Banner、用户、商家、询盘、报价、消息等业务数据。
- 管理员 / 商家 / 用户权限校验。
- 媒体上传、分类树维护、OSS 上传和远程删除。
- 产品规格模板保存和同步。
- 多语言 JSON 文件读取和后台编辑。
- 数据库兼容字段补齐和初始化。

## 4. 目录结构

```text
dulizhan2-vue-flask/
  backend/
    app/
      __init__.py                 Flask 应用工厂
      config.py                   后端环境变量配置
      extensions.py               SQLAlchemy 扩展
      models.py                   数据模型
      routes.py                   REST API 和业务逻辑
      media_storage.py            本地/OSS 媒体存储抽象
      i18n_messages.py            后台多语言管理
      spec_template_store.py      产品规格模板管理
      product_spec_template.json  默认规格模板
      seed.py                     初始化基础数据
      schema_compat.py            数据库兼容字段补齐
    Dockerfile
    requirements.txt
    run.py

  frontend/
    src/
      App.vue                     前台整体 Shell、导航、询盘抽屉
      main.js                     Vue 应用入口
      router.js                   多语言路由
      api.js                      API 请求封装
      i18n.js                     语言包加载和合并
      styles.css                  全局样式
      stores/                     Pinia 状态
      components/                 公共组件
      pages/                      前台、后台、商家端页面
      messages/                   多语言 JSON
    public/
      images/                     本地静态图片
    Dockerfile
    nginx.conf
    package.json

  database/
    schema.sql                    基础数据库创建脚本

  docker-compose.yml              生产/容器编排
  dulizhan_vue_flask_powerstrip.sql 当前排插项目数据库导出
  TECHNICAL_DOCUMENTATION.md      本文档
```

## 5. 前端路由设计

所有主要业务页面都带语言前缀：

```text
/:locale
/:locale/shop
/:locale/product/:slug
/:locale/inquiry
/:locale/account
/:locale/admin
/:locale/vendor
```

根路径 `/` 会自动跳转到用户上次选择的语言，默认英文：

```text
/ -> /en
```

后台和商家端非语言路径也会自动补全语言前缀：

```text
/admin -> /en/admin
/vendor -> /en/vendor
```

主要路由分组：

| 分组 | 路由 | 说明 |
| --- | --- | --- |
| 前台 | `/en`、`/en/shop`、`/en/product/:slug` | 首页、产品列表、产品详情 |
| 内容页 | `/en/about`、`/en/service`、`/en/faq`、`/en/blog`、`/en/contact` | 公司介绍、服务、FAQ、博客、联系 |
| 政策页 | `/en/shipping`、`/en/returns`、`/en/privacy`、`/en/terms` | 物流、退换、隐私、条款 |
| 账号 | `/en/login`、`/en/register`、`/en/account` | 登录注册、个人中心 |
| 询盘 | `/en/inquiry`、`/en/account/inquiries/:id` | 提交询盘、查看询盘详情 |
| 后台 | `/en/admin/*` | 管理员后台 |
| 商家 | `/en/vendor/*` | 商家工作台 |

## 6. 前端核心模块

### 6.1 前台模块

前台主要页面：

| 文件 | 功能 |
| --- | --- |
| `HomePage.vue` | 首页 Banner、分类入口、推荐商品、服务流程、FAQ |
| `ShopPage.vue` | 产品列表、筛选、分页、排序、悬浮筛选栏 |
| `ProductDetailPage.vue` | 商品详情、图片展示、规格参数、阶梯价格、询盘入口 |
| `InquiryPage.vue` | 询盘篮提交表单 |
| `InquiryDetailPage.vue` | 询盘详情、报价、消息沟通 |
| `WishlistPage.vue` | 收藏夹 |
| `AccountPage.vue` | 个人中心和密码修改入口 |
| `ContactPage.vue` | 联系我们和联系表单 |
| `ServicePage.vue` | 服务能力展示 |
| `FaqPage.vue` | 常见问题 |
| `BlogPage.vue` | 排插相关博客内容 |

产品卡片组件 `ProductCard.vue` 支持：

- 图片完整显示，不裁剪主体。
- 悬停切换图。
- 移动端固定标题字号，超出省略。
- 懒加载和异步解码。
- 加入收藏、进入详情、询盘相关入口。

### 6.2 询盘和收藏状态

询盘篮和收藏夹使用 Pinia + `localStorage`。

| Store | 文件 | 存储 Key |
| --- | --- | --- |
| 询盘篮 | `stores/inquiry.js` | `misicheng-inquiry-items:{owner}` |
| 收藏夹 | `stores/wishlist.js` | `misicheng-wishlist-items:{owner}` |
| UI 状态 | `stores/ui.js` | `misicheng-locale`、`misicheng-currency` |

`owner` 会根据当前登录用户隔离：

```text
guest
user:{userId 或 email}
```

因此游客、普通用户、不同用户之间的询盘篮和收藏夹不会混在一起。

### 6.3 管理员后台

后台统一由 `AdminPage.vue` 承载，通过路由判断当前 section。

主要功能：

- 仪表盘：统计商品、询盘、客户、趋势等数据。
- 商品管理：新增、编辑、删除、审核、拖拽排序、图片拖拽排序。
- 商品审核：商家提交商品后进入 `PENDING_REVIEW`，管理员可通过或驳回。
- 模板设置：配置商品规格字段和候选值，只影响字段结构和前台展示，不覆盖已填写的值。
- 分类管理：产品分类新增、编辑、排序、多语言名称。
- Banner 管理：首页 Banner 图片、标题、按钮、链接和排序。
- 商家审核：审核商家入驻申请。
- 询盘管理：查看询盘、更新状态、创建报价、回复消息。
- 客户管理：管理普通用户和商家账号的邮箱、密码、角色和启停状态。
- 管理员管理：高级管理员以上可添加和编辑管理员；最高管理员可删除管理员。
- 媒体库：管理员共享媒体库，支持批量上传、分类树、子分类、删除分类、图片改分类。
- 多语言管理：在线编辑语言包。
- 联系消息：查看联系表单提交内容。
- 修改密码：管理员使用原密码修改自己的密码。

后台商品图片规则：

```text
展示图 sortOrder: 0, 1, 2...
详情海报图 sortOrder: 100, 101, 102...
```

这样后端只用一张 `product_images` 表，前端根据 `sortOrder` 区分展示区域。

### 6.4 商家工作台

商家端由 `VendorWorkspacePage.vue` 承载。

主要功能：

- 商家入驻状态查看。
- 商家资料和认证文件提交。
- 审核通过后新增和编辑商品。
- 商品状态跟踪：草稿、待审核、已上架、已驳回。
- 商品列表拖拽排序。
- 商品图片批量上传、媒体库选择、拖拽排序。
- 商家独立媒体库：每个商家账号单独隔离。
- 媒体分类树：支持中英文分类名、主分类、子分类、删除分类、图片重新分类。
- 修改商家账号密码。

### 6.5 多语言模块

语言包位置：

```text
frontend/src/messages/en.json
frontend/src/messages/zh.json
frontend/src/messages/ja.json
frontend/src/messages/ko.json
frontend/src/messages/fr.json
frontend/src/messages/de.json
frontend/src/messages/es.json
frontend/src/messages/ar.json
```

加载逻辑：

- 英文和中文随主包直接加载。
- 日语、韩语、法语、德语、西语、阿语通过动态 import 加载。
- 生产环境还会尝试请求 `/messages/{locale}.json`，便于后台多语言修改后无需重新构建即可生效。
- `/messages/` 在 Nginx 中设置为 `no-store`，避免语言包修改后被缓存。

后台多语言管理使用：

```text
backend/app/i18n_messages.py
```

它会把嵌套 JSON 扁平化成 `namespace.key` 形式，便于后台列表编辑，再保存回对应语言 JSON。

## 7. 权限模型

系统当前角色：

| 角色 | 说明 | 主要权限 |
| --- | --- | --- |
| `USER` | 普通客户 | 浏览、收藏、提交询盘、查看自己的询盘、改密码 |
| `VENDOR` | 商家账号 | 商家入驻、商家商品管理、商家媒体库、改密码 |
| `ADMIN` | 普通管理员 | 仪表盘、商品管理/审核、商家审核、询盘管理、联系消息、媒体库 |
| `SENIOR_ADMIN` | 高级管理员 | 拥有高级后台功能，可管理普通管理员，但不能删除管理员 |
| `SUPER_ADMIN` | 最高管理员 | 全部权限，可添加、编辑、启停和删除管理员 |

后端权限函数集中在：

```text
backend/app/routes.py
```

核心函数：

```text
require_admin()
require_elevated_admin()
require_super_admin()
require_vendor()
can_access_inquiry()
```

权限边界：

- 普通客户只能访问自己的询盘。
- 商家只能访问自己的商家商品和自己的媒体库。
- 管理员可以处理询盘、商家审核和商品审核。
- 高级管理员可进入客户管理、管理员管理、多语言、分类、Banner、模板设置等高级功能。
- 最高管理员额外拥有删除管理员权限。
- 后台客户页面不显示管理员账号，管理员账号由独立管理员管理模块维护。

## 8. 数据模型

数据模型定义在：

```text
backend/app/models.py
```

核心表：

| 表 | 说明 |
| --- | --- |
| `users` | 用户、商家、管理员统一账号表 |
| `vendor_applications` | 商家入驻申请 |
| `categories` | 商品分类 |
| `category_translations` | 分类多语言 |
| `products` | 商品主表 |
| `product_translations` | 商品多语言 |
| `product_images` | 商品展示图和海报图 |
| `product_variants` | 商品 SKU / 规格变体 |
| `reviews` | 商品评价数据 |
| `banners` | 首页 Banner |
| `banner_translations` | Banner 多语言 |
| `inquiries` | 询盘主表 |
| `inquiry_items` | 询盘商品明细 |
| `inquiry_messages` | 询盘沟通消息 |
| `quotes` | 后台报价单 |
| `quote_items` | 报价明细 |
| `notifications` | 后台和用户通知 |
| `contact_messages` | 联系表单消息 |
| `subscribers` | 订阅邮箱 |

### 8.1 商品状态

| 状态 | 说明 |
| --- | --- |
| `DRAFT` | 草稿 |
| `PENDING_REVIEW` | 待审核 |
| `ACTIVE` | 已上架 |
| `REJECTED` | 已驳回 |

商家提交或修改商品后，商品会进入待审核状态。管理员审核通过后前台可展示。

### 8.2 商家入驻状态

| 状态 | 说明 |
| --- | --- |
| `PENDING` | 待审核 |
| `APPROVED` | 已通过 |
| `REJECTED` | 已驳回 |

商家账号本身在注册时创建，是否能发布商品由入驻申请状态控制。

### 8.3 询盘状态

| 状态 | 说明 |
| --- | --- |
| `SUBMITTED` | 客户已提交 |
| `PROCESSING` | 后台处理中 |
| `QUOTED` | 已报价 |
| `ACCEPTED` | 客户接受报价 |
| `REJECTED` | 客户拒绝报价 |
| `CANCELLED` | 已取消 |

询盘支持管理员和客户双方消息沟通，并支持管理员创建和更新报价。

### 8.4 产品规格模板

规格模板由文件维护：

```text
backend/app/product_spec_template.json
backend/app/product_spec_template.local.json
```

处理逻辑：

- 默认模板来自 `product_spec_template.json`。
- 后台保存后的模板写入 `product_spec_template.local.json`。
- 模板设置只同步“字段、分组、候选值、展示结构”。
- 已填写的商品规格值不会被模板覆盖。
- 已彻底移除定制选项相关字段，前台不再显示定制选项模块。

## 9. API 设计

API 前缀：

```text
/api
```

前端封装文件：

```text
frontend/src/api.js
```

### 9.1 公共接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | 健康检查 |
| GET | `/uploads/<path>` | 本地上传文件访问 |
| GET | `/home` | 首页数据：Banner、分类、推荐商品 |
| GET | `/categories` | 前台分类列表 |
| GET | `/products` | 前台商品列表、筛选、排序 |
| GET | `/products/<slug>` | 商品详情 |
| GET | `/search` | 商品搜索 |
| GET | `/spec-template` | 前台规格模板 |
| POST | `/contact` | 提交联系表单 |
| POST | `/newsletter` | 邮箱订阅 |

### 9.2 账号接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/auth/login` | 登录，支持普通用户、商家、管理员 |
| POST | `/auth/register` | 普通用户注册 |
| POST | `/auth/vendor-register` | 商家注册并提交入驻信息 |
| POST | `/auth/change-password` | 当前登录账号修改密码 |

### 9.3 通知接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/notifications` | 获取通知 |
| POST | `/notifications/read` | 标记通知已读 |

### 9.4 商家接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/vendor/application-upload` | 上传入驻证明文件 |
| GET | `/vendor/application` | 获取当前商家入驻状态 |
| GET | `/vendor/products` | 获取当前商家商品 |
| POST | `/vendor/products` | 新增商家商品 |
| PATCH | `/vendor/products/<product_id>` | 修改商家商品 |
| PATCH | `/vendor/products/reorder` | 商家商品拖拽排序 |
| GET | `/vendor/media` | 商家媒体库 |
| POST | `/vendor/media` | 商家媒体上传 |
| PATCH | `/vendor/media` | 商家媒体改分类 |
| DELETE | `/vendor/media` | 删除商家媒体 |
| POST | `/vendor/media/categories` | 新增商家媒体分类 |
| DELETE | `/vendor/media/categories` | 删除商家媒体分类 |

### 9.5 询盘接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/inquiries` | 当前用户或管理员可见询盘列表 |
| POST | `/inquiries` | 创建询盘 |
| GET | `/inquiries/<inquiry_id>` | 询盘详情 |
| PATCH | `/inquiries/<inquiry_id>` | 更新询盘状态 |
| GET | `/inquiries/<inquiry_id>/messages` | 询盘消息 |
| POST | `/inquiries/<inquiry_id>/messages` | 发送询盘消息 |
| POST | `/inquiries/<inquiry_id>/quotes` | 管理员创建报价 |
| PATCH | `/inquiries/<inquiry_id>/quotes/<quote_id>` | 管理员修改报价 |

### 9.6 管理员接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/admin/analytics` | 仪表盘统计 |
| GET | `/admin/products` | 后台商品列表 |
| POST | `/admin/products` | 后台新增商品 |
| PATCH | `/admin/products/<product_id>` | 后台修改 / 审核商品 |
| DELETE | `/admin/products/<product_id>` | 删除商品 |
| PATCH | `/admin/products/reorder` | 后台商品拖拽排序 |
| GET | `/admin/spec-template` | 获取后台规格模板 |
| PUT | `/admin/spec-template` | 保存规格模板并同步字段 |
| GET | `/admin/categories` | 分类列表 |
| POST | `/admin/categories` | 新增分类 |
| PATCH | `/admin/categories/<category_id>` | 修改分类 |
| GET | `/admin/banners` | Banner 列表 |
| POST | `/admin/banners` | 新增 Banner |
| PATCH | `/admin/banners/<banner_id>` | 修改 Banner |
| GET | `/admin/vendors` | 商家入驻申请列表 |
| PATCH | `/admin/vendors/<application_id>` | 审核商家入驻 |
| GET | `/admin/inquiries` | 后台询盘列表 |
| GET | `/admin/inquiries/<inquiry_id>` | 后台询盘详情 |
| POST | `/admin/inquiries/<inquiry_id>/messages` | 后台回复询盘 |
| POST | `/admin/inquiries/<inquiry_id>/quotes` | 后台创建报价 |
| GET | `/admin/users` | 客户账号列表 |
| PATCH | `/admin/users/<user_id>` | 修改客户邮箱、角色、密码、启停 |
| GET | `/admin/admins` | 管理员列表 |
| POST | `/admin/admins` | 新增管理员 |
| PATCH | `/admin/admins/<admin_id>` | 修改管理员邮箱、密码、等级、启停 |
| DELETE | `/admin/admins/<admin_id>` | 删除管理员，仅最高管理员 |
| GET | `/admin/media` | 管理员共享媒体库 |
| POST | `/admin/media` | 上传管理员媒体 |
| PATCH | `/admin/media` | 管理员媒体改分类 |
| DELETE | `/admin/media` | 删除管理员媒体 |
| POST | `/admin/media/categories` | 新增管理员媒体分类 |
| DELETE | `/admin/media/categories` | 删除管理员媒体分类 |
| GET | `/admin/i18n` | 获取多语言编辑数据 |
| PUT | `/admin/i18n` | 保存语言包 |
| GET | `/admin/contacts` | 联系消息列表 |

## 10. 媒体库与 OSS

媒体存储抽象在：

```text
backend/app/media_storage.py
```

支持两种模式：

| 模式 | 环境变量 | 说明 |
| --- | --- | --- |
| 本地模式 | `MEDIA_STORAGE_PROVIDER=local` | 上传到后端容器挂载目录，通过 `/api/uploads/*` 访问 |
| OSS 模式 | `MEDIA_STORAGE_PROVIDER=aliyun_oss` | 上传到阿里云 OSS，通过自定义图片域名访问 |

媒体库隔离规则：

| 类型 | 存储逻辑 |
| --- | --- |
| 管理员媒体库 | 所有管理员共享同一套媒体库 |
| 商家媒体库 | 每个商家账号独立媒体库 |
| 产品引用 | 商品图片存 URL，删除或移动媒体时会同步更新相关商品引用 |

媒体库功能：

- 批量上传图片。
- 保留本地文件原始名称作为上传后名称。
- 上传时可选择分类。
- 分类支持中英文名称。
- 分类树支持主分类和子分类。
- 可删除分类，分类下图片会移动到未分类或根目录。
- 点击图片可预览，并重新选择分类。
- 管理员和商家的产品编辑页面都支持从媒体库批量选择展示图和海报图。

图片优化：

- 上传图片可通过 Pillow 自动压缩。
- 最大边长由 `MEDIA_IMAGE_MAX_SIDE` 控制，默认 1920。
- JPEG / WebP 质量由环境变量控制。
- OSS 模式下缩略图会自动追加 `x-oss-process` 参数生成 WebP 缩略图。

关键环境变量：

```text
MEDIA_STORAGE_PROVIDER
MEDIA_PUBLIC_BASE_URL
ALIYUN_OSS_BUCKET
ALIYUN_OSS_ENDPOINT
ALIYUN_OSS_ACCESS_KEY_ID
ALIYUN_OSS_ACCESS_KEY_SECRET
MEDIA_IMAGE_OPTIMIZE
MEDIA_IMAGE_MAX_SIDE
MEDIA_IMAGE_JPEG_QUALITY
MEDIA_IMAGE_WEBP_QUALITY
```

## 11. 缓存和性能设计

### 11.1 前端性能

当前前端性能策略：

- Vue Router 页面级动态导入，后台、商家端、产品页等按需加载。
- Vite 生产构建输出带 hash 的资源文件。
- 产品图片使用 `loading="lazy"` 和 `decoding="async"`。
- 产品卡片使用 `IntersectionObserver` 延迟处理部分显示逻辑。
- 首页和产品列表的动效使用 GSAP transform，减少布局抖动。
- 产品列表前端分页，网格模式每页显示更多商品。
- 产品展示图使用 `object-contain`，避免裁剪图片主体。

### 11.2 Nginx 缓存策略

前端 Nginx 配置在：

```text
frontend/nginx.conf
```

缓存策略：

| 路径 | 策略 |
| --- | --- |
| `/assets/` | `Cache-Control: public, immutable`，一年缓存 |
| `/images/` | 30 天缓存 |
| `/messages/` | `no-store`，语言包实时生效 |
| `/` | `no-store`，避免 HTML 缓存旧构建入口 |
| `/api/` | 反代 Flask，不做静态缓存 |

因为图片有较长缓存，替换同名图片后如果 CDN 或浏览器仍显示旧图，需要清理 CDN 缓存，或改图片文件名 / 查询参数触发新资源。

### 11.3 后端性能

后端优化点：

- 首页接口返回数据使用短缓存响应头，降低重复请求压力。
- 商品卡片数据使用 `to_card_dict()`，避免列表页返回过多详情数据。
- OSS 缩略图通过 `x-oss-process` 在访问层处理，不需要后端生成多份文件。
- 上传文件保存前压缩，降低后续访问体积。
- Docker 中前端由 Nginx 提供静态资源，Flask 只处理 API。

## 12. 本地开发

### 12.1 前置环境

建议环境：

```text
Node.js 20+
Python 3.11+
MySQL 8.0+
Docker Desktop 可选
```

### 12.2 数据库

创建数据库：

```sql
CREATE DATABASE IF NOT EXISTS dulizhan_vue_flask_powerstrip
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

如需导入当前排插项目数据：

```sql
SOURCE D:/suibian/Downloads/dulizhan2-vue-flask/dulizhan_vue_flask_powerstrip.sql;
```

开发环境也可以设置 `AUTO_CREATE_TABLES=true`，由 Flask 根据模型自动建表，并执行兼容字段补齐。

### 12.3 启动后端

```powershell
cd D:\suibian\Downloads\dulizhan2-vue-flask\backend
copy .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

后端默认地址：

```text
http://127.0.0.1:5000
```

### 12.4 启动前端

```powershell
cd D:\suibian\Downloads\dulizhan2-vue-flask\frontend
npm install
npm run dev
```

前端默认地址：

```text
http://127.0.0.1:5173/en
```

Vite 会把 `/api` 代理到 Flask：

```text
VITE_PROXY_TARGET=http://127.0.0.1:5000
```

## 13. Docker 部署

Docker 编排文件：

```text
docker-compose.yml
```

核心服务：

| 服务 | 说明 |
| --- | --- |
| `mysql` | MySQL 8.0，挂载 `mysql_data` |
| `backend` | Flask + Gunicorn，连接 MySQL，处理 API 和上传 |
| `frontend` | Nginx 托管 Vite 构建产物，反代 `/api` |

启动或更新：

```bash
docker compose up -d --build
```

只重建前端：

```bash
docker compose up -d --build frontend
```

只重建后端：

```bash
docker compose up -d --build backend
```

查看日志：

```bash
docker compose logs -f frontend
docker compose logs -f backend
docker compose logs -f mysql
```

线上前端容器监听：

```text
127.0.0.1:3000 -> frontend:80
```

服务器外层 Nginx 或反向代理负责把域名流量转发到本机 `3000`。

## 14. 环境变量

### 14.1 后端环境变量

| 变量 | 说明 |
| --- | --- |
| `SECRET_KEY` | Flask 密钥 |
| `DATABASE_URL` | MySQL 连接字符串 |
| `AUTO_CREATE_TABLES` | 是否自动建表 |
| `AUTO_SEED` | 是否自动初始化示例数据 |
| `CORS_ORIGINS` | 允许跨域的前端域名 |
| `MEDIA_STORAGE_PROVIDER` | 媒体存储模式：`local` 或 `aliyun_oss` |
| `MEDIA_PUBLIC_BASE_URL` | OSS 或 CDN 图片公开访问域名 |
| `ALIYUN_OSS_BUCKET` | OSS Bucket 名称 |
| `ALIYUN_OSS_ENDPOINT` | OSS Endpoint |
| `ALIYUN_OSS_ACCESS_KEY_ID` | OSS AccessKey ID |
| `ALIYUN_OSS_ACCESS_KEY_SECRET` | OSS AccessKey Secret |
| `MEDIA_IMAGE_OPTIMIZE` | 是否启用上传压缩 |
| `MEDIA_IMAGE_MAX_SIDE` | 上传图片最大边长 |
| `MEDIA_IMAGE_JPEG_QUALITY` | JPEG 压缩质量 |
| `MEDIA_IMAGE_WEBP_QUALITY` | WebP 压缩质量 |

### 14.2 前端环境变量

| 变量 | 说明 |
| --- | --- |
| `VITE_API_BASE_URL` | 前端请求 API 的基础路径，生产通常为 `/api` |
| `VITE_PROXY_TARGET` | 本地开发代理目标，默认 Flask 地址 |

## 15. 数据初始化和维护

初始化逻辑：

```text
backend/app/seed.py
```

用途：

- 创建基础管理员角色账号。
- 初始化排插相关分类、商品、Banner。
- 确保基础 Banner 多语言内容存在。
- 如果数据库已有分类，默认不会清空重建，只会补齐必要账号和 Banner 翻译。

数据库兼容逻辑：

```text
backend/app/schema_compat.py
```

用途：

- 在旧数据库上补齐新增字段。
- 创建报价相关表。
- 补充必要索引。

生产环境建议：

- `AUTO_SEED=false`，避免自动写入示例商品。
- 保留基础分类和必要管理员账号。
- 商品、普通用户、商家、询盘等业务数据根据正式运营重新录入。
- 管理员首次部署后应立即修改初始密码。

## 16. 安全设计和后续加固建议

当前实现：

- 密码使用 Werkzeug `generate_password_hash()` 存储，不保存明文密码。
- 登录后前端把用户摘要保存到 `localStorage`。
- API 请求携带 `userId` 和 `userEmail`，后端据此识别当前用户。
- 后端对管理员、商家和询盘访问做角色校验。
- 管理员密码、客户密码、商家密码均支持使用原密码修改。

后续建议：

- 将当前轻量登录态升级为服务端 Session 或 JWT。
- 对管理员后台增加 CSRF / 请求签名 / Token 过期机制。
- 对媒体上传增加更严格的文件体积、像素尺寸和 MIME 校验。
- 对登录接口增加失败次数限制和验证码。
- 将默认初始化密码改为部署时环境变量注入，避免固定值出现在代码中。
- 对后台关键操作增加审计日志，例如删除商品、删除管理员、修改客户角色。

## 17. 业务流程

### 17.1 客户询盘流程

```text
客户浏览商品
  -> 加入询盘篮
  -> 登录或注册
  -> 填写联系人、公司、数量、交期、备注
  -> 提交询盘
  -> 后台收到通知
  -> 管理员处理并创建报价
  -> 客户在个人中心查看报价
  -> 双方通过询盘消息继续沟通
  -> 客户接受或拒绝报价
```

### 17.2 商家入驻流程

```text
商家注册
  -> 填写公司资料和联系方式
  -> 上传认证文件
  -> 后台管理员审核
  -> 审核通过后商家可新增商品
  -> 商家商品提交审核
  -> 管理员审核商品
  -> 审核通过后商品进入前台展示
```

### 17.3 商品管理流程

```text
管理员或商家进入商品编辑
  -> 填写中英文标题、描述、价格、分类、规格、阶梯价
  -> 上传或从媒体库选择展示图和海报图
  -> 拖拽调整图片顺序
  -> 保存商品
  -> 后台同步规格模板字段
  -> 根据角色决定直接上架或进入审核
```

### 17.4 媒体库流程

```text
进入媒体库
  -> 新增中英文分类或子分类
  -> 选择上传分类
  -> 批量上传图片
  -> 图片自动压缩并保存原始文件名
  -> 点击图片可预览、删除或重新分类
  -> 产品编辑时从媒体库批量选择图片
```

## 18. 构建和验证

前端构建：

```powershell
cd D:\suibian\Downloads\dulizhan2-vue-flask\frontend
npm run build
```

后端基本检查：

```powershell
cd D:\suibian\Downloads\dulizhan2-vue-flask\backend
python run.py
```

线上健康检查：

```bash
curl https://misicheng.cn/api/health
```

静态资源检查：

```bash
curl -I https://misicheng.cn/assets/
curl -I https://misicheng.cn/images/hero-banner.png
```

语言包检查：

```bash
curl -I https://misicheng.cn/messages/en.json
curl -I https://misicheng.cn/messages/zh.json
```

## 19. 维护注意事项

- 修改前端页面后需要重新 `npm run build` 或重新构建前端 Docker 镜像。
- 修改后端 Python 代码后需要重建或重启后端容器。
- 修改 `frontend/src/messages/*.json` 后，线上通过 `/messages/*.json` 挂载可实时生效，但前端构建包内的 fallback 语言仍需下次构建更新。
- 替换同名 `/images/*` 图片后，可能需要清 Cloudflare 和浏览器缓存。
- OSS AccessKey 必须只放在服务器环境变量或 `.env` 中，不要写入代码仓库和展示文档。
- 数据库导出文件可能包含历史测试数据，交付或演示前应确认是否需要脱敏。
- 删除媒体、移动媒体分类会同步产品引用，操作前建议备份数据库和上传目录。
- 商品模板设置不会覆盖已填写值，但会影响后台可编辑字段和前台展示字段。

## 20. 当前项目特点总结

本项目不是简单静态展示站，而是一套完整的 B2B 独立站业务系统：

- 前台展示和询盘转化完整。
- 普通用户、商家、管理员三端统一。
- 商家入驻和商品审核流程完整。
- 后台具备商品、分类、Banner、询盘、报价、客户、管理员、多语言、媒体库管理。
- 支持管理员三级权限。
- 支持 8 语言和 RTL。
- 支持本地媒体和阿里云 OSS 两种存储。
- 支持媒体分类树、批量上传、图片重新分类和商品图片批量选择。
- 支持 Docker Compose 容器化部署。
- 已针对图片加载、静态资源缓存、OSS 缩略图和页面代码拆分做性能优化。
