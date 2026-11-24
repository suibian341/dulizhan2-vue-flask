from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.seed import seed_database

app = create_app()

with app.app_context():
    seed_database(force=True)
    print("Seed completed.")
