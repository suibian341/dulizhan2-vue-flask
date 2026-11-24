import io
import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, unquote, urlparse


ALIYUN_PROVIDER_ALIASES = {"aliyun", "aliyun_oss", "oss"}
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}


@dataclass
class MediaUploadPayload:
    data: bytes
    content_type: str
    optimized: bool
    original_size: int
    stored_size: int


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name, default, minimum=None, maximum=None):
    try:
        value = int(os.getenv(name, default))
    except (TypeError, ValueError):
        value = default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value


def media_storage_provider():
    provider = os.getenv("MEDIA_STORAGE_PROVIDER", "local").strip().lower().replace("-", "_")
    return "aliyun_oss" if provider in ALIYUN_PROVIDER_ALIASES else "local"


def aliyun_oss_settings():
    return {
        "access_key_id": os.getenv("ALIYUN_OSS_ACCESS_KEY_ID", "").strip(),
        "access_key_secret": os.getenv("ALIYUN_OSS_ACCESS_KEY_SECRET", "").strip(),
        "bucket": os.getenv("ALIYUN_OSS_BUCKET", os.getenv("ALIYUN_OSS_BUCKET_NAME", "")).strip(),
        "endpoint": os.getenv("ALIYUN_OSS_ENDPOINT", "").strip().removeprefix("https://").removeprefix("http://"),
    }


def aliyun_oss_enabled():
    if media_storage_provider() != "aliyun_oss":
        return False
    settings = aliyun_oss_settings()
    return all(settings.values())


def media_public_base_url():
    configured = (
        os.getenv("MEDIA_PUBLIC_BASE_URL")
        or os.getenv("ALIYUN_OSS_PUBLIC_BASE_URL")
        or os.getenv("OSS_PUBLIC_BASE_URL")
        or ""
    ).strip().rstrip("/")
    if configured:
        return configured
    settings = aliyun_oss_settings()
    if settings["bucket"] and settings["endpoint"]:
        return f"https://{settings['bucket']}.{settings['endpoint']}".rstrip("/")
    return ""


def local_media_url(key):
    return f"/api/uploads/{key}"


def media_public_url(key):
    normalized = normalize_media_key(key)
    if aliyun_oss_enabled():
        base_url = media_public_base_url()
        if base_url:
            return f"{base_url}/{quote(normalized, safe='/~')}"
    return local_media_url(normalized)


def media_variant_url(value, width=480, quality=78):
    text = str(value or "").strip()
    if not text or media_storage_provider() != "aliyun_oss":
        return text

    base_url = media_public_base_url()
    parsed = urlparse(text)
    base = urlparse(base_url)
    if not base.netloc or parsed.netloc != base.netloc:
        return text
    if Path(parsed.path).suffix.lower() in {".gif", ".svg"}:
        return text
    if "x-oss-process=" in parsed.query:
        return text

    safe_width = env_int("MEDIA_THUMBNAIL_MAX_WIDTH", width, minimum=64, maximum=2400)
    safe_quality = env_int("MEDIA_THUMBNAIL_QUALITY", quality, minimum=50, maximum=95)
    process = f"x-oss-process=image/resize,w_{safe_width}/quality,q_{safe_quality}/format,webp"
    separator = "&" if parsed.query else "?"
    return f"{text}{separator}{process}"


def media_url_candidates(key):
    normalized = normalize_media_key(key)
    candidates = {local_media_url(normalized), media_public_url(normalized)}
    base_url = media_public_base_url()
    if base_url:
        candidates.add(f"{base_url}/{quote(normalized, safe='/~')}")
    return {item for item in candidates if item}


def normalize_media_key(value):
    text = str(value or "").strip()
    if not text:
        return ""
    if text.startswith(("http://", "https://")):
        parsed = urlparse(text)
        text = parsed.path.lstrip("/")
        base_url = media_public_base_url()
        if base_url:
            base_path = urlparse(base_url).path.strip("/")
            if base_path and text.startswith(f"{base_path}/"):
                text = text[len(base_path) + 1 :]
    if text.startswith("/api/uploads/"):
        text = text.removeprefix("/api/uploads/")
    elif text.startswith("api/uploads/"):
        text = text.removeprefix("api/uploads/")
    text = unquote(text).replace("\\", "/")
    parts = [part for part in text.split("/") if part and part not in {".", ".."}]
    return "/".join(parts)


