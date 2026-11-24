import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # 端口可在 backend/.env 中用 PORT 覆盖（默认 5005，对应前端 vite 代理）
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5005")), debug=True)
