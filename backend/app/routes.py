from datetime import datetime
import copy
import json
from math import ceil
from pathlib import Path
import re
import shutil
from uuid import uuid4

from flask import Blueprint, jsonify, request, send_from_directory
from sqlalchemy import or_, text
from sqlalchemy.orm import joinedload, selectinload
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db
from .i18n_messages import LOCALES, get_admin_i18n_data, update_admin_locale_messages
from .media_storage import (
    aliyun_oss_bucket,
    aliyun_oss_enabled,
    content_type_for_key,
    delete_remote_media,
    media_public_url,
    media_variant_url,
    media_storage_provider,
    media_url_candidates,
    normalize_media_key,
    prepare_media_upload,
    upload_remote_media,
)
from .spec_template_store import load_spec_template, merge_specs_with_template, save_spec_template, without_customization_specs
from .models import (
    Banner,
    BannerTranslation,
    Category,
    CategoryTranslation,
    ContactMessage,
    Inquiry,
    InquiryItem,
    InquiryMessage,
    Notification,
    Product,
    ProductImage,
    ProductVariant,
    ProductTranslation,
    Quote,
    QuoteItem,
    VendorApplication,
    Subscriber,
    User,
)

api = Blueprint("api", __name__, url_prefix="/api")
UPLOAD_ROOT = Path(__file__).resolve().parents[1] / "uploads"
ALLOWED_VENDOR_FILE_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "webp"}
ALLOWED_PRODUCT_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
MAX_MEDIA_UPLOAD_BYTES = 10 * 1024 * 1024
MEDIA_CATEGORY_FILE = ".categories.json"
MEDIA_CATEGORY_RESERVED_VALUES = {"all", "__all__", "uncategorized", "__uncategorized__"}
MEDIA_CATEGORY_DEFAULTS = {
    "general": {"nameEn": "General", "nameZh": "通用素材", "sortOrder": 10},
    "products": {"nameEn": "Product images", "nameZh": "商品图片", "sortOrder": 20},
    "posters": {"nameEn": "Detail posters", "nameZh": "详情海报", "sortOrder": 30},
    "banners": {"nameEn": "Banners", "nameZh": "横幅图片", "sortOrder": 40},
    "categories": {"nameEn": "Category images", "nameZh": "分类图片", "sortOrder": 50},
}
ADMIN_MEDIA_CATEGORY_PRESETS = []
VENDOR_MEDIA_CATEGORY_PRESETS = []
ADMIN_SHARED_MEDIA_PARTS = ("media", "admin")
ADMIN_LEGACY_MEDIA_ROOT_PARTS = ("media", "admins")
ADMIN_SHARED_MIGRATION_MARKER = ".admin-shared-media-migrated"
SUPER_ADMIN_ROLE = "SUPER_ADMIN"
SENIOR_ADMIN_ROLE = "SENIOR_ADMIN"
BASIC_ADMIN_ROLE = "ADMIN"
ADMIN_ROLES = {BASIC_ADMIN_ROLE, SENIOR_ADMIN_ROLE, SUPER_ADMIN_ROLE}
ELEVATED_ADMIN_ROLES = {SENIOR_ADMIN_ROLE, SUPER_ADMIN_ROLE}
ASSIGNABLE_ADMIN_ROLES = {BASIC_ADMIN_ROLE, SENIOR_ADMIN_ROLE}
CUSTOMER_ROLES = {"USER", "VENDOR"}


def get_locale():
    return request.args.get("locale") or request.headers.get("Accept-Language", "en")[:2]


def public_product_load_options(include_reviews=False):
    options = [
        selectinload(Product.translations),
        selectinload(Product.images),
        selectinload(Product.variants),
        joinedload(Product.category).selectinload(Category.translations),
    ]
    if include_reviews:
        options.append(selectinload(Product.reviews))
    return options


def public_json(payload, max_age=15, shared_max_age=30):
    response = jsonify(payload)
    response.headers["Cache-Control"] = (
        f"public, max-age={max_age}, s-maxage={shared_max_age}, "
        "stale-while-revalidate=120"
    )
    return response


def create_notification(notification_type, title, content=None, link=None, user_id=None):
    notification = Notification(
        type=notification_type,
        title=title,
        content=content,
        link=link,
        user_id=user_id,
    )
    db.session.add(notification)
    return notification


def normalize_email(value):
    return (value or "").strip().lower()


def request_user(required=False):
    payload = request.get_json(silent=True) or {}
    args = request.args
    form = request.form or {}
    user_id = (
        payload.get("userId")
        or payload.get("user_id")
        or args.get("userId")
        or args.get("user_id")
        or form.get("userId")
        or form.get("user_id")
    )
    email = (
        payload.get("userEmail")
        or payload.get("email")
        or args.get("userEmail")
        or args.get("email")
        or form.get("userEmail")
        or form.get("email")
    )
    user = None
    if user_id:
        user = User.query.get(user_id)
    if not user and email:
        user = User.query.filter_by(email=normalize_email(email)).first()
    if required and not user:
        return None
    return user


def require_user():
    user = request_user(required=True)
    if not user:
        return None, (jsonify({"error": "Authentication required"}), 401)
    if not user.is_active:
        return None, (jsonify({"error": "Account is disabled"}), 403)
    return user, None


def is_admin_user(user):
    return bool(user and user.role in ADMIN_ROLES)


def is_super_admin_user(user):
    return bool(user and user.role == SUPER_ADMIN_ROLE)


def is_elevated_admin_user(user):
    return bool(user and user.role in ELEVATED_ADMIN_ROLES)


def require_admin():
    user, error_response = require_user()
    if error_response:
        return None, error_response
    if not is_admin_user(user):
        return None, (jsonify({"error": "Admin access required"}), 403)
    return user, None


def require_super_admin():
    user, error_response = require_admin()
    if error_response:
        return None, error_response
    if not is_super_admin_user(user):
        return None, (jsonify({"error": "Super admin access required"}), 403)
    return user, None


def require_elevated_admin():
    user, error_response = require_admin()
    if error_response:
        return None, error_response
    if not is_elevated_admin_user(user):
        return None, (jsonify({"error": "Elevated admin access required"}), 403)
    return user, None


def require_vendor():
    user, error_response = require_user()
    if error_response:
        return None, error_response
    if user.role != "VENDOR":
        return None, (jsonify({"error": "Vendor access required"}), 403)
    return user, None


def can_access_inquiry(user, inquiry):
    return bool(user and inquiry and (is_admin_user(user) or inquiry.user_id == user.id))


def parse_date(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    text_value = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text_value).replace(tzinfo=None)
    except ValueError:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d")


def allowed_vendor_file(filename):
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in ALLOWED_VENDOR_FILE_EXTENSIONS


def allowed_product_image_file(filename):
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in ALLOWED_PRODUCT_IMAGE_EXTENSIONS


def uploaded_file_size(file):
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    return size