def content_type_for_key(key):
    content_type, _ = mimetypes.guess_type(key)
    return content_type or "application/octet-stream"


def optimize_image_bytes(data, filename):
    ext = Path(filename or "").suffix.lower().lstrip(".")
    if ext not in IMAGE_EXTENSIONS or ext == "gif" or not env_bool("MEDIA_IMAGE_OPTIMIZE", True):
        return MediaUploadPayload(data, content_type_for_key(filename), False, len(data), len(data))

    try:
        from PIL import Image, ImageOps
    except ImportError:
        return MediaUploadPayload(data, content_type_for_key(filename), False, len(data), len(data))

    try:
        image = Image.open(io.BytesIO(data))
        if getattr(image, "is_animated", False):
            return MediaUploadPayload(data, content_type_for_key(filename), False, len(data), len(data))

        image = ImageOps.exif_transpose(image)
        max_side = env_int("MEDIA_IMAGE_MAX_SIDE", 1920, minimum=320, maximum=6000)
        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
        if max(image.size) > max_side:
            image.thumbnail((max_side, max_side), resample)

        output = io.BytesIO()
        if ext in {"jpg", "jpeg"}:
            if image.mode not in {"RGB", "L"}:
                image = image.convert("RGB")
            quality = env_int("MEDIA_IMAGE_JPEG_QUALITY", 82, minimum=50, maximum=95)
            image.save(output, format="JPEG", quality=quality, optimize=True, progressive=True)
            content_type = "image/jpeg"
        elif ext == "png":
            image.save(output, format="PNG", optimize=True, compress_level=9)
            content_type = "image/png"
        elif ext == "webp":
            quality = env_int("MEDIA_IMAGE_WEBP_QUALITY", 82, minimum=50, maximum=95)
            if image.mode not in {"RGB", "RGBA"}:
                image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            image.save(output, format="WEBP", quality=quality, method=6)
            content_type = "image/webp"
        else:
            return MediaUploadPayload(data, content_type_for_key(filename), False, len(data), len(data))

        optimized = output.getvalue()
        if optimized and len(optimized) < len(data):
            return MediaUploadPayload(optimized, content_type, True, len(data), len(optimized))
    except Exception:
        return MediaUploadPayload(data, content_type_for_key(filename), False, len(data), len(data))

    return MediaUploadPayload(data, content_type_for_key(filename), False, len(data), len(data))


def prepare_media_upload(file_storage, filename):
    data = file_storage.read()
    try:
        file_storage.seek(0)
    except (AttributeError, OSError):
        pass
    return optimize_image_bytes(data, filename)


def aliyun_oss_bucket():
    settings = aliyun_oss_settings()
    missing = [name for name, value in settings.items() if not value]
    if missing:
        raise RuntimeError(f"Aliyun OSS configuration is incomplete: {', '.join(missing)}")
    try:
        import oss2
    except ImportError as exc:
        raise RuntimeError("Python package oss2 is not installed") from exc

    auth = oss2.Auth(settings["access_key_id"], settings["access_key_secret"])
    endpoint = f"https://{settings['endpoint']}"
    return oss2.Bucket(auth, endpoint, settings["bucket"])


def upload_remote_media(key, data, content_type=None):
    if media_storage_provider() != "aliyun_oss":
        return False
    if not aliyun_oss_enabled():
        aliyun_oss_bucket()
    headers = {
        "Content-Type": content_type or content_type_for_key(key),
        "Cache-Control": "public, max-age=31536000, immutable",
    }
    aliyun_oss_bucket().put_object(normalize_media_key(key), data, headers=headers)
    return True


def delete_remote_media(key):
    if media_storage_provider() != "aliyun_oss":
        return False
    if not aliyun_oss_enabled():
        aliyun_oss_bucket()
    normalized = normalize_media_key(key)
    if not normalized:
        return False
    aliyun_oss_bucket().delete_object(normalized)
    return True
