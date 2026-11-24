# Dulizhan2：Vue3 + Flask + MySQL

这是原 `dulizhan2` 独立站的前后端重构版本：前端 Vue 3，后端 Flask，数据库 MySQL。

## 目录结构

- `frontend/` —— Vue 3、Vite、Vue Router、Pinia、Axios、lucide 图标
- `backend/` —— Flask、Flask-SQLAlchemy、PyMySQL、Flask-CORS
- `database/schema.sql` —— 数据库初始化脚本

## 数据库

先建库，再导入表结构：

```sql
CREATE DATABASE IF NOT EXISTS dulizhan_vue_flask_powerstrip
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

```powershell
mysql -uroot -proot dulizhan_vue_flask_powerstrip < database\schema.sql
```

也可以不导入：后端 `.env` 里把 `AUTO_CREATE_TABLES=true`、`AUTO_SEED=true` 打开，首次启动会自动建表并写入演示数据。

## 后端

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

- 端口取 `.env` 的 `PORT`，默认 `5005`
- 本机 MySQL 若密码不同，改 `DATABASE_URL`
- 图片默认存本地 `MEDIA_STORAGE_PROVIDER=local`，也可切阿里云 OSS（填 `ALIYUN_OSS_*`）

## 前端

```powershell
cd frontend
npm install
npm run dev
```

默认地址 `http://localhost:5173`。`vite.config.js` 把 `/api` 代理到 `VITE_PROXY_TARGET` 或默认的 `http://127.0.0.1:5005`，可以用 `frontend/.env` 覆盖。

## 演示数据

开启 `AUTO_CREATE_TABLES` + `AUTO_SEED` 后，首次启动会写入：

- 12 个插排 / 插座分类
- 72 个产品
- 首页 banner
- 产品图、规格变体、评价
- 管理员账号：`admin@misicheng.local` / `admin123456`

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + Pinia + Vue Router |
| 后端 | Flask + Flask-SQLAlchemy + PyMySQL |
| 数据库 | MySQL 8（utf8mb4） |
