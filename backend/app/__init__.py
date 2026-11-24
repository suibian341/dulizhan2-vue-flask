from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import db
from .routes import api
from .schema_compat import ensure_compatible_schema
from .seed import seed_database


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)
    app.register_blueprint(api)

    with app.app_context():
        if app.config["AUTO_CREATE_TABLES"]:
            db.create_all()
            ensure_compatible_schema()
            if app.config["AUTO_SEED"]:
                seed_database(force=False)

    return app