def clean_upload_segment(value, fallback, max_length=120):
    segment = str(value or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
    segment = re.sub(r"[\x00-\x1f\x7f]+", "", segment)
    segment = re.sub(r'[<>:"/\\|?*#%&]+', "_", segment)
    segment = segment.strip(" .")
    return (segment or fallback)[:max_length]


def media_upload_filename(filename):
    name = clean_upload_segment(filename, "product-image", max_length=180)
    if "." not in name:
        return name
    stem, suffix = name.rsplit(".", 1)
    return f"{stem}.{suffix.lower()}"


def media_rename_filename(value, current_name):
    raw_name = str(value or "").strip()
    if not raw_name:
        return current_name, None

    current_suffix = Path(current_name or "").suffix.lower()
    cleaned = media_upload_filename(raw_name)
    requested_suffix = Path(cleaned).suffix.lower()
    if requested_suffix:
        if requested_suffix.lstrip(".") not in ALLOWED_PRODUCT_IMAGE_EXTENSIONS:
            return None, "Unsupported image type"
        cleaned = cleaned[:-len(requested_suffix)]

    stem = clean_upload_segment(cleaned, Path(current_name or "media").stem or "media", max_length=160)
    if not current_suffix:
        return stem, None
    return f"{stem}{current_suffix}", None


def media_category_now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def media_category_lookup_value(value):
    lookup = str(value or "").strip()
    if lookup.lower() in MEDIA_CATEGORY_RESERVED_VALUES:
        return ""
    return lookup


def media_category_slug(value, fallback=None):
    slug = str(value or "").strip().lower()
    slug = re.sub(r"\s+", "-", slug)
    slug = clean_upload_segment(slug, "", max_length=64).lower()
    slug = re.sub(r"[^\w._-]+", "-", slug, flags=re.UNICODE)
    slug = re.sub(r"-+", "-", slug).strip("-_.")
    return slug or fallback or f"category-{uuid4().hex[:8]}"


def unique_media_category_slug(categories, preferred):
    base_slug = media_category_slug(preferred)
    used_slugs = {str(row.get("slug") or "").lower() for row in categories}
    if base_slug.lower() not in used_slugs:
        return base_slug
    index = 2
    while True:
        candidate = f"{base_slug}-{index}"
        if candidate.lower() not in used_slugs:
            return candidate
        index += 1


def media_category_record(slug, name_en, name_zh, parent_id=None, sort_order=100, category_id=None, is_default=False):
    now = media_category_now()
    return {
        "id": category_id or f"cat-{uuid4().hex}",
        "slug": media_category_slug(slug),
        "nameEn": str(name_en or slug).strip(),
        "nameZh": str(name_zh or name_en or slug).strip(),
        "parentId": parent_id or None,
        "sortOrder": sort_order,
        "isDefault": bool(is_default),
        "createdAt": now,
        "updatedAt": now,
    }


def sanitize_media_categories(rows):
    categories = []
    used_ids = set()
    used_slugs = set()
    for index, row in enumerate(rows or []):
        if not isinstance(row, dict):
            continue
        if row.get("isDefault") or str(row.get("id") or "").startswith("default-"):
            continue
        raw_slug = row.get("slug") or row.get("category") or row.get("nameEn") or row.get("name") or f"category-{index + 1}"
        slug = media_category_slug(raw_slug, fallback=f"category-{index + 1}")
        if slug.lower() in used_slugs:
            slug = unique_media_category_slug(categories, slug)
        raw_id = str(row.get("id") or "").strip()
        category_id = raw_id if raw_id and raw_id not in used_ids else f"cat-{uuid4().hex}"
        used_ids.add(category_id)
        used_slugs.add(slug.lower())
        name_en = str(row.get("nameEn") or row.get("name_en") or row.get("name") or slug).strip()
        name_zh = str(row.get("nameZh") or row.get("name_zh") or row.get("name") or name_en).strip()
        try:
            sort_order = int(row.get("sortOrder", index * 10))
        except (TypeError, ValueError):
            sort_order = index * 10
        categories.append({
            "id": category_id,
            "slug": slug,
            "nameEn": name_en,
            "nameZh": name_zh,
            "parentId": row.get("parentId") or row.get("parent_id") or None,
            "sortOrder": sort_order,
            "isDefault": bool(row.get("isDefault")),
            "createdAt": row.get("createdAt") or row.get("created_at") or media_category_now(),
            "updatedAt": row.get("updatedAt") or row.get("updated_at") or media_category_now(),
        })

    valid_ids = {row["id"] for row in categories}
    for row in categories:
        parent_id = str(row.get("parentId") or "").strip()
        row["parentId"] = parent_id if parent_id in valid_ids and parent_id != row["id"] else None
    return sorted(categories, key=lambda row: (row.get("sortOrder", 0), row.get("nameEn", "").lower(), row.get("slug", "")))


def media_category_file(base_dir):
    return base_dir / MEDIA_CATEGORY_FILE


def save_media_categories(base_dir, categories):
    base_dir.mkdir(parents=True, exist_ok=True)
    file_path = media_category_file(base_dir)
    temp_path = base_dir / f"{MEDIA_CATEGORY_FILE}.tmp"
    temp_path.write_text(json.dumps(sanitize_media_categories(categories), ensure_ascii=False, indent=2), encoding="utf-8")
    temp_path.replace(file_path)


def load_media_categories(base_dir, preset_keys=None):
    preset_keys = list(preset_keys or [])
    file_path = media_category_file(base_dir)
    metadata_exists = file_path.exists()
    rows = []
    needs_save = False
    if metadata_exists:
        try:
            content = json.loads(file_path.read_text(encoding="utf-8"))
            rows = content if isinstance(content, list) else []
        except (OSError, json.JSONDecodeError):
            rows = []
            needs_save = True
    else:
        for index, slug in enumerate(preset_keys):
            config = MEDIA_CATEGORY_DEFAULTS.get(slug)
            if not config:
                continue
            rows.append(media_category_record(
                slug,
                config["nameEn"],
                config["nameZh"],
                sort_order=config.get("sortOrder", index * 10),
                category_id=f"default-{slug}",
                is_default=True,
            ))
        needs_save = bool(rows)

    raw_count = len(rows or [])
    categories = sanitize_media_categories(rows)
    if raw_count != len(categories):
        needs_save = True
    known_slugs = {row["slug"].lower() for row in categories}
    if base_dir.exists() and not metadata_exists:
        legacy_dirs = [path for path in base_dir.iterdir() if path.is_dir()]
        for path in sorted(legacy_dirs, key=lambda item: item.name.lower()):
            slug = media_category_slug(path.name)
            if not slug or slug.lower() in known_slugs or slug in MEDIA_CATEGORY_DEFAULTS:
                continue
            config = MEDIA_CATEGORY_DEFAULTS.get(slug, {})
            categories.append(media_category_record(
                slug,
                config.get("nameEn") or path.name,
                config.get("nameZh") or config.get("nameEn") or path.name,
                sort_order=1000 + len(categories),
                is_default=False,
            ))
            known_slugs.add(slug.lower())
            needs_save = True

    categories = sanitize_media_categories(categories)
    if needs_save:
        save_media_categories(base_dir, categories)
    return categories


def media_category_by_lookup(categories, value):
    lookup = media_category_lookup_value(value)
    if not lookup:
        return None
    lookup_lower = lookup.lower()
    slug_lookup = media_category_slug(lookup)
    for row in categories:
        if row.get("id") == lookup:
            return row
        if str(row.get("slug") or "").lower() == lookup_lower or str(row.get("slug") or "").lower() == slug_lookup:
            return row
        if str(row.get("nameEn") or "").lower() == lookup_lower or str(row.get("nameZh") or "").lower() == lookup_lower:
            return row
    return None


def media_category_create_payload():
    payload = request.get_json(silent=True) or {}
    name_en = str(payload.get("nameEn") or payload.get("name_en") or "").strip()
    name_zh = str(payload.get("nameZh") or payload.get("name_zh") or "").strip()
    if not name_en or not name_zh:
        return None, (jsonify({"error": "Chinese and English category names are required"}), 400)
    return {
        "nameEn": name_en[:120],
        "nameZh": name_zh[:120],
        "slug": payload.get("slug") or payload.get("category") or name_en,
        "parent": payload.get("parentId") or payload.get("parent_id") or payload.get("parent") or "",
    }, None


def media_category_delete_payload():
    payload = request.get_json(silent=True) or {}
    lookup = (
        payload.get("id")
        or payload.get("categoryId")
        or payload.get("category_id")
        or payload.get("category")
        or payload.get("slug")
        or payload.get("name")
    )
    lookup = media_category_lookup_value(lookup)
    if not lookup:
        return None, (jsonify({"error": "Category is required"}), 400)
    if lookup.startswith("default-"):
        lookup = lookup.removeprefix("default-")
    return lookup, None


def media_upload_category(base_dir=None, preset_keys=None):
    lookup = media_category_lookup_value(request.form.get("category"))
    if not lookup:
        return ""
    if base_dir is not None:
        category = media_category_by_lookup(load_media_categories(base_dir, preset_keys=preset_keys), lookup)
        if category:
            return category["slug"]
        return ""
    return media_category_slug(lookup)


def unique_media_path(upload_dir, filename):
    target = upload_dir / filename
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    index = 1
    while True:
        candidate = upload_dir / f"{stem} ({index}){suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def uploaded_media_item(path, base_dir=None, category_map=None):
    relative_path = path.relative_to(UPLOAD_ROOT).as_posix()
    category = ""
    category_id = None
    if base_dir:
        try:
            relative_to_base = path.relative_to(base_dir)
            if len(relative_to_base.parts) > 1:
                raw_category = relative_to_base.parts[0]
                if category_map is None or raw_category in category_map:
                    category = raw_category
                    category_id = (category_map or {}).get(category, {}).get("id")
        except ValueError:
            category = ""
            category_id = None
    storage_key = relative_path
    return {
        "id": f"upload-{relative_path}",
        "url": media_public_url(storage_key),
        "thumbnailUrl": media_variant_url(media_public_url(storage_key), width=480, quality=78),
        "localUrl": f"/api/uploads/{relative_path}",
        "storageKey": storage_key,
        "storageProvider": media_storage_provider(),
        "deletable": True,
        "name": path.name,
        "category": category,
        "categoryId": category_id,
        "productId": None,
    }


def uploaded_media_items(*relative_parts, limit=300, categories=None):
    base_dir = UPLOAD_ROOT.joinpath(*relative_parts)
    if not base_dir.exists():
        return []
    category_map = {row.get("slug"): row for row in categories or []}
    files = [
        path
        for path in base_dir.rglob("*")
        if path.is_file()
        and path.name != MEDIA_CATEGORY_FILE
        and path.suffix.lower().lstrip(".") in ALLOWED_PRODUCT_IMAGE_EXTENSIONS
    ]
    files.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return [uploaded_media_item(path, base_dir=base_dir, category_map=category_map) for path in files[:limit]]


def uploaded_media_categories(*relative_parts, preset_keys=None):
    base_dir = UPLOAD_ROOT.joinpath(*relative_parts)
    return load_media_categories(base_dir, preset_keys=preset_keys)


def media_category_descendant_ids(categories, category_id):
    ids = {category_id}
    changed = True
    while changed:
        changed = False
        for row in categories:
            if row.get("parentId") in ids and row.get("id") not in ids:
                ids.add(row["id"])
                changed = True
    return ids


def media_category_response(*relative_parts, limit=300, preset_keys=None):
    categories = uploaded_media_categories(*relative_parts, preset_keys=preset_keys)
    media = uploaded_media_items(*relative_parts, limit=limit, categories=categories)
    return {"media": media, "categories": categories}


def admin_media_parts():
    return ADMIN_SHARED_MEDIA_PARTS


def user_media_parts(user, namespace):
    return ("media", namespace, user.id)


def media_url_for_path(path):
    return f"/api/uploads/{path.relative_to(UPLOAD_ROOT).as_posix()}"


def merge_media_category_rows(base_categories, incoming_categories):
    categories = sanitize_media_categories(base_categories)
    used_slugs = {str(row.get("slug") or "").lower() for row in categories}
    used_ids = {str(row.get("id") or "") for row in categories}
    category_map = {}

    for row in sanitize_media_categories(incoming_categories):
        slug = row.get("slug") or ""
        if not slug:
            continue
        existing = next((item for item in categories if str(item.get("slug") or "").lower() == slug.lower()), None)
        if existing:
            category_map[row["id"]] = existing["id"]
            category_map[slug] = existing["slug"]
            continue

        copied = dict(row)
        if copied["id"] in used_ids:
            copied["id"] = f"cat-{uuid4().hex}"
        parent_id = copied.get("parentId")
        copied["parentId"] = category_map.get(parent_id) if parent_id else None
        copied["sortOrder"] = max([item.get("sortOrder", 0) for item in categories] or [0]) + 10
        copied["createdAt"] = copied.get("createdAt") or media_category_now()
        copied["updatedAt"] = media_category_now()
        categories.append(copied)
        used_slugs.add(slug.lower())
        used_ids.add(copied["id"])
        category_map[row["id"]] = copied["id"]
        category_map[slug] = copied["slug"]

    return sanitize_media_categories(categories), category_map


def migrate_admin_media_to_shared():
    shared_dir = UPLOAD_ROOT.joinpath(*admin_media_parts())
    marker_path = shared_dir / ADMIN_SHARED_MIGRATION_MARKER
    legacy_root = UPLOAD_ROOT.joinpath(*ADMIN_LEGACY_MEDIA_ROOT_PARTS)
    if marker_path.exists():
        return

    legacy_dirs = []
    legacy_single_dir = UPLOAD_ROOT / "media" / "admin"
    if legacy_single_dir.exists() and legacy_single_dir.is_dir():
        legacy_dirs.append(legacy_single_dir)
    if legacy_root.exists() and legacy_root.is_dir():
        legacy_dirs.extend(path for path in sorted(legacy_root.iterdir(), key=lambda item: item.name.lower()) if path.is_dir())

    if not legacy_dirs:
        shared_dir.mkdir(parents=True, exist_ok=True)
        marker_path.write_text(media_category_now(), encoding="utf-8")
        return

    shared_dir.mkdir(parents=True, exist_ok=True)
    shared_categories = load_media_categories(shared_dir, preset_keys=ADMIN_MEDIA_CATEGORY_PRESETS)
    copied_urls = {}

    for legacy_dir in legacy_dirs:
        try:
            if legacy_dir.resolve() == shared_dir.resolve():
                continue
        except OSError:
            continue

        legacy_categories = load_media_categories(legacy_dir, preset_keys=ADMIN_MEDIA_CATEGORY_PRESETS)
        shared_categories, category_map = merge_media_category_rows(shared_categories, legacy_categories)
        category_slug_map = {
            row.get("slug"): category_map.get(row.get("slug"), row.get("slug"))
            for row in legacy_categories
            if row.get("slug")
        }

        for path in legacy_dir.rglob("*"):
            if (
                not path.is_file()
                or path.name in {MEDIA_CATEGORY_FILE, ADMIN_SHARED_MIGRATION_MARKER}
                or path.suffix.lower().lstrip(".") not in ALLOWED_PRODUCT_IMAGE_EXTENSIONS
            ):
                continue
            try:
                relative_to_legacy = path.relative_to(legacy_dir)
            except ValueError:
                continue

            target_dir = shared_dir
            if len(relative_to_legacy.parts) > 1:
                legacy_category = relative_to_legacy.parts[0]
                mapped_category = category_slug_map.get(legacy_category)
                if mapped_category:
                    target_dir = shared_dir / mapped_category
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / path.name
            if not target_path.exists():
                shutil.copy2(path, target_path)
            elif target_path.resolve() != path.resolve():
                target_path = unique_media_path(target_dir, path.name)
                shutil.copy2(path, target_path)

            old_url = media_url_for_path(path)
            new_url = media_url_for_path(target_path)
            if old_url != new_url:
                copied_urls[old_url] = new_url

    save_media_categories(shared_dir, shared_categories)
    for old_url, new_url in copied_urls.items():
        for row in ProductImage.query.filter(ProductImage.url == old_url).all():
            row.url = new_url
    if copied_urls:
        db.session.commit()
    marker_path.write_text(media_category_now(), encoding="utf-8")


def merge_media_items(*groups):
    seen = set()
    media = []
    for group in groups:
        for item in group:
            url = item.get("url")
            if not url or url in seen:
                continue
            seen.add(url)
            media.append(item)
    return media


def uploaded_media_path_from_url(reference, *allowed_base_parts):
    key = normalize_media_key(reference)
    if not key or not key.startswith("media/"):
        return None
    path = (UPLOAD_ROOT / key).resolve()
    allowed_base = UPLOAD_ROOT.joinpath(*allowed_base_parts).resolve()
    try:
        path.relative_to(allowed_base)
    except ValueError:
        return None
    return path


def save_product_media_upload(*relative_parts, preset_keys=None):
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "File is required"}), 400
    if not allowed_product_image_file(file.filename):
        return jsonify({"error": "Unsupported image type"}), 400
    if uploaded_file_size(file) > MAX_MEDIA_UPLOAD_BYTES:
        return jsonify({"error": "File must be smaller than 10MB"}), 400

    base_dir = UPLOAD_ROOT.joinpath(*relative_parts)
    category = media_upload_category(base_dir, preset_keys=preset_keys)
    upload_parts = (*relative_parts, category) if category else relative_parts
    upload_dir = UPLOAD_ROOT.joinpath(*upload_parts)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_path = unique_media_path(upload_dir, media_upload_filename(file.filename))
    payload = prepare_media_upload(file, stored_path.name)
    stored_path.write_bytes(payload.data)
    storage_key = stored_path.relative_to(UPLOAD_ROOT).as_posix()
    try:
        upload_remote_media(storage_key, payload.data, payload.content_type)
    except Exception as exc:
        try:
            if stored_path.exists():
                stored_path.unlink()
        except OSError:
            pass
        return jsonify({"error": f"Failed to upload image to OSS: {exc}"}), 502
    categories = load_media_categories(base_dir, preset_keys=preset_keys)
    item = uploaded_media_item(stored_path, base_dir=base_dir, category_map={row.get("slug"): row for row in categories})
    item["optimized"] = payload.optimized
    item["originalSize"] = payload.original_size
    item["storedSize"] = payload.stored_size
    return jsonify({"success": True, **item})


