# Dulizhan2：外贸独立站（Vue3 + Flask + MySQL）

一个**以视觉与交互设计为主**的外贸 B2B/B2C 独立站：前台是自建设计系统的品牌站（悬浮玻璃导航、滚动叙事动效、8 语言），后台覆盖商品、询盘、报价、供应商与管理员等多角色业务。

> 和同目录下的 `muban` 是两条路线：**dulizhan2 卖的是「看起来像品牌官网」的观感与交互**，muban 卖的是「拿来就能跑业务」的 B2B 模板。详细对比见下一节。

## 与 muban 的区别

| 维度 | **dulizhan2-vue-flask**（本仓库） | **muban** |
|---|---|---|
| 定位 | 品牌独立站，**视觉 / 交互先行** | B2B/B2C 可复用模板，**功能先行** |
| 前端技术 | Vue 3 + **Tailwind 4** + 自定义设计 token | Vue 3 + **Element Plus** 组件库 |
| 视觉体系 | 自建：语义色变量、圆角梯度（`--radius-sm` → `--radius-4xl`）、暗色变体、渐变品牌字 | 沿用 Element Plus 默认风格 |
| 动效 | **GSAP + ScrollTrigger** 滚动叙事（`.reveal-section` 区块入场、`.service-row` 逐条错峰），导航栏跟随鼠标做 3D 倾斜 | 无滚动动画（gsap 使用 0 处） |
| 导航形态 | 悬浮胶囊 + `backdrop-blur` 玻璃质感，移动端独立浮头 + 抽屉 | 常规顶部导航 |
| 页面量 | 22 个页面，含 182KB 管理后台、108KB 供应商工作台 | 11 个页面 |
| 业务形态 | 管理员 / 供应商 / 买家多角色 + 询盘、报价单、愿望单 | 商品列表详情、买家注册、工厂入驻询盘、清关、物流、条款 |
| 多语言 | 8 语言（en/zh 内置，ja/ko/fr/de/es/ar 懒加载） | vue-i18n（中英为主） |
| 适合谁 | 要「品牌感」的外贸官网、给客户看设计 | 要快速起一个能跑业务的 B2B 站 |

## UI 与交互设计拆解

### 1. 自建设计系统（不是套组件库）

`frontend/src/styles.css` 用 Tailwind 4 的 `@theme inline` + CSS 变量定义语义化 token：

```css
--color-background / --color-foreground / --color-primary / --color-muted / --color-border …
--radius-sm: calc(var(--radius) - 4px)   /* 一路到 --radius-4xl */
@custom-variant dark (&:is(.dark *));    /* 预留暗色 */
```

好处是换主题只改变量，不改组件；也不受某个 UI 库的视觉风格限制。

### 2. 悬浮玻璃导航 + 鼠标跟随倾斜

`App.vue` 里桌面端导航是固定居中的胶囊：`rounded-2xl`、`bg-white/80`、`backdrop-blur-xl`、大范围柔和阴影；移动端是独立的浮动条 + 抽屉菜单。桌面端还实现了**跟随鼠标的轻微 3D 倾斜**（`headerTiltStyle` + `handleHeaderMouseMove` / `resetHeaderTilt`），鼠标移出自动回正。

### 3. 滚动叙事动效

首页用 GSAP + ScrollTrigger：`.reveal-section` 区块进入视口时上浮淡入，`.service-row` 按索引逐条错峰出现（`index` 参与延迟计算）。动效写在 `gsap.context()` 里，组件卸载时统一 `revert()`，不会残留。

### 4. 业务型微交互

- `ProductCard.vue` 商品卡：图片悬浮、价格/规格切换
- `QuoteEditDialog.vue` 报价单编辑弹窗：供应商侧改价、改交期
- `MessagePanel.vue` + `NotificationBell.vue`：站内消息与未读提醒
- `AdminShell.vue` / `VendorShell.vue`：管理端与供应商端两套壳，导航与权限不同
- `SectionHeading.vue`：统一的标题排版组件，保证全站节奏一致

### 5. 可访问性与多语言

- `skip-to-content` 跳转链接、按钮 `aria-label`、键盘焦点可见
- 路由带语言前缀（`/en/...`、`/zh/...`），`i18n.js` 对 6 种语言做动态 import，首屏只加载当前语言

## 页面清单（22 个）

| 模块 | 页面 |
|---|---|
| 前台 | `HomePage`、`ShopPage`、`ProductDetailPage`、`AboutPage`、`ServicePage`、`ContactPage`、`BlogPage`、`FaqPage`、`PolicyPage` |
| 交易 | `AuthPage`、`AccountPage`、`AccountOrdersPage`、`WishlistPage`、`InquiryPage`、`InquiryDetailPage` |
| 供应商 | `VendorApplicationPage`、`VendorDashboardPage`、`VendorPanel`、`VendorWorkspacePage` |
| 管理 | `AdminPage`、`AdminDashboard`、`ForgotPasswordPage` |

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3.5、Vite 7、**Tailwind CSS 4**、**GSAP 3 + ScrollTrigger**、Pinia、Vue Router、lucide 图标 |
| 后端 | Flask、Flask-SQLAlchemy、PyMySQL、Flask-CORS |
| 数据库 | MySQL 8（utf8mb4） |
| 其他 | i18n（8 语言）、阿里云 OSS 可选（图片） |

## 本地运行

### 数据库

```sql
CREATE DATABASE IF NOT EXISTS dulizhan_vue_flask_powerstrip
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

也可以跳过：后端 `.env` 里 `AUTO_CREATE_TABLES=true`、`AUTO_SEED=true` 时首次启动自动建表 + 写入演示数据。

### 后端

```powershell
cd backend
copy .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

`.env` 关键项：

```env
DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/dulizhan_vue_flask_powerstrip?charset=utf8mb4
PORT=5005
AUTO_CREATE_TABLES=true
AUTO_SEED=true
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 前端

```powershell
cd frontend
npm install
npm run dev
```

打开 <http://localhost:5173>。`/api` 由 Vite 代理到 `VITE_PROXY_TARGET`（默认 `http://127.0.0.1:5005`）。

## 演示数据

首次启动写入：12 个插排/插座分类、72 个产品、首页 banner、产品图与规格变体、评价；管理员账号 `admin@misicheng.local` / `admin123456`。
