import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:root@127.0.0.1:3306/dulizhan_vue_flask_powerstrip?charset=utf8mb4",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true"
    AUTO_SEED = os.getenv("AUTO_SEED", "false").lower() == "true"
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]