def delete_product_media_upload(reference, *allowed_base_parts, vendor_id=None):
    path = uploaded_media_path_from_url(reference, *allowed_base_parts)
    key = normalize_media_key(reference)
    candidate_urls = media_url_candidates(key) if key else {str(reference or "").strip()}
    if not path:
        return jsonify({"error": "Only uploaded media files can be deleted"}), 400

    query = ProductImage.query.filter(ProductImage.url.in_(candidate_urls))
    if vendor_id:
        query = query.join(Product).filter(Product.vendor_id == vendor_id)
    reference_ids = [row.id for row in query.all()]
    deleted_refs = 0
    if reference_ids:
        deleted_refs = ProductImage.query.filter(ProductImage.id.in_(reference_ids)).delete(
            synchronize_session=False
        )
    deleted_file = False
    if path.exists() and path.is_file():
        path.unlink()
        deleted_file = True
        allowed_base = UPLOAD_ROOT.joinpath(*allowed_base_parts).resolve()
        for parent in path.parents:
            if parent == allowed_base:
                break
            try:
                parent.rmdir()
            except OSError:
                break
    deleted_remote = False
    try:
        deleted_remote = delete_remote_media(key)
    except Exception:
        deleted_remote = False
    db.session.commit()
    return jsonify({"success": True, "deletedFile": deleted_file, "deletedRemote": deleted_remote, "deletedReferences": deleted_refs})


def read_media_upload_bytes(path, key):
    if path.exists() and path.is_file():
        return path.read_bytes()
    if aliyun_oss_enabled() and key:
        return aliyun_oss_bucket().get_object(normalize_media_key(key)).read()
    return None


def cleanup_empty_media_dirs(start_dir, allowed_base):
    for parent in start_dir.parents:
        if parent == allowed_base:
            break
        try:
            parent.rmdir()
        except OSError:
            break


def update_media_references(old_urls, new_url, vendor_id=None, include_shared_refs=False):
    old_urls = {item for item in old_urls if item}
    if not old_urls or not new_url:
        return 0

    updated = 0
    query = ProductImage.query.filter(ProductImage.url.in_(old_urls))
    if vendor_id:
        query = query.join(Product).filter(Product.vendor_id == vendor_id)
    for row in query.all():
        row.url = new_url
        updated += 1

    if include_shared_refs:
        for model, attr_name in ((Category, "image"), (Banner, "image"), (InquiryItem, "image")):
            attr = getattr(model, attr_name)
            for row in model.query.filter(attr.in_(old_urls)).all():
                setattr(row, attr_name, new_url)
                updated += 1

    return updated


def move_product_media_upload(reference, target_category, *allowed_base_parts, vendor_id=None, preset_keys=None, include_shared_refs=False, target_name=None):
    path = uploaded_media_path_from_url(reference, *allowed_base_parts)
    old_key = normalize_media_key(reference)
    if not path or not old_key:
        return jsonify({"error": "Only uploaded media files can be updated"}), 400
    if path.suffix.lower().lstrip(".") not in ALLOWED_PRODUCT_IMAGE_EXTENSIONS:
        return jsonify({"error": "Unsupported image type"}), 400
    target_filename, filename_error = media_rename_filename(target_name, path.name)
    if filename_error:
        return jsonify({"error": filename_error}), 400
    if Path(target_filename).suffix.lower().lstrip(".") not in ALLOWED_PRODUCT_IMAGE_EXTENSIONS:
        return jsonify({"error": "Unsupported image type"}), 400

    base_dir = UPLOAD_ROOT.joinpath(*allowed_base_parts).resolve()
    categories = load_media_categories(base_dir, preset_keys=preset_keys)
    category_map = {row.get("slug"): row for row in categories}
    lookup = media_category_lookup_value(target_category)
    target = media_category_by_lookup(categories, lookup) if lookup else None
    if lookup and not target:
        return jsonify({"error": "Category not found"}), 404
    target_slug = target["slug"] if target else ""

    try:
        relative_to_base = path.relative_to(base_dir)
    except ValueError:
        return jsonify({"error": "Invalid media path"}), 400
    current_slug = relative_to_base.parts[0] if len(relative_to_base.parts) > 1 else ""

    if current_slug == target_slug and path.name == target_filename:
        item = uploaded_media_item(path, base_dir=base_dir, category_map=category_map)
        data = media_category_response(*allowed_base_parts, preset_keys=preset_keys)
        return jsonify({
            "success": True,
            "moved": False,
            "renamed": False,
            "oldUrl": media_public_url(old_key),
            "newUrl": media_public_url(old_key),
            "item": item,
            **data,
        })

    target_dir = (base_dir / target_slug).resolve() if target_slug else base_dir
    try:
        target_dir.relative_to(base_dir)
    except ValueError:
        return jsonify({"error": "Invalid target category"}), 400
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / target_filename
    if target_path.exists() and target_path.resolve() != path.resolve():
        target_path = unique_media_path(target_dir, target_filename)

    new_key = target_path.relative_to(UPLOAD_ROOT).as_posix()
    old_urls = media_url_candidates(old_key)
    uploaded_remote = False
    try:
        media_bytes = read_media_upload_bytes(path, old_key)
        if media_bytes is None:
            return jsonify({"error": "Media file not found"}), 404
        if aliyun_oss_enabled():
            upload_remote_media(new_key, media_bytes, content_type_for_key(new_key))
            uploaded_remote = True
        if path.exists() and path.is_file():
            path.replace(target_path)
        else:
            target_path.write_bytes(media_bytes)
        if aliyun_oss_enabled():
            try:
                delete_remote_media(old_key)
            except Exception:
                pass
    except Exception as exc:
        if uploaded_remote:
            try:
                delete_remote_media(new_key)
            except Exception:
                pass
        return jsonify({"error": f"Failed to move image: {exc}"}), 502

    new_url = media_public_url(new_key)
    updated_refs = update_media_references(
        old_urls,
        new_url,
        vendor_id=vendor_id,
        include_shared_refs=include_shared_refs,
    )
    db.session.commit()
    cleanup_empty_media_dirs(path, base_dir)

    categories = load_media_categories(base_dir, preset_keys=preset_keys)
    item = uploaded_media_item(target_path, base_dir=base_dir, category_map={row.get("slug"): row for row in categories})
    data = media_category_response(*allowed_base_parts, preset_keys=preset_keys)
    return jsonify({
        "success": True,
        "moved": True,
        "renamed": path.name != target_path.name,
        "oldUrl": media_public_url(old_key),
        "oldUrls": list(old_urls),
        "newUrl": new_url,
        "updatedReferences": updated_refs,
        "item": item,
        **data,
    })


def create_product_media_category(*relative_parts, preset_keys=None):
    payload, error_response = media_category_create_payload()
    if error_response:
        return error_response
    base_dir = UPLOAD_ROOT.joinpath(*relative_parts)
    categories = load_media_categories(base_dir, preset_keys=preset_keys)
    parent = media_category_by_lookup(categories, payload["parent"]) if payload.get("parent") else None
    parent_id = parent["id"] if parent else None
    slug = unique_media_category_slug(categories, payload.get("slug") or payload["nameEn"])
    category = media_category_record(
        slug,
        payload["nameEn"],
        payload["nameZh"],
        parent_id=parent_id,
        sort_order=max([row.get("sortOrder", 0) for row in categories] or [0]) + 10,
    )
    categories.append(category)
    save_media_categories(base_dir, categories)
    (base_dir / category["slug"]).mkdir(parents=True, exist_ok=True)
    data = media_category_response(*relative_parts, preset_keys=preset_keys)
    return jsonify({"success": True, "category": category, **data})


def delete_product_media_category(*relative_parts, vendor_id=None, preset_keys=None):
    lookup, error_response = media_category_delete_payload()
    if error_response:
        return error_response
    base_dir = UPLOAD_ROOT.joinpath(*relative_parts).resolve()
    categories = load_media_categories(base_dir, preset_keys=preset_keys)
    target = media_category_by_lookup(categories, lookup)
    if not target:
        legacy_slug = media_category_slug(lookup)
        legacy_dir = (base_dir / legacy_slug).resolve()
        try:
            legacy_dir.relative_to(base_dir)
        except ValueError:
            return jsonify({"error": "Invalid category"}), 400
        if not legacy_slug or legacy_dir == base_dir or not legacy_dir.exists() or not legacy_dir.is_dir():
            if legacy_slug in MEDIA_CATEGORY_DEFAULTS:
                save_media_categories(base_dir, categories)
                data = media_category_response(*relative_parts, preset_keys=preset_keys)
                return jsonify({
                    "success": True,
                    "category": {"slug": legacy_slug},
                    "deletedCategoryIds": [],
                    "moved": 0,
                    **data,
                })
            return jsonify({"error": "Category not found"}), 404
        target = media_category_record(legacy_slug, legacy_slug, legacy_slug)
        delete_ids = {target["id"]}
        delete_slugs = {legacy_slug}
    else:
        delete_ids = media_category_descendant_ids(categories, target["id"])
        delete_categories = [row for row in categories if row.get("id") in delete_ids]
        delete_slugs = {row.get("slug") for row in delete_categories if row.get("slug")}

    moved = 0
    moved_urls = {}
    for slug in sorted(delete_slugs):
        category_dir = (base_dir / slug).resolve()
        try:
            category_dir.relative_to(base_dir)
        except ValueError:
            continue
        if category_dir == base_dir or not category_dir.exists() or not category_dir.is_dir():
            continue
        for path in list(category_dir.iterdir()):
            if not path.is_file() or path.name == MEDIA_CATEGORY_FILE:
                continue
            if path.suffix.lower().lstrip(".") not in ALLOWED_PRODUCT_IMAGE_EXTENSIONS:
                continue
            target_path = unique_media_path(base_dir, path.name)
            old_key = path.relative_to(UPLOAD_ROOT).as_posix()
            new_key = target_path.relative_to(UPLOAD_ROOT).as_posix()
            if aliyun_oss_enabled():
                try:
                    upload_remote_media(new_key, path.read_bytes())
                except Exception as exc:
                    return jsonify({"error": f"Failed to move image in OSS: {exc}"}), 502
            path.replace(target_path)
            if aliyun_oss_enabled():
                try:
                    delete_remote_media(old_key)
                except Exception:
                    pass
            for old_url in media_url_candidates(old_key):
                moved_urls[old_url] = media_public_url(new_key)
            moved += 1
        try:
            category_dir.rmdir()
        except OSError:
            pass

    for old_url, new_url in moved_urls.items():
        query = ProductImage.query.filter(ProductImage.url == old_url)
        if vendor_id:
            query = query.join(Product).filter(Product.vendor_id == vendor_id)
        for row in query.all():
            row.url = new_url

    remaining_categories = [row for row in categories if row.get("id") not in delete_ids and row.get("slug") not in delete_slugs]
    save_media_categories(base_dir, remaining_categories)
    db.session.commit()
    data = media_category_response(*relative_parts, preset_keys=preset_keys)
    return jsonify({
        "success": True,
        "category": target,
        "deletedCategoryIds": list(delete_ids),
        "moved": moved,
        **data,
    })


def notification_payload(row, user):
    item = row.to_dict()
    link = item.get("link") or ""
    if user.role == "ADMIN":
        match = re.search(r"/(?:account/)?inquiries/([^/?#]+)", link)
        inquiry_id = match.group(1) if match else None
        if inquiry_id and inquiry_id.lower() not in {"none", "null", "undefined"}:
            item["link"] = f"/admin/orders/{inquiry_id}"
        elif link == "/inquiry" or re.search(r"/admin/orders/(none|null|undefined)(?=$|[/?#])", link, re.I):
            item["link"] = "/admin/orders"
        elif link.startswith("/vendor"):
            item["link"] = "/admin/vendors"
        elif link == "/contact":
            item["link"] = "/admin/contacts"
    return item


