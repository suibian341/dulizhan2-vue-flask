import copy
import hashlib
import json
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATE_PATH = BASE_DIR / "product_spec_template.json"
SAVED_TEMPLATE_PATH = Path(os.getenv("SPEC_TEMPLATE_PATH") or BASE_DIR.parent / "uploads" / "product_spec_template.local.json")


def _read_json(path):
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, list) else None


def _localized_value(value, locale, fallback=""):
    if isinstance(value, dict):
        return value.get(locale) or value.get("en") or value.get("zh") or fallback
    return value or fallback


def _is_customization_spec(row):
    note = row.get("note") or row.get("notes") or row.get("remark") or row.get("section") or ""
    note_en = row.get("noteEn") or _localized_value(note, "en")
    note_zh = row.get("noteZh") or _localized_value(note, "zh", note_en)
    return str(note_en).strip().lower() == "customization" or str(note_zh).strip() == "\u5b9a\u5236\u9009\u9879"


def _localized_source(row, *keys):
    for key in keys:
        value = row.get(key)
        if value:
            return value
    return ""


def _localized_pair(row, source_key, en_key=None, zh_key=None):
    source = row.get(source_key) or ""
    en_value = row.get(en_key) if en_key else None
    zh_value = row.get(zh_key) if zh_key else None
    en_text = en_value or _localized_value(source, "en")
    zh_text = zh_value or _localized_value(source, "zh", en_text)
    return str(en_text or "").strip(), str(zh_text or "").strip()


def _spec_key(row):
    label_en, label_zh = _localized_pair(row, "label", "labelEn", "labelZh")
    if not (label_en or label_zh):
        label_en, label_zh = _localized_pair(row, "name", None, None)
    if not (label_en or label_zh):
        label_en, label_zh = _localized_pair(row, "key", None, None)
    note_source = _localized_source(row, "note", "notes", "remark", "section")
    note_en = row.get("noteEn") or _localized_value(note_source, "en")
    note_zh = row.get("noteZh") or _localized_value(note_source, "zh", note_en)
    return "::".join(
        [
            str(label_en or "").strip().lower(),
            str(label_zh or "").strip().lower(),
            str(note_en or "").strip().lower(),
            str(note_zh or "").strip().lower(),
        ]
    )


def _stable_spec_id(row):
    source = _spec_key(row)
    digest = hashlib.sha1(source.encode("utf-8")).hexdigest()[:16] if source else "blank"
    return f"spec-{digest}"


def _with_spec_id(row):
    next_row = copy.deepcopy(row)
    next_row["id"] = str(next_row.get("id") or next_row.get("templateId") or _stable_spec_id(next_row))
    return next_row


def _spec_value(row, locale):
    if row.get("valueEn") or row.get("valueZh"):
        return str(row.get("valueEn") if locale == "en" else row.get("valueZh") or row.get("valueEn") or "").strip()
    value = row.get("value") or row.get("details") or row.get("content") or ""
    return str(_localized_value(value, locale)).strip()


def _merge_value(template_row, saved_row):
    if not saved_row:
        return template_row
    saved_en = _spec_value(saved_row, "en")
    saved_zh = _spec_value(saved_row, "zh")
    template_en = _spec_value(template_row, "en")
    template_zh = _spec_value(template_row, "zh")
    next_row = copy.deepcopy(template_row)
    next_row["value"] = {
        "en": saved_en or template_en,
        "zh": saved_zh or saved_en or template_zh,
    }
    return next_row


def without_customization_specs(rows):
    return [_with_spec_id(row) for row in (rows or []) if isinstance(row, dict) and not _is_customization_spec(row)]


def template_rows(rows):
    cleaned_rows = []
    for row in without_customization_specs(rows):
        next_row = copy.deepcopy(row)
        for key in ("value", "valueEn", "valueZh", "details", "content"):
            next_row.pop(key, None)
        cleaned_rows.append(next_row)
    return cleaned_rows


def merge_specs_with_template(product_specs, template, previous_template=None):
    rows = without_customization_specs(product_specs if isinstance(product_specs, list) else [])
    template_spec_rows = template_rows(template if isinstance(template, list) else [])
    previous_rows = template_rows(previous_template if isinstance(previous_template, list) else [])

    saved_by_id = {str(row.get("id")): row for row in rows if row.get("id")}
    saved_by_key = {}
    for row in rows:
        key = _spec_key(row)
        if key:
            saved_by_key[key] = row

    previous_by_id = {str(row.get("id")): row for row in previous_rows if row.get("id")}

    merged_rows = []
    for template_row in template_spec_rows:
        template_id = str(template_row.get("id") or "")
        saved_row = saved_by_id.get(template_id)
        if not saved_row and template_id in previous_by_id:
            saved_row = saved_by_key.get(_spec_key(previous_by_id[template_id]))
        if not saved_row:
            saved_row = saved_by_key.get(_spec_key(template_row))
        merged_rows.append(_merge_value(template_row, saved_row))
    return merged_rows


def default_spec_template():
    return copy.deepcopy(template_rows(_read_json(DEFAULT_TEMPLATE_PATH) or []))


def load_spec_template():
    return copy.deepcopy(template_rows(_read_json(SAVED_TEMPLATE_PATH) or _read_json(DEFAULT_TEMPLATE_PATH) or []))


def save_spec_template(template):
    rows = template_rows(template if isinstance(template, list) else [])
    SAVED_TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SAVED_TEMPLATE_PATH.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return copy.deepcopy(rows)
