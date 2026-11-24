# Dulizhan2 Vue + Flask + MySQL

This is a Vue 3 + Flask + MySQL rebuild of the original `dulizhan2` storefront. The original project is left untouched; this version lives in `D:\suibian\Downloads\dulizhan2-vue-flask`.

## Structure

- `frontend/` - Vue 3, Vite, Vue Router, Pinia, Axios, lucide icons
- `backend/` - Flask, Flask-SQLAlchemy, PyMySQL, Flask-CORS
- `database/schema.sql` - MySQL database bootstrap

## MySQL

Create the database first:

```sql
SOURCE D:/suibian/Downloads/dulizhan2-vue-flask/database/schema.sql;
```

Or run the SQL in your MySQL client:

```sql
CREATE DATABASE IF NOT EXISTS dulizhan_vue_flask
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

## Backend

```powershell
cd D:\suibian\Downloads\dulizhan2-vue-flask\backend
copy .env.example .env
```

Edit `.env` if your local MySQL password is different. The current local setup uses `root` / `root`:

```env
DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/dulizhan_vue_flask?charset=utf8mb4
AUTO_CREATE_TABLES=true
AUTO_SEED=true
```

Install and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

The backend runs at `http://127.0.0.1:5000`.

## Frontend

```powershell
cd D:\suibian\Downloads\dulizhan2-vue-flask\frontend
npm install
npm run dev
```

The frontend runs at `http://127.0.0.1:5173/en` and proxies `/api` to Flask.

## Seed Data

With `AUTO_CREATE_TABLES=true` and `AUTO_SEED=true`, Flask creates tables and inserts sample storefront data on first startup:

- 12 plug/socket categories
- 72 products
- hero banners
- product images, variants, and reviews
- admin user: `admin@misicheng.local` / `admin123456`