def fallback_notifications(limit=30):
    notifications = []
    inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(limit).all()
    for inquiry in inquiries:
        notifications.append(
            {
                "id": f"fallback-inquiry-{inquiry.id}",
                "type": "INQUIRY_SUBMITTED",
                "title": "New inquiry submitted",
                "content": f"{inquiry.contact_name} submitted {inquiry.inquiry_number}",
                "link": f"/admin/orders/{inquiry.id}",
                "isRead": True,
                "createdAt": inquiry.created_at.isoformat() if inquiry.created_at else None,
            }
        )

    contacts = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(limit).all()
    for message in contacts:
        notifications.append(
            {
                "id": f"fallback-contact-{message.id}",
                "type": "CONTACT_MESSAGE",
                "title": "New contact message",
                "content": f"{message.name}: {message.subject}",
                "link": "/contact",
                "isRead": True,
                "createdAt": message.created_at.isoformat() if message.created_at else None,
            }
        )

    notifications.sort(key=lambda item: item.get("createdAt") or "", reverse=True)
    return notifications[:limit]


@api.get("/health")
def health():
    db.session.execute(text("SELECT 1"))
    return jsonify(
        {
            "status": "ok",
            "services": {"database": "ok"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@api.get("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_ROOT, filename)


@api.get("/home")
def home():
    locale = get_locale()
    categories = (
        Category.query.filter_by(is_active=True, parent_id=None)
        .options(selectinload(Category.translations))
        .order_by(Category.sort_order.asc())
        .all()
    )
    banners = (
        Banner.query.filter_by(position="hero", is_active=True)
        .options(selectinload(Banner.translations))
        .order_by(Banner.sort_order.asc())
        .all()
    )
    new_products = (
        Product.query.filter_by(status="ACTIVE", is_new=True)
        .options(*public_product_load_options())
        .order_by(Product.created_at.desc(), Product.id.desc())
        .limit(18)
        .all()
    )

    category_products = []
    for category in categories:
        products = (
            Product.query.filter_by(status="ACTIVE", category_id=category.id)
            .options(*public_product_load_options())
            .order_by(Product.sort_order.asc(), Product.created_at.asc(), Product.id.asc())
            .limit(6)
            .all()
        )
        category_products.append(
            {
                "category": category.to_dict(locale=locale, include_children=False),
                "products": [product.to_card_dict(locale=locale) for product in products],
            }
        )

    return public_json(
        {
            "banners": [banner.to_dict(locale=locale) for banner in banners],
            "categoryProducts": category_products,
            "newProducts": [product.to_card_dict(locale=locale) for product in new_products],
        }
    )


@api.get("/categories")
def categories():
    locale = get_locale()
    rows = (
        Category.query.filter_by(is_active=True, parent_id=None)
        .options(selectinload(Category.translations))
        .order_by(Category.sort_order.asc())
        .all()
    )
    return public_json([row.to_dict(locale=locale) for row in rows])


@api.get("/products")
def products():
    locale = get_locale()
    page = max(int(request.args.get("page", 1)), 1)
    limit = min(max(int(request.args.get("limit", 12)), 1), 500)
    category_slug = request.args.get("category")
    sort = request.args.get("sort", "recommended")
    query_text = request.args.get("q")
    min_price = request.args.get("minPrice")
    max_price = request.args.get("maxPrice")
    featured = request.args.get("featured")
    is_new = request.args.get("new")

    query = Product.query.filter(Product.status == "ACTIVE")

    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first()
        if not category:
            return public_json(
                {
                    "products": [],
                    "pagination": {"page": page, "limit": limit, "total": 0, "totalPages": 0},
                }
            )
        query = query.filter(Product.category_id == category.id)

    if min_price:
        query = query.filter(Product.price >= float(min_price))
    if max_price:
        query = query.filter(Product.price <= float(max_price))
    if featured in ("true", "1"):
        query = query.filter(Product.is_featured.is_(True))
    if is_new in ("true", "1"):
        query = query.filter(Product.is_new.is_(True))
    if query_text:
        like = f"%{query_text}%"
        query = query.outerjoin(ProductTranslation).filter(
            or_(
                Product.slug.ilike(like),
                Product.sku.ilike(like),
                Product.brand_name.ilike(like),
                ProductTranslation.name.ilike(like),
                ProductTranslation.description.ilike(like),
            )
        )

    if sort == "price-asc":
        query = query.order_by(Product.price.asc(), Product.sort_order.asc(), Product.created_at.asc(), Product.id.asc())
    elif sort == "price-desc":
        query = query.order_by(Product.price.desc(), Product.sort_order.asc(), Product.created_at.asc(), Product.id.asc())
    elif sort == "newest":
        query = query.order_by(Product.created_at.desc(), Product.id.desc())
    elif sort in ("recommended", "popular"):
        query = query.order_by(Product.sort_order.asc(), Product.created_at.asc(), Product.id.asc())
    else:
        query = query.order_by(Product.created_at.desc(), Product.id.desc())

    total = query.count()
    rows = (
        query.options(*public_product_load_options())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return public_json(
        {
            "products": [row.to_card_dict(locale=locale) for row in rows],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": ceil(total / limit) if total else 0,
            },
        }
    )


@api.get("/products/<slug>")
def product_detail(slug):
    locale = get_locale()
    product = (
        Product.query.filter_by(slug=slug, status="ACTIVE")
        .options(*public_product_load_options(include_reviews=True))
        .first()
    )
    if not product:
        return jsonify({"error": "Product not found"}), 404

    related = []
    if product.category_id:
        related = (
            Product.query.filter(
                Product.status == "ACTIVE",
                Product.category_id == product.category_id,
                Product.id != product.id,
            )
            .options(*public_product_load_options())
            .order_by(Product.sort_order.asc())
            .limit(4)
            .all()
        )
    return public_json(
        {
            "product": product.to_dict(locale=locale),
            "relatedProducts": [row.to_card_dict(locale=locale) for row in related],
        }
    )


@api.get("/search")
def search():
    locale = get_locale()
    q = request.args.get("q", "").strip()
    limit = min(max(int(request.args.get("limit", 20)), 1), 50)
    if len(q) < 2:
        return public_json({"products": [], "total": 0}, max_age=5, shared_max_age=10)
    like = f"%{q}%"
    rows = (
        Product.query.filter(Product.status == "ACTIVE")
        .outerjoin(ProductTranslation)
        .options(*public_product_load_options())
        .filter(
            or_(
                Product.slug.ilike(like),
                Product.sku.ilike(like),
                Product.brand_name.ilike(like),
                ProductTranslation.name.ilike(like),
                ProductTranslation.description.ilike(like),
            )
        )
        .limit(limit)
        .all()
    )
    products = []
    for row in rows:
        item = row.to_card_dict(locale=locale)
        products.append(
            {
                "id": item["id"],
                "slug": item["slug"],
                "name": item["name"],
                "image": item.get("image"),
                "price": item["price"],
                "compareAtPrice": item["compareAtPrice"],
            }
        )
    return public_json({"products": products, "total": len(products)}, max_age=5, shared_max_age=10)


@api.post("/contact")
def contact():
    payload = request.get_json(silent=True) or {}
    required = ["name", "email", "subject", "message"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
    contact_row = ContactMessage(
        name=payload["name"],
        email=payload["email"],
        subject=payload["subject"],
        message=payload["message"],
    )
    db.session.add(contact_row)
    create_notification(
        "CONTACT_MESSAGE",
        "New contact message",
        f"{contact_row.name}: {contact_row.subject}",
        "/contact",
    )
    db.session.commit()
    return jsonify({"success": True, "id": contact_row.id}), 201


@api.get("/notifications")
def notifications():
    user, error_response = require_user()
    if error_response:
        return error_response
    limit = min(max(int(request.args.get("limit", 20)), 1), 50)
    unread_only = request.args.get("unreadOnly") == "true"
    query = Notification.query
    if not is_admin_user(user):
        query = query.filter(Notification.user_id == user.id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    rows = query.order_by(Notification.created_at.desc()).limit(limit).all()
    items = [notification_payload(row, user) for row in rows]
    unread_query = Notification.query.filter(Notification.is_read.is_(False))
    if not is_admin_user(user):
        unread_query = unread_query.filter(Notification.user_id == user.id)
    unread_count = unread_query.count()
    if is_admin_user(user) and not items and not unread_only:
        items = fallback_notifications(limit=limit)
    return jsonify(
        {
            "success": True,
            "data": {"notifications": items, "unreadCount": unread_count},
        }
    )


@api.post("/notifications/read")
def notifications_read():
    user, error_response = require_user()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    query = Notification.query
    if not is_admin_user(user):
        query = query.filter(Notification.user_id == user.id)
    if payload.get("all"):
        query.filter(Notification.is_read.is_(False)).update(
            {"is_read": True}, synchronize_session=False
        )
    else:
        ids = payload.get("ids") or []
        if ids:
            query.filter(Notification.id.in_(ids)).update(
                {"is_read": True}, synchronize_session=False
            )
    db.session.commit()
    return jsonify({"success": True})


@api.post("/newsletter")
def newsletter():
    payload = request.get_json(silent=True) or {}
    email = payload.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400
    existing = Subscriber.query.filter_by(email=email).first()
    if existing:
        existing.is_active = True
    else:
        db.session.add(Subscriber(email=email))
    db.session.commit()
    return jsonify({"success": True})


def user_payload(user):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "isActive": user.is_active,
        "createdAt": user.created_at.isoformat() if getattr(user, "created_at", None) else None,
        "updatedAt": user.updated_at.isoformat() if getattr(user, "updated_at", None) else None,
    }


def make_slug(value):
    slug = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return slug or f"product-{datetime.utcnow():%Y%m%d%H%M%S}"


def unique_slug(slug, product_id=None):
    base = make_slug(slug)
    candidate = base
    index = 2
    while True:
        query = Product.query.filter_by(slug=candidate)
        if product_id:
            query = query.filter(Product.id != product_id)
        if not query.first():
            return candidate
        candidate = f"{base}-{index}"
        index += 1


def unique_category_slug(slug, category_id=None):
    base = make_slug(slug).removeprefix("product-") or f"category-{datetime.utcnow():%Y%m%d%H%M%S}"
    candidate = base
    index = 2
    while True:
        query = Category.query.filter_by(slug=candidate)
        if category_id:
            query = query.filter(Category.id != category_id)
        if not query.first():
            return candidate
        candidate = f"{base}-{index}"
        index += 1


def unique_sku(sku, product_id=None):
    base = (sku or f"SKU-{datetime.utcnow():%Y%m%d%H%M%S}").strip()
    candidate = base
    index = 2
    while True:
        query = Product.query.filter_by(sku=candidate)
        if product_id:
            query = query.filter(Product.id != product_id)
        if not query.first():
            return candidate
        candidate = f"{base}-{index}"
        index += 1


def number_or_none(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def bool_value(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in {"0", "false", "no", "off", ""}
    return bool(value)


def int_value(value, default=0):
    number = number_or_none(value)
    return int(number if number is not None else default)


def translation_rows(payload):
    translations = payload.get("translations")
    if isinstance(translations, list):
        return [row for row in translations if isinstance(row, dict)]
    if isinstance(translations, dict):
        return [
            {"locale": locale, **row}
            for locale, row in translations.items()
            if isinstance(row, dict)
        ]
    return []


def upsert_category_translation(category, row, locale):
    name = (row.get("name") or "").strip()
    if not name:
        return
    translation = next((item for item in category.translations if item.locale == locale), None)
    if not translation:
        translation = CategoryTranslation(locale=locale)
        category.translations.append(translation)
    translation.name = name
    translation.description = (row.get("description") or "").strip() or None
    translation.meta_title = row.get("metaTitle") or name
    translation.meta_description = row.get("metaDescription") or translation.description


def apply_category_payload(category, payload):
    rows = translation_rows(payload)
    names = {
        (row.get("locale") or "en"): (row.get("name") or "").strip()
        for row in rows
        if isinstance(row, dict)
    }
    fallback_name = (
        payload.get("name")
        or payload.get("nameEn")
        or names.get("en")
        or names.get("zh")
        or category.slug
    )
    category.slug = unique_category_slug(payload.get("slug") or fallback_name, category.id)
    if "parentId" in payload:
        parent_id = payload.get("parentId") or None
        category.parent_id = parent_id if parent_id != category.id else None
    if "image" in payload or "imageUrl" in payload:
        category.image = (payload.get("image") or payload.get("imageUrl") or "").strip() or None
    if "sortOrder" in payload:
        category.sort_order = int_value(payload.get("sortOrder"), category.sort_order or 0)
    if "isActive" in payload:
        category.is_active = bool_value(payload.get("isActive"), category.is_active)

    if rows:
        for row in rows:
            locale = row.get("locale") or "en"
            if locale in ("en", "zh"):
                upsert_category_translation(category, row, locale)
    else:
        if payload.get("name") or payload.get("nameEn"):
            upsert_category_translation(
                category,
                {"name": payload.get("nameEn") or payload.get("name"), "description": payload.get("descriptionEn") or payload.get("description")},
                "en",
            )
        if payload.get("nameZh") or payload.get("descriptionZh"):
            upsert_category_translation(
                category,
                {"name": payload.get("nameZh") or payload.get("name"), "description": payload.get("descriptionZh")},
                "zh",
            )
    return category


def upsert_banner_translation(banner, row, locale):
    translation = next((item for item in banner.translations if item.locale == locale), None)
    if not translation:
        translation = BannerTranslation(locale=locale)
        banner.translations.append(translation)
    translation.title = (row.get("title") or "").strip() or None
    translation.subtitle = (row.get("subtitle") or "").strip() or None
    translation.button_text = (row.get("buttonText") or row.get("button_text") or "").strip() or None


def apply_banner_payload(banner, payload):
    if "position" in payload:
        banner.position = (payload.get("position") or "hero").strip() or "hero"
    if "image" in payload or "imageUrl" in payload:
        banner.image = (payload.get("image") or payload.get("imageUrl") or "").strip()
    if "link" in payload:
        banner.link = (payload.get("link") or "").strip() or None
    if "sortOrder" in payload:
        banner.sort_order = int_value(payload.get("sortOrder"), banner.sort_order or 0)
    if "isActive" in payload:
        banner.is_active = bool_value(payload.get("isActive"), banner.is_active)
    for row in translation_rows(payload):
        locale = row.get("locale") or "en"
        if locale in LOCALES:
            upsert_banner_translation(banner, row, locale)
    return banner


def upsert_product_translation(product, payload, locale="en"):
    name = (payload.get("name") or product.slug).strip()
    description = (payload.get("description") or "").strip()
    short_description = (payload.get("shortDescription") or "").strip()
    translation = next((item for item in product.translations if item.locale == locale), None)
    if not translation:
        translation = ProductTranslation(locale=locale)
        product.translations.append(translation)
    translation.name = name
    translation.description = description
    translation.short_description = short_description
    translation.meta_title = payload.get("metaTitle") or name
    translation.meta_description = payload.get("metaDescription") or short_description or description[:180]


def apply_product_translations(product, payload):
    supported_product_locales = ("en", "zh")
    translations = payload.get("translations")
    if isinstance(translations, list) and translations:
        for row in translations:
            if not isinstance(row, dict):
                continue
            row_locale = row.get("locale") or "en"
            if row_locale not in supported_product_locales:
                continue
            if not row.get("name") and row_locale == "en":
                row = {**row, "name": payload.get("name") or product.slug}
            if row.get("name"):
                upsert_product_translation(product, row, row_locale)
        if product.id:
            ProductTranslation.query.filter(
                ProductTranslation.product_id == product.id,
                ProductTranslation.locale.notin_(supported_product_locales),
            ).delete(synchronize_session=False)
            db.session.flush()
        else:
            product.translations = [
                item for item in product.translations if item.locale in supported_product_locales
            ]
        if not any((row or {}).get("locale") == "en" for row in translations if isinstance(row, dict)):
            upsert_product_translation(product, payload, "en")
        return

    upsert_product_translation(product, payload, "en")
    if payload.get("zhName") or payload.get("zhDescription"):
        upsert_product_translation(
            product,
            {
                "name": payload.get("zhName") or payload.get("name"),
                "description": payload.get("zhDescription") or payload.get("description"),
                "shortDescription": payload.get("zhShortDescription") or payload.get("shortDescription"),
                "metaTitle": payload.get("zhMetaTitle"),
                "metaDescription": payload.get("zhMetaDescription"),
            },
            "zh",
        )


def replace_product_images(product, payload):
    if "images" not in payload and not any(key in payload for key in ("image", "imageUrl")):
        return
    images = payload.get("images")
    if isinstance(images, list):
        if product.id:
            ProductImage.query.filter_by(product_id=product.id).delete()
            db.session.flush()
        product.images = []
        for index, row in enumerate(images):
            if isinstance(row, str):
                url = row.strip()
                sort_order = index
                alt = payload.get("name") or product.slug
            elif isinstance(row, dict):
                url = (row.get("url") or "").strip()
                sort_order = int(row.get("sortOrder", index) or index)
                alt = row.get("alt") or payload.get("name") or product.slug
            else:
                continue
            if url:
                product.images.append(ProductImage(url=url, alt=alt, sort_order=sort_order))
        return

    image_url = (payload.get("image") or payload.get("imageUrl") or "").strip()
    if image_url:
        if product.images:
            product.images[0].url = image_url
            product.images[0].alt = payload.get("name") or product.slug
        else:
            product.images.append(
                ProductImage(url=image_url, alt=payload.get("name") or product.slug, sort_order=0)
            )


def replace_product_variants(product, payload):
    if "variants" not in payload:
        return
    variants = payload.get("variants")
    if not isinstance(variants, list):
        return
    if product.id:
        ProductVariant.query.filter_by(product_id=product.id).delete()
        db.session.flush()
    product.variants = []
    for index, row in enumerate(variants):
        if not isinstance(row, dict):
            continue
        sku = (row.get("sku") or "").strip()
        if not sku:
            continue
        price_value = number_or_none(row.get("price"))
        if price_value is None:
            price_value = number_or_none(payload.get("price")) or 0
        compare_value = number_or_none(row.get("compareAtPrice"))
        stock = int(number_or_none(row.get("stock")) or 0)
        low_stock = int(number_or_none(row.get("lowStockThreshold")) or 5)
        product.variants.append(
            ProductVariant(
                sku=sku,
                price=price_value,
                compare_at_price=compare_value,
                stock=stock,
                low_stock_threshold=low_stock,
                options=row.get("options") or {},
                is_active=bool(row.get("isActive", True)),
                sort_order=int(row.get("sortOrder", index) or index),
            )
        )


def normalize_ordered_ids(values):
    if not isinstance(values, list):
        return []
    ordered_ids = []
    seen = set()
    for value in values:
        item_id = str(value or "").strip()
        if not item_id or item_id in seen:
            continue
        ordered_ids.append(item_id)
        seen.add(item_id)
    return ordered_ids


def reorder_product_sort_orders(ordered_ids):
    current_rows = Product.query.order_by(Product.sort_order.asc(), Product.created_at.asc(), Product.id.asc()).all()
    current_by_id = {row.id: row for row in current_rows}
    selected_ids = [product_id for product_id in ordered_ids if product_id in current_by_id]
    if not selected_ids:
        return []
    selected_set = set(selected_ids)
    selected_rows = [current_by_id[product_id] for product_id in selected_ids]
    selected_iter = iter(selected_rows)
    reordered_rows = [next(selected_iter) if row.id in selected_set else row for row in current_rows]
    for index, row in enumerate(reordered_rows):
        row.sort_order = index
    return reordered_rows


def next_product_sort_order():
    max_sort_order = db.session.query(db.func.max(Product.sort_order)).scalar()
    return int(max_sort_order) + 1 if max_sort_order is not None else 0


def apply_product_payload(product, payload, default_status=None):
    product.slug = unique_slug(payload.get("slug") or payload.get("name") or product.slug, product.id)
    product.sku = unique_sku(payload.get("sku") or product.sku, product.id)
    product.status = payload.get("status") or default_status or product.status or "DRAFT"
    product.price = number_or_none(payload.get("price")) or 0
    product.compare_at_price = number_or_none(payload.get("compareAtPrice"))
    product.cost_price = number_or_none(payload.get("costPrice"))
    product.category_id = payload.get("categoryId") or None
    product.brand_name = payload.get("brandName") or product.brand_name or "Misicheng"
    product.weight = number_or_none(payload.get("weight"))
    product.is_featured = bool(payload.get("isFeatured", product.is_featured))
    product.is_new = bool(payload.get("isNew", product.is_new))
    product.sort_order = int(number_or_none(payload.get("sortOrder")) or product.sort_order or 0)
    if "specifications" in payload:
        product.specifications = merge_specs_with_template(payload.get("specifications") or [], load_spec_template())
    if "tradeInfo" in payload:
        trade_info = copy.deepcopy(payload.get("tradeInfo") or {})
        if isinstance(trade_info, dict):
            trade_info.pop("customizationOptions", None)
        else:
            trade_info = {}
        product.trade_info = trade_info
    apply_product_translations(product, payload)
    replace_product_images(product, payload)
    replace_product_variants(product, payload)
    return product


def create_product_from_payload(payload, default_status="DRAFT"):
    specifications = payload.get("specifications")
    if not isinstance(specifications, list) or not specifications:
        specifications = load_spec_template()
    else:
        specifications = merge_specs_with_template(specifications, load_spec_template())
    trade_info = copy.deepcopy(payload.get("tradeInfo") or {})
    if isinstance(trade_info, dict):
        trade_info.pop("customizationOptions", None)
    else:
        trade_info = {}
    product = Product(
        slug=unique_slug(payload.get("slug") or payload.get("name")),
        sku=unique_sku(payload.get("sku")),
        status=payload.get("status") or default_status,
        price=number_or_none(payload.get("price")) or 0,
        compare_at_price=number_or_none(payload.get("compareAtPrice")),
        cost_price=number_or_none(payload.get("costPrice")),
        category_id=payload.get("categoryId") or None,
        brand_name=payload.get("brandName") or "Misicheng",
        weight=number_or_none(payload.get("weight")),
        specifications=specifications,
        trade_info=trade_info,
        sort_order=next_product_sort_order(),
    )
    apply_product_payload(product, payload, default_status=default_status)
    db.session.add(product)
    return product


def user_by_email(email):
    normalized = (email or "").strip().lower()
    if not normalized:
        return None
    return User.query.filter_by(email=normalized).first()


@api.post("/auth/login")
def auth_login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    account_type = payload.get("type") or "user"
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401
    if not user.is_active:
        return jsonify({"error": "Account is disabled"}), 403
    if account_type == "vendor" and user.role != "VENDOR":
        return jsonify({"error": "This account is not registered as a vendor"}), 403

    return jsonify({"success": True, "user": user_payload(user)})


@api.post("/auth/change-password")
def auth_change_password():
    user, error_response = require_user()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    old_password = payload.get("oldPassword") or payload.get("currentPassword") or ""
    new_password = payload.get("newPassword") or ""
    if not old_password or len(new_password) < 8:
        return jsonify({"error": "Old password and an 8+ character new password are required"}), 400
    if not user.password_hash or not check_password_hash(user.password_hash, old_password):
        return jsonify({"error": "Old password is incorrect"}), 400
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"success": True})


@api.post("/auth/register")
def auth_register():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    if not name or not email or len(password) < 8:
        return jsonify({"error": "Name, email, and an 8+ character password are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(
        email=email,
        name=name,
        role="USER",
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"success": True, "user": user_payload(user)}), 201


@api.post("/auth/vendor-register")
def auth_vendor_register():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or payload.get("companyName") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    company_name = (payload.get("companyName") or "").strip()
    if not name or not email or len(password) < 8 or not company_name:
        return jsonify({"error": "Vendor name, company name, email, and password are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(
        email=email,
        name=name,
        role="VENDOR",
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    application = VendorApplication(
        user=user,
        email=email,
        name=name,
        company_name=company_name,
        contact_person=(payload.get("contactPerson") or name).strip(),
        phone=(payload.get("phone") or "").strip() or None,
        country=(payload.get("country") or "").strip() or None,
        address=(payload.get("address") or "").strip() or None,
        description=(payload.get("description") or "").strip() or None,
        certification_files=payload.get("certificationFiles") or [],
    )
    db.session.add(application)
    create_notification(
        "CONTACT_MESSAGE",
        "New vendor application",
        f"{company_name} submitted a vendor application",
        "/admin",
    )
    db.session.commit()
    return jsonify({"success": True, "user": user_payload(user), "application": application.to_dict()}), 201


@api.post("/vendor/application-upload")
def vendor_application_upload():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "File is required"}), 400
    if not allowed_vendor_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    if uploaded_file_size(file) > MAX_MEDIA_UPLOAD_BYTES:
        return jsonify({"error": "File must be smaller than 10MB"}), 400

    upload_dir = UPLOAD_ROOT / "vendor-applications"
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = secure_filename(file.filename) or "application-file"
    ext = safe_name.rsplit(".", 1)[-1].lower()
    stored_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:10]}.{ext}"
    file.save(upload_dir / stored_name)
    return jsonify(
        {
            "success": True,
            "name": safe_name,
            "url": f"/api/uploads/vendor-applications/{stored_name}",
        }
    )


@api.post("/vendor/media")
def vendor_media_upload():
    user, error_response = require_vendor()
    if error_response:
        return error_response
    return save_product_media_upload(*user_media_parts(user, "vendors"), preset_keys=VENDOR_MEDIA_CATEGORY_PRESETS)


@api.delete("/vendor/media")
def vendor_media_delete():
    user, error_response = require_vendor()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    return delete_product_media_upload(
        payload.get("storageKey") or payload.get("key") or payload.get("url") or payload.get("mediaUrl"),
        *user_media_parts(user, "vendors"),
        vendor_id=user.id,
    )


@api.patch("/vendor/media")
def vendor_media_update():
    user, error_response = require_vendor()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    return move_product_media_upload(
        payload.get("storageKey") or payload.get("key") or payload.get("url") or payload.get("mediaUrl"),
        payload.get("category") or payload.get("categoryId") or payload.get("category_id") or "",
        *user_media_parts(user, "vendors"),
        vendor_id=user.id,
        preset_keys=VENDOR_MEDIA_CATEGORY_PRESETS,
        target_name=payload.get("name") or payload.get("filename") or payload.get("fileName"),
    )


@api.post("/vendor/media/categories")
def vendor_media_category_create():
    user, error_response = require_vendor()
    if error_response:
        return error_response
    return create_product_media_category(*user_media_parts(user, "vendors"), preset_keys=VENDOR_MEDIA_CATEGORY_PRESETS)


@api.delete("/vendor/media/categories")
def vendor_media_category_delete():
    user, error_response = require_vendor()
    if error_response:
        return error_response
    return delete_product_media_category(*user_media_parts(user, "vendors"), vendor_id=user.id, preset_keys=VENDOR_MEDIA_CATEGORY_PRESETS)


@api.get("/vendor/application")
def vendor_application():
    user, error_response = require_vendor()
    if error_response:
        return error_response
    email = normalize_email(request.args.get("email") or request.args.get("userEmail") or user.email)
    if email != user.email:
        return jsonify({"error": "Access denied"}), 403
    application = None
    if email:
        application = VendorApplication.query.filter_by(email=email).order_by(VendorApplication.created_at.desc()).first()
    if not application:
        return jsonify({"error": "Application not found"}), 404
    return jsonify({"success": True, "data": application.to_dict()})


@api.get("/vendor/products")
def vendor_products():
    user, error_response = require_vendor()
    if error_response:
        return error_response
    locale = get_locale()
    email = normalize_email(request.args.get("email") or request.args.get("userEmail") or user.email)
    if email != user.email:
        return jsonify({"error": "Access denied"}), 403
    query = Product.query.filter(Product.vendor_id == user.id)
    rows = query.order_by(Product.sort_order.asc(), Product.created_at.asc(), Product.id.asc()).all()
    return jsonify({"products": [row.to_dict(locale=locale) for row in rows]})


@api.post("/vendor/products")
def vendor_product_create():
    user, error_response = require_vendor()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    application = (
        VendorApplication.query.filter_by(email=user.email)
        .order_by(VendorApplication.created_at.desc())
        .first()
    )
    if not application or application.status != "APPROVED":
        return jsonify({"error": "Vendor application must be approved before product submission"}), 403
    if not (payload.get("name") or payload.get("nameEn") or any((row or {}).get("name") for row in payload.get("translations") or [])) or not payload.get("sku"):
        return jsonify({"error": "Product name and SKU are required"}), 400
    product = create_product_from_payload(payload, default_status="PENDING_REVIEW")
    product.vendor_id = user.id
    product.submitted_at = datetime.utcnow()
    product.status = "PENDING_REVIEW"
    create_notification(
        "PRODUCT_REVIEW",
        "New product pending review",
        f"{payload.get('name')} was submitted by a vendor",
        "/admin/products?status=PENDING_REVIEW",
    )
    db.session.commit()
    return jsonify({"success": True, "product": product.to_dict(locale=get_locale())}), 201


@api.patch("/vendor/products/<product_id>")
def vendor_product_update(product_id):
    user, error_response = require_vendor()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    application = (
        VendorApplication.query.filter_by(email=user.email)
        .order_by(VendorApplication.created_at.desc())
        .first()
    )
    if not application or application.status != "APPROVED":
        return jsonify({"error": "Vendor application must be approved before product submission"}), 403
    product = Product.query.get_or_404(product_id)
    if product.vendor_id != user.id:
        return jsonify({"error": "Product does not belong to this vendor"}), 403
    apply_product_payload(product, payload, default_status="PENDING_REVIEW")
    product.submitted_at = datetime.utcnow()
    product.reviewed_at = None
    product.rejection_reason = None
    product.status = "PENDING_REVIEW"
    create_notification(
        "PRODUCT_REVIEW",
        "Product resubmitted for review",
        f"{product.to_dict(locale='en')['name']} was resubmitted by a vendor",
        "/admin/products?status=PENDING_REVIEW",
    )
    db.session.commit()
    return jsonify({"success": True, "product": product.to_dict(locale=get_locale())})


@api.patch("/vendor/products/reorder")
def vendor_products_reorder():
    user, error_response = require_vendor()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    ordered_ids = normalize_ordered_ids(payload.get("orderedIds") or payload.get("ids") or [])
    if not ordered_ids:
        return jsonify({"error": "Product order is required"}), 400
    allowed_ids = {
        row_id for (row_id,) in Product.query.filter(Product.vendor_id == user.id).with_entities(Product.id).all()
    }
    current_ids = {row_id for (row_id,) in Product.query.with_entities(Product.id).all()}
    if any(product_id in current_ids and product_id not in allowed_ids for product_id in ordered_ids):
        return jsonify({"error": "Access denied"}), 403
    ordered_ids = [product_id for product_id in ordered_ids if product_id in allowed_ids]
    if not ordered_ids:
        return jsonify({"error": "No products matched the requested order"}), 404
    reordered_rows = reorder_product_sort_orders(ordered_ids)
    if not reordered_rows:
        return jsonify({"error": "No products matched the requested order"}), 404
    db.session.commit()
    return jsonify({"success": True, "count": len(reordered_rows)})


@api.get("/vendor/media")
def vendor_media():
    user, error_response = require_vendor()
    if error_response:
        return error_response
    email = normalize_email(request.args.get("email") or request.args.get("userEmail") or user.email)
    if email != user.email:
        return jsonify({"error": "Access denied"}), 403
    data = media_category_response(*user_media_parts(user, "vendors"), limit=200, preset_keys=VENDOR_MEDIA_CATEGORY_PRESETS)
    return jsonify(data)


@api.get("/inquiries")
def list_inquiries():
    user, error_response = require_user()
    if error_response:
        return error_response
    query = Inquiry.query.order_by(Inquiry.created_at.desc())
    if not is_admin_user(user):
        query = query.filter(Inquiry.user_id == user.id)
    rows = query.limit(100).all()
    return jsonify({"success": True, "data": [row.to_dict(include_quotes=True) for row in rows], "inquiries": [row.to_dict(include_quotes=True) for row in rows]})


@api.post("/inquiries")
def create_inquiry():
    user, error_response = require_user()
    if error_response:
        return error_response

    payload = request.get_json(silent=True) or {}
    contact = payload.get("contact") or payload
    items = payload.get("items") or []
    contact_name = (contact.get("contactName") or user.name or user.email).strip()
    contact_email = normalize_email(contact.get("email") or user.email)
    if contact_email != user.email:
        return jsonify({"error": "Inquiry email must match the logged-in account"}), 403
    if not contact_name or not contact_email:
        return jsonify({"error": "Contact name and email are required"}), 400
    if not items:
        return jsonify({"error": "Inquiry requires at least one item"}), 400

    count = Inquiry.query.count() + 1
    inquiry = Inquiry(
        inquiry_number=f"INQ-{datetime.utcnow():%Y%m%d}-{count:04d}",
        user_id=user.id,
        contact_name=contact_name,
        company_name=contact.get("companyName"),
        email=contact_email,
        phone=contact.get("phone"),
        country=contact.get("country"),
        quantity_requirements=contact.get("quantityRequirements"),
        customization_needs=contact.get("customizationNeeds"),
        expected_delivery_time=contact.get("expectedDeliveryTime"),
        message=contact.get("message"),
    )
    for item in items:
        inquiry.items.append(
            InquiryItem(
                product_id=item.get("productId"),
                variant_id=item.get("variantId"),
                name=item.get("name") or "Product",
                image=item.get("image"),
                price=item.get("price") or 0,
                quantity=item.get("quantity") or 1,
                options=item.get("options") or {},
                note=item.get("note"),
            )
        )
    inquiry.messages.append(
        InquiryMessage(
            sender_type="SYSTEM",
            content="Inquiry submitted successfully. Sales will follow up within 1-2 business days.",
        )
    )
    db.session.add(inquiry)
    create_notification(
        "INQUIRY_SUBMITTED",
        "New inquiry submitted",
        f"{inquiry.contact_name} submitted {inquiry.inquiry_number}",
        f"/admin/orders/{inquiry.id}",
    )
    db.session.commit()
    return jsonify({"success": True, "data": inquiry.to_dict(include_messages=True, include_quotes=True), "inquiry": inquiry.to_dict(include_messages=True, include_quotes=True)}), 201


@api.get("/inquiries/<inquiry_id>")
def inquiry_detail(inquiry_id):
    user, error_response = require_user()
    if error_response:
        return error_response
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    if not can_access_inquiry(user, inquiry):
        return jsonify({"error": "Access denied"}), 403
    return jsonify({"success": True, "data": inquiry.to_dict(include_messages=True, include_quotes=True), "inquiry": inquiry.to_dict(include_messages=True, include_quotes=True)})


@api.patch("/inquiries/<inquiry_id>")
def update_inquiry_status(inquiry_id):
    user, error_response = require_user()
    if error_response:
        return error_response
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    if not can_access_inquiry(user, inquiry):
        return jsonify({"error": "Access denied"}), 403

    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    valid_statuses = {"SUBMITTED", "REVIEWING", "QUOTED", "ACCEPTED", "REJECTED", "EXPIRED", "CANCELLED"}
    if status not in valid_statuses:
        return jsonify({"error": "Invalid status"}), 400
    if not is_admin_user(user) and status not in {"ACCEPTED", "REJECTED"}:
        return jsonify({"error": "Users can only accept or reject quoted inquiries"}), 403

    inquiry.status = status
    if status in {"ACCEPTED", "REJECTED"}:
        inquiry.messages.append(
            InquiryMessage(
                sender_id=user.id,
                sender_type="USER",
                content="Quote accepted." if status == "ACCEPTED" else "Quote rejected.",
            )
        )
        create_notification(
            "QUOTE_ACCEPTED" if status == "ACCEPTED" else "QUOTE_REJECTED",
            f"Inquiry {inquiry.inquiry_number} {status.lower()}",
            f"{inquiry.contact_name} updated the quote response.",
            f"/admin/orders/{inquiry.id}",
        )
    else:
        create_notification(
            "INQUIRY_STATUS",
            f"Inquiry {inquiry.inquiry_number} status updated",
            f"Status changed to {status}.",
            f"/account/inquiries/{inquiry.id}",
            inquiry.user_id,
        )
    db.session.commit()
    return jsonify({"success": True, "data": inquiry.to_dict(include_messages=True, include_quotes=True), "inquiry": inquiry.to_dict(include_messages=True, include_quotes=True)})


@api.get("/inquiries/<inquiry_id>/messages")
def inquiry_messages(inquiry_id):
    user, error_response = require_user()
    if error_response:
        return error_response
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    if not can_access_inquiry(user, inquiry):
        return jsonify({"error": "Access denied"}), 403

    view_as = request.args.get("viewAs")
    effective_role = "ADMIN" if is_admin_user(user) and view_as == "ADMIN" else "USER"
    for message in inquiry.messages:
        if (
            not message.read_at
            and message.sender_type != "SYSTEM"
            and not (message.sender_id == user.id and message.sender_type == effective_role)
        ):
            message.read_at = datetime.utcnow()
    Notification.query.filter(
        Notification.user_id == user.id,
        Notification.type == "NEW_MESSAGE",
        Notification.is_read.is_(False),
        Notification.link.ilike(f"%{inquiry_id}%"),
    ).update({"is_read": True}, synchronize_session=False)
    db.session.commit()
    return jsonify({"success": True, "data": [message.to_dict() for message in inquiry.messages], "messages": [message.to_dict() for message in inquiry.messages]})


@api.post("/inquiries/<inquiry_id>/messages")
def create_inquiry_message(inquiry_id):
    user, error_response = require_user()
    if error_response:
        return error_response
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    if not can_access_inquiry(user, inquiry):
        return jsonify({"error": "Access denied"}), 403

    payload = request.get_json(silent=True) or {}
    content = (payload.get("content") or "").strip()
    if not content:
        return jsonify({"error": "Message content is required"}), 400

    sender_type = "ADMIN" if is_admin_user(user) else "USER"
    if payload.get("senderType") == "USER" and is_admin_user(user):
        sender_type = "USER"
    message = InquiryMessage(
        inquiry_id=inquiry.id,
        sender_id=user.id,
        sender_type=sender_type,
        content=content,
    )
    db.session.add(message)
    if sender_type == "ADMIN":
        create_notification(
            "NEW_MESSAGE",
            f"Inquiry {inquiry.inquiry_number} has a new message",
            content[:160],
            f"/account/inquiries/{inquiry.id}",
            inquiry.user_id,
        )
    else:
        create_notification(
            "NEW_MESSAGE",
            f"Inquiry {inquiry.inquiry_number} has a new message",
            content[:160],
            f"/admin/orders/{inquiry.id}",
        )
    db.session.commit()
    return jsonify({"success": True, "data": message.to_dict(), "message": message.to_dict()}), 201


@api.post("/inquiries/<inquiry_id>/quotes")
def create_quote(inquiry_id):
    admin, error_response = require_admin()
    if error_response:
        return error_response
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    payload = request.get_json(silent=True) or {}
    items = payload.get("items") or []
    valid_until = parse_date(payload.get("validUntil"))
    if not items or not valid_until:
        return jsonify({"error": "Items and validUntil are required"}), 400

    quote = Quote(
        inquiry_id=inquiry.id,
        valid_until=valid_until,
        notes=payload.get("notes"),
        total_amount=0,
    )
    total = replace_quote_items(quote, items)
    inquiry.status = "QUOTED"
    inquiry.messages.append(
        InquiryMessage(
            sender_id=admin.id,
            sender_type="SYSTEM",
            content=f"Sales submitted a quote, total amount: ${total:.2f}, valid until: {valid_until:%Y-%m-%d}.",
        )
    )
    db.session.add(quote)
    create_notification(
        "QUOTE_RECEIVED",
        f"Inquiry {inquiry.inquiry_number} received a quote",
        "Sales has provided a quote. Please review it.",
        f"/account/inquiries/{inquiry.id}",
        inquiry.user_id,
    )
    db.session.commit()
    return jsonify({"success": True, "data": quote.to_dict(), "quote": quote.to_dict()}), 201


def replace_quote_items(quote, items):
    if quote.id:
        QuoteItem.query.filter_by(quote_id=quote.id).delete()
        db.session.flush()
    quote.items = []
    total = 0
    for item in items:
        quantity = max(int(number_or_none(item.get("quantity")) or 1), 1)
        unit_price = max(number_or_none(item.get("unitPrice")) or 0, 0)
        line_total = quantity * unit_price
        total += line_total
        quote.items.append(
            QuoteItem(
                product_id=item.get("productId"),
                variant_id=item.get("variantId"),
                name=item.get("name") or "Product",
                quantity=quantity,
                unit_price=unit_price,
                total_price=line_total,
                options=item.get("options") or {},
            )
        )
    quote.total_amount = total
    return total


@api.patch("/inquiries/<inquiry_id>/quotes/<quote_id>")
def update_quote(inquiry_id, quote_id):
    admin, error_response = require_admin()
    if error_response:
        return error_response
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    quote = Quote.query.filter_by(id=quote_id, inquiry_id=inquiry.id).first_or_404()
    payload = request.get_json(silent=True) or {}
    items = payload.get("items") or []
    valid_until = parse_date(payload.get("validUntil"))
    if not items or not valid_until:
        return jsonify({"error": "Items and validUntil are required"}), 400

    total = replace_quote_items(quote, items)
    quote.valid_until = valid_until
    quote.notes = payload.get("notes")
    inquiry.status = "QUOTED"
    inquiry.messages.append(
        InquiryMessage(
            sender_id=admin.id,
            sender_type="SYSTEM",
            content=f"Sales updated a quote, total amount: ${total:.2f}, valid until: {valid_until:%Y-%m-%d}.",
        )
    )
    create_notification(
        "QUOTE_RECEIVED",
        f"Inquiry {inquiry.inquiry_number} quote was updated",
        "Sales has updated the quote. Please review it.",
        f"/account/inquiries/{inquiry.id}",
        inquiry.user_id,
    )
    db.session.commit()
    return jsonify({"success": True, "data": quote.to_dict(), "quote": quote.to_dict()})


@api.get("/admin/analytics")
def admin_analytics():
    _, error_response = require_admin()
    if error_response:
        return error_response
    total_products = Product.query.count()
    active_products = Product.query.filter_by(status="ACTIVE").count()
    total_users = User.query.count()
    total_inquiries = Inquiry.query.count()
    total_contacts = ContactMessage.query.count()
    monthly_data = []
    now = datetime.utcnow()
    for offset in range(11, -1, -1):
        start = datetime(now.year, now.month, 1)
        month = start.month - offset
        year = start.year
        while month <= 0:
            month += 12
            year -= 1
        current = datetime(year, month, 1)
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        count = Inquiry.query.filter(
            Inquiry.created_at >= current, Inquiry.created_at < next_month
        ).count()
        monthly_data.append({"month": current.strftime("%b"), "inquiries": count})

    top_products = (
        Product.query.filter_by(status="ACTIVE")
        .order_by(Product.sort_order.asc())
        .limit(5)
        .all()
    )
    return jsonify(
        {
            "stats": {
                "totalProducts": total_products,
                "activeProducts": active_products,
                "totalUsers": total_users,
                "newUsers": total_users,
                "newUsersChange": "0%",
                "totalInquiries": total_inquiries,
                "inquiries": total_inquiries,
                "inquiriesChange": "0%",
                "pageViews": 0,
                "pageViewsChange": "0%",
                "contactMessages": total_contacts,
            },
            "monthlyData": monthly_data,
            "topProducts": [
                {"name": product.to_dict(locale="zh")["name"], "units": product.sort_order + 1}
                for product in top_products
            ],
            "topCountries": [],
            "trafficSources": [],
            "topPages": [],
        }
    )


@api.get("/admin/products")
def admin_products():
    _, error_response = require_admin()
    if error_response:
        return error_response
    locale = get_locale()
    rows = Product.query.order_by(Product.sort_order.asc(), Product.created_at.asc(), Product.id.asc()).all()
    return jsonify({"products": [row.to_dict(locale=locale) for row in rows]})


@api.patch("/admin/products/reorder")
def admin_products_reorder():
    _, error_response = require_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    ordered_ids = normalize_ordered_ids(payload.get("orderedIds") or payload.get("ids") or [])
    if not ordered_ids:
        return jsonify({"error": "Product order is required"}), 400
    reordered_rows = reorder_product_sort_orders(ordered_ids)
    if not reordered_rows:
        return jsonify({"error": "No products matched the requested order"}), 404
    db.session.commit()
    return jsonify({"success": True, "count": len(reordered_rows)})


@api.get("/spec-template")
def product_spec_template():
    return jsonify({"template": load_spec_template()})


@api.get("/admin/spec-template")
def admin_spec_template():
    _, error_response = require_admin()
    if error_response:
        return error_response
    return jsonify({"template": load_spec_template(), "productCount": Product.query.count()})


@api.put("/admin/spec-template")
def admin_spec_template_update():
    _, error_response = require_elevated_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    template = payload.get("template") or payload.get("specifications") or []
    if not isinstance(template, list):
        return jsonify({"error": "Template must be a list"}), 400
    previous_template = load_spec_template()
    saved_template = save_spec_template(template)
    synced_count = 0
    if payload.get("syncProducts", True):
        for product in Product.query.all():
            product.specifications = merge_specs_with_template(product.specifications or [], saved_template, previous_template)
            synced_count += 1
        db.session.commit()
    return jsonify({"success": True, "template": saved_template, "syncedCount": synced_count})


@api.post("/admin/products")
def admin_product_create():
    _, error_response = require_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    if not (payload.get("name") or payload.get("nameEn") or any((row or {}).get("name") for row in payload.get("translations") or [])) or not payload.get("sku"):
        return jsonify({"error": "Product name and SKU are required"}), 400
    product = create_product_from_payload(payload, default_status=payload.get("status") or "ACTIVE")
    db.session.commit()
    return jsonify({"success": True, "product": product.to_dict(locale=get_locale())}), 201


@api.patch("/admin/products/<product_id>")
def admin_product_update(product_id):
    admin, error_response = require_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    product = Product.query.get_or_404(product_id)
    business_keys = {key for key in payload.keys() if key not in {"userId", "user_id", "userEmail"}}
    if business_keys <= {"status", "rejectionReason", "reviewNote"}:
        product.status = payload.get("status") or product.status
        if product.status in ("ACTIVE", "REJECTED"):
            product.reviewed_at = datetime.utcnow()
            product.reviewed_by_id = admin.id
        if product.status == "REJECTED":
            product.rejection_reason = payload.get("rejectionReason") or payload.get("reviewNote") or "Rejected by admin"
    else:
        apply_product_payload(product, payload, default_status=product.status)
    db.session.commit()
    return jsonify({"success": True, "product": product.to_dict(locale=get_locale())})


@api.delete("/admin/products/<product_id>")
def admin_product_delete(product_id):
    _, error_response = require_admin()
    if error_response:
        return error_response
    product = Product.query.get_or_404(product_id)
    InquiryItem.query.filter_by(product_id=product.id).update({"product_id": None}, synchronize_session=False)
    QuoteItem.query.filter_by(product_id=product.id).update({"product_id": None}, synchronize_session=False)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"success": True})


@api.get("/admin/categories")
def admin_categories():
    _, error_response = require_admin()
    if error_response:
        return error_response
    locale = get_locale()
    rows = Category.query.order_by(Category.sort_order.asc()).all()
    return jsonify({"categories": [row.to_dict(locale=locale) for row in rows]})


@api.post("/admin/categories")
def admin_category_create():
    _, error_response = require_elevated_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    rows = translation_rows(payload)
    has_name = payload.get("name") or payload.get("nameEn") or any((row or {}).get("name") for row in rows)
    if not has_name:
        return jsonify({"error": "Category name is required"}), 400
    category = Category(
        slug=unique_category_slug(payload.get("slug") or payload.get("name") or payload.get("nameEn")),
        image=(payload.get("image") or payload.get("imageUrl") or "").strip() or None,
        sort_order=int_value(payload.get("sortOrder"), Category.query.count()),
        is_active=bool_value(payload.get("isActive"), True),
    )
    db.session.add(category)
    apply_category_payload(category, payload)
    db.session.commit()
    return jsonify({"success": True, "category": category.to_dict(locale=get_locale())}), 201


@api.patch("/admin/categories/<category_id>")
def admin_category_update(category_id):
    _, error_response = require_elevated_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    category = Category.query.get_or_404(category_id)
    apply_category_payload(category, payload)
    db.session.commit()
    return jsonify({"success": True, "category": category.to_dict(locale=get_locale())})


@api.get("/admin/banners")
def admin_banners():
    _, error_response = require_elevated_admin()
    if error_response:
        return error_response
    locale = get_locale()
    rows = Banner.query.order_by(Banner.position.asc(), Banner.sort_order.asc()).all()
    return jsonify({"banners": [row.to_dict(locale=locale) for row in rows]})


@api.post("/admin/banners")
def admin_banner_create():
    _, error_response = require_elevated_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    image = (payload.get("image") or payload.get("imageUrl") or "").strip()
    if not image:
        return jsonify({"error": "Banner image is required"}), 400
    banner = Banner(
        position=(payload.get("position") or "hero").strip() or "hero",
        image=image,
        link=(payload.get("link") or "").strip() or None,
        is_active=bool_value(payload.get("isActive"), True),
        sort_order=int_value(payload.get("sortOrder"), Banner.query.count()),
    )
    db.session.add(banner)
    apply_banner_payload(banner, payload)
    db.session.commit()
    return jsonify({"success": True, "banner": banner.to_dict(locale=get_locale())}), 201


@api.patch("/admin/banners/<banner_id>")
def admin_banner_update(banner_id):
    _, error_response = require_elevated_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    banner = Banner.query.get_or_404(banner_id)
    apply_banner_payload(banner, payload)
    if not banner.image:
        return jsonify({"error": "Banner image is required"}), 400
    db.session.commit()
    return jsonify({"success": True, "banner": banner.to_dict(locale=get_locale())})


@api.get("/admin/vendors")
def admin_vendors():
    _, error_response = require_admin()
    if error_response:
        return error_response
    rows = VendorApplication.query.order_by(VendorApplication.created_at.desc()).all()
    return jsonify({"vendors": [row.to_dict() for row in rows]})


@api.patch("/admin/vendors/<application_id>")
def admin_vendor_update(application_id):
    _, error_response = require_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    application = VendorApplication.query.get_or_404(application_id)
    status = payload.get("status")
    if status not in ("PENDING", "APPROVED", "REJECTED", "DISABLED"):
        return jsonify({"error": "Invalid vendor status"}), 400
    application.status = status
    application.review_note = (payload.get("reviewNote") or "").strip() or None
    application.reviewed_at = datetime.utcnow()
    if application.user:
        application.user.is_active = status != "DISABLED"
    create_notification(
        "VENDOR_REVIEW",
        "Vendor application updated",
        f"{application.company_name} status changed to {status}",
        "/vendor/application",
        application.user_id,
    )
    db.session.commit()
    return jsonify({"success": True, "data": application.to_dict()})


@api.get("/admin/i18n")
def admin_i18n():
    _, error_response = require_elevated_admin()
    if error_response:
        return error_response
    selected_locale = request.args.get("locale") or "zh"
    return jsonify({"success": True, "data": get_admin_i18n_data(selected_locale)})


@api.put("/admin/i18n")
def admin_i18n_update():
    _, error_response = require_elevated_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    locale = payload.get("locale")
    translations = payload.get("translations") or {}
    if locale not in LOCALES or locale == "en":
        return jsonify({"error": "Invalid locale"}), 400
    if not isinstance(translations, dict):
        return jsonify({"error": "Translations must be an object"}), 400
    try:
        update_admin_locale_messages(locale, translations)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"success": True, "data": get_admin_i18n_data(locale)})


