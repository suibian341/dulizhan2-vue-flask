import json
from pathlib import Path


LOCALES = ["en", "zh", "ja", "ko", "fr", "de", "es", "ar"]
MESSAGES_DIR = Path(__file__).resolve().parents[2] / "frontend" / "src" / "messages"


def flatten_object(data, prefix=""):
    result = {}
    for key, value in (data or {}).items():
        full_key = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            result.update(flatten_object(value, full_key))
        else:
            result[full_key] = "" if value is None else str(value)
    return result


def unflatten_object(flat):
    result = {}
    for key, value in (flat or {}).items():
        current = result
        parts = key.split(".")
        for part in parts[:-1]:
            next_value = current.get(part)
            if not isinstance(next_value, dict):
                next_value = {}
                current[part] = next_value
            current = next_value
        current[parts[-1]] = value
    return result


def read_locale_messages(locale):
    if locale not in LOCALES:
        return {}
    file_path = MESSAGES_DIR / f"{locale}.json"
    try:
        return flatten_object(json.loads(file_path.read_text(encoding="utf-8")))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_admin_i18n_data(selected_locale="zh"):
    stats_map = {locale: read_locale_messages(locale) for locale in LOCALES}
    all_keys = sorted((stats_map.get("en") or {}).keys())
    locales = []
    for locale in LOCALES:
        total = len(all_keys)
        filled = sum(1 for key in all_keys if stats_map.get(locale, {}).get(key))
        locales.append(
            {
                "code": locale,
                "total": total,
                "filled": filled,
                "progress": round((filled / total) * 100) if total else 0,
            }
        )

    selected = selected_locale if selected_locale in LOCALES else "zh"
    initial_locales = ["en"]
    if selected != "en":
        initial_locales.append(selected)

    return {
        "locales": locales,
        "keys": all_keys,
        "translations": {locale: stats_map.get(locale, {}) for locale in initial_locales},
    }


def update_admin_locale_messages(locale, updates):
    if locale not in LOCALES or locale == "en":
        raise ValueError("Invalid locale")
    MESSAGES_DIR.mkdir(parents=True, exist_ok=True)
    existing = read_locale_messages(locale)
    existing.update({str(key): "" if value is None else str(value) for key, value in (updates or {}).items()})
    file_path = MESSAGES_DIR / f"{locale}.json"
    file_path.write_text(
        json.dumps(unflatten_object(existing), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
