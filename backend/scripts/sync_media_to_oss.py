import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app import create_app
from app.extensions import db
from app.media_storage import (
    IMAGE_EXTENSIONS,
    aliyun_oss_enabled,
    media_public_url,
    media_storage_provider,
    normalize_media_key,
    optimize_image_bytes,
    upload_remote_media,
)
from app.models import Banner, Category, ProductImage, Review


UPLOAD_ROOT = BACKEND_ROOT / "uploads"
MEDIA_ROOT = UPLOAD_ROOT / "media"


def iter_media_files():
    if not MEDIA_ROOT.exists():
        return
    for path in MEDIA_ROOT.rglob("*"):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower().lstrip(".") in IMAGE_EXTENSIONS:
            yield path


def is_local_upload_url(value):
    text = str(value or "").strip()
    if text.startswith("/api/uploads/") or text.startswith("api/uploads/"):
        return True
    if text.startswith(("http://", "https://")):
        return urlparse(text).path.startswith("/api/uploads/")
    return False


def rewrite_local_media_url(value):
    if not isinstance(value, str) or not value or not is_local_upload_url(value):
        return value, False
    key = normalize_media_key(value)
    if not key.startswith("media/"):
        return value, False
    rewritten = media_public_url(key)
    return rewritten, rewritten != value


def rewrite_json_urls(value):
    changed = False
    if isinstance(value, list):
        items = []
        for item in value:
            new_item, item_changed = rewrite_json_urls(item)
            items.append(new_item)
            changed = changed or item_changed
        return items, changed
    if isinstance(value, dict):
        row = {}
        for key, item in value.items():
            if isinstance(item, str):
                row[key], item_changed = rewrite_local_media_url(item)
            else:
                row[key], item_changed = rewrite_json_urls(item)
            changed = changed or item_changed
        return row, changed
    return value, False


def sync_files(dry_run=False):
    stats = {"files": 0, "optimized": 0, "uploaded": 0, "bytesBefore": 0, "bytesAfter": 0}
    for path in iter_media_files() or []:
        key = path.relative_to(UPLOAD_ROOT).as_posix()
        original = path.read_bytes()
        payload = optimize_image_bytes(original, path.name)
        stats["files"] += 1
        stats["bytesBefore"] += payload.original_size
        stats["bytesAfter"] += payload.stored_size
        if payload.optimized:
            stats["optimized"] += 1
        if not dry_run:
            if payload.optimized:
                path.write_bytes(payload.data)
            upload_remote_media(key, payload.data, payload.content_type)
        stats["uploaded"] += 1
    return stats


def rewrite_database_urls(dry_run=False):
    stats = {"productImages": 0, "banners": 0, "categories": 0, "reviews": 0}

    for row in ProductImage.query.all():
        rewritten, changed = rewrite_local_media_url(row.url)
        if changed:
            row.url = rewritten
            stats["productImages"] += 1

    for row in Banner.query.all():
        rewritten, changed = rewrite_local_media_url(row.image)
        if changed:
            row.image = rewritten
            stats["banners"] += 1

    for row in Category.query.all():
        rewritten, changed = rewrite_local_media_url(row.image)
        if changed:
            row.image = rewritten
            stats["categories"] += 1

    for row in Review.query.all():
        rewritten, changed = rewrite_json_urls(row.images or [])
        if changed:
            row.images = rewritten
            stats["reviews"] += 1

    if not dry_run and any(stats.values()):
        db.session.commit()
    elif dry_run:
        db.session.rollback()
    return stats


def main():
    parser = argparse.ArgumentParser(description="Sync local media uploads to Aliyun OSS.")
    parser.add_argument("--dry-run", action="store_true", help="Scan and report without uploading or rewriting DB.")
    parser.add_argument("--rewrite-db", action="store_true", help="Rewrite local upload URLs in image-related tables.")
    args = parser.parse_args()

    if media_storage_provider() != "aliyun_oss" or not aliyun_oss_enabled():
        raise SystemExit("Aliyun OSS storage is not fully configured in environment variables.")

    app = create_app()
    with app.app_context():
        file_stats = sync_files(dry_run=args.dry_run)
        db_stats = rewrite_database_urls(dry_run=args.dry_run) if args.rewrite_db else {}

    print({"files": file_stats, "database": db_stats, "dryRun": args.dry_run})


if __name__ == "__main__":
    main()