@api.get("/admin/inquiries")
def admin_inquiries():
    _, error_response = require_admin()
    if error_response:
        return error_response
    rows = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(500).all()
    return jsonify({"success": True, "data": [row.to_dict(include_quotes=True) for row in rows], "inquiries": [row.to_dict(include_quotes=True) for row in rows]})


@api.get("/admin/inquiries/<inquiry_id>")
def admin_inquiry_detail(inquiry_id):
    _, error_response = require_admin()
    if error_response:
        return error_response
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    return jsonify({"success": True, "data": inquiry.to_dict(include_messages=True, include_quotes=True), "inquiry": inquiry.to_dict(include_messages=True, include_quotes=True)})


@api.post("/admin/inquiries/<inquiry_id>/messages")
def admin_create_inquiry_message(inquiry_id):
    return create_inquiry_message(inquiry_id)


@api.post("/admin/inquiries/<inquiry_id>/quotes")
def admin_create_quote(inquiry_id):
    return create_quote(inquiry_id)


@api.get("/admin/users")
def admin_users():
    _, error_response = require_elevated_admin()
    if error_response:
        return error_response
    rows = (
        User.query.filter(~User.role.in_(ADMIN_ROLES))
        .order_by(User.created_at.desc())
        .limit(500)
        .all()
    )
    return jsonify({"users": [user_payload(row) for row in rows]})


@api.patch("/admin/users/<user_id>")
def admin_user_update(user_id):
    _, error_response = require_elevated_admin()
    if error_response:
        return error_response
    target = User.query.get_or_404(user_id)
    if target.role in ADMIN_ROLES:
        return jsonify({"error": "Admin accounts must be managed from admin management"}), 400
    payload = request.get_json(silent=True) or {}
    if "email" in payload:
        email = normalize_email(payload.get("email"))
        if not email:
            return jsonify({"error": "Email is required"}), 400
        existing = User.query.filter(User.email == email, User.id != target.id).first()
        if existing:
            return jsonify({"error": "Email already exists"}), 409
        if target.email != email:
            target.email = email
            VendorApplication.query.filter_by(user_id=target.id).update({"email": email})
    if "name" in payload:
        return jsonify({"error": "Customer name cannot be changed here"}), 400
    if "role" in payload:
        role = payload.get("role")
        if role not in CUSTOMER_ROLES:
            return jsonify({"error": "Invalid customer role"}), 400
        target.role = role
    if "isActive" in payload:
        target.is_active = bool_value(payload.get("isActive"), target.is_active)
    password = payload.get("password") or ""
    if password:
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400
        target.password_hash = generate_password_hash(password)
    db.session.commit()
    return jsonify({"success": True, "user": user_payload(target)})


@api.get("/admin/admins")
def admin_admins():
    _, error_response = require_elevated_admin()
    if error_response:
        return error_response
    rows = (
        User.query.filter(User.role.in_(ADMIN_ROLES))
        .order_by(User.role.desc(), User.created_at.desc())
        .all()
    )
    return jsonify({"admins": [user_payload(row) for row in rows]})


@api.post("/admin/admins")
def admin_admin_create():
    current_admin, error_response = require_elevated_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    email = normalize_email(payload.get("email"))
    name = (payload.get("name") or email or "").strip()
    password = payload.get("password") or ""
    if not email or not name or len(password) < 8:
        return jsonify({"error": "Name, email, and an 8+ character password are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409
    role = payload.get("role") or BASIC_ADMIN_ROLE
    if role == SUPER_ADMIN_ROLE:
        return jsonify({"error": "Super admin cannot be created here"}), 400
    if role not in ASSIGNABLE_ADMIN_ROLES:
        return jsonify({"error": "Invalid admin role"}), 400
    if role != BASIC_ADMIN_ROLE and not is_super_admin_user(current_admin):
        return jsonify({"error": "Only super admin can assign elevated admin role"}), 403
    user = User(
        email=email,
        name=name,
        role=role,
        is_active=bool_value(payload.get("isActive"), True),
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"success": True, "admin": user_payload(user)}), 201


@api.patch("/admin/admins/<admin_id>")
def admin_admin_update(admin_id):
    current_admin, error_response = require_elevated_admin()
    if error_response:
        return error_response
    target = User.query.get_or_404(admin_id)
    if target.role not in ADMIN_ROLES:
        return jsonify({"error": "Target user is not an admin"}), 400
    if target.role == SUPER_ADMIN_ROLE:
        return jsonify({"error": "Super admin cannot be changed here"}), 400
    is_self = target.id == current_admin.id
    if not is_super_admin_user(current_admin) and target.role != BASIC_ADMIN_ROLE and not is_self:
        return jsonify({"error": "Only super admin can change elevated admins"}), 403
    payload = request.get_json(silent=True) or {}
    if target.id == current_admin.id and payload.get("isActive") is False:
        return jsonify({"error": "You cannot disable your own account"}), 400
    if "email" in payload:
        email = normalize_email(payload.get("email"))
        if not email:
            return jsonify({"error": "Email is required"}), 400
        existing = User.query.filter(User.email == email, User.id != target.id).first()
        if existing:
            return jsonify({"error": "Email already exists"}), 409
        target.email = email
    if "name" in payload:
        target.name = (payload.get("name") or target.email).strip()
    if "role" in payload:
        role = payload.get("role")
        if role == SUPER_ADMIN_ROLE:
            return jsonify({"error": "Super admin role cannot be assigned here"}), 400
        if role not in ASSIGNABLE_ADMIN_ROLES:
            return jsonify({"error": "Invalid admin role"}), 400
        if role != target.role and not is_super_admin_user(current_admin):
            return jsonify({"error": "Only super admin can change admin role"}), 403
        if is_self and role != target.role:
            return jsonify({"error": "You cannot change your own admin role"}), 400
        target.role = role
    if "isActive" in payload:
        target.is_active = bool_value(payload.get("isActive"), target.is_active)
    password = payload.get("password") or ""
    if password:
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400
        target.password_hash = generate_password_hash(password)
    db.session.commit()
    return jsonify({"success": True, "admin": user_payload(target)})


@api.delete("/admin/admins/<admin_id>")
def admin_admin_delete(admin_id):
    current_admin, error_response = require_super_admin()
    if error_response:
        return error_response
    target = User.query.get_or_404(admin_id)
    if target.id == current_admin.id:
        return jsonify({"error": "You cannot delete your own account"}), 400
    if target.role == SUPER_ADMIN_ROLE:
        return jsonify({"error": "Super admin cannot be deleted"}), 400
    if target.role not in ADMIN_ROLES:
        return jsonify({"error": "Target user is not an admin"}), 400
    db.session.delete(target)
    db.session.commit()
    return jsonify({"success": True})


@api.get("/admin/media")
def admin_media():
    user, error_response = require_admin()
    if error_response:
        return error_response
    migrate_admin_media_to_shared()
    data = media_category_response(*admin_media_parts(), limit=300, preset_keys=ADMIN_MEDIA_CATEGORY_PRESETS)
    return jsonify(data)


@api.post("/admin/media")
def admin_media_upload():
    user, error_response = require_admin()
    if error_response:
        return error_response
    migrate_admin_media_to_shared()
    return save_product_media_upload(*admin_media_parts(), preset_keys=ADMIN_MEDIA_CATEGORY_PRESETS)


@api.delete("/admin/media")
def admin_media_delete():
    user, error_response = require_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    migrate_admin_media_to_shared()
    return delete_product_media_upload(payload.get("storageKey") or payload.get("key") or payload.get("url") or payload.get("mediaUrl"), *admin_media_parts())


@api.patch("/admin/media")
def admin_media_update():
    user, error_response = require_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    migrate_admin_media_to_shared()
    return move_product_media_upload(
        payload.get("storageKey") or payload.get("key") or payload.get("url") or payload.get("mediaUrl"),
        payload.get("category") or payload.get("categoryId") or payload.get("category_id") or "",
        *admin_media_parts(),
        preset_keys=ADMIN_MEDIA_CATEGORY_PRESETS,
        include_shared_refs=True,
        target_name=payload.get("name") or payload.get("filename") or payload.get("fileName"),
    )


@api.post("/admin/media/categories")
def admin_media_category_create():
    user, error_response = require_admin()
    if error_response:
        return error_response
    migrate_admin_media_to_shared()
    return create_product_media_category(*admin_media_parts(), preset_keys=ADMIN_MEDIA_CATEGORY_PRESETS)


@api.delete("/admin/media/categories")
def admin_media_category_delete():
    user, error_response = require_admin()
    if error_response:
        return error_response
    migrate_admin_media_to_shared()
    return delete_product_media_category(*admin_media_parts(), preset_keys=ADMIN_MEDIA_CATEGORY_PRESETS)


@api.get("/admin/contacts")
def admin_contacts():
    _, error_response = require_admin()
    if error_response:
        return error_response
    rows = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return jsonify({"contacts": [row.to_dict() for row in rows]})
