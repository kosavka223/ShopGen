import json
import random
import re
from pathlib import Path
from typing import Any, Dict, Tuple, Union


class SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return ""


def _load_json(path: Union[str, Path]) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    text = re.sub(r"\.\s*\.", ".", text)
    text = re.sub(r"\s*,\s*,", ",", text)
    text = re.sub(r"\s+—\s*\.", ".", text)
    text = re.sub(r"\s+\.", ".", text)
    return text.strip()


def _fmt(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, bool):
        return "да" if x else "нет"
    if isinstance(x, int):
        return str(x)
    if isinstance(x, float):
        s = f"{x:.2f}".rstrip("0").rstrip(".")
        return s
    return str(x)


def _as_num(x: Any) -> Union[int, float, None]:
    if isinstance(x, (int, float)):
        return x
    if isinstance(x, str):
        s = x.strip().lower().replace(",", ".")
        s = s.replace("gb", "").replace("гб", "")
        s = s.replace("mhz", "").replace("мгц", "")
        try:
            return float(s) if "." in s else int(s)
        except Exception:
            return None
    return None


def _title_from(a: Dict[str, Any], keys) -> str:
    parts = []
    for k in keys:
        v = a.get(k)
        if isinstance(v, str) and v.strip():
            parts.append(v.strip())
    return " ".join(parts).strip()


def _normalize_category(raw_cat: str) -> str:
    cat_map = {
        "smartphone": "smartphone",
        "смартфон": "smartphone",
        "телефон": "smartphone",
        "sneakers": "sneakers",
        "кроссовки": "sneakers",
        "кеды": "sneakers",
        "gpu": "gpu",
        "видеокарта": "gpu",
        "video card": "gpu",
        "videocard": "gpu",
    }
    return cat_map.get(raw_cat.lower(), raw_cat)


def _purpose_phrase(v: Any) -> str:
    if not isinstance(v, str):
        return ""
    s = v.strip()
    if not s:
        return ""

    low = s.lower()

    direct_map = {
        "город": "для города",
        "города": "для города",
        "бег": "для бега",
        "бега": "для бега",
        "тренировки": "для тренировок",
        "тренировок": "для тренировок",
        "спорт": "для спорта",
        "спорта": "для спорта",
        "повседневные": "для повседневной носки",
        "повседневная носка": "для повседневной носки",
        "повседневной носки": "для повседневной носки",
        "зал": "для тренировок",
    }

    if low.startswith("для "):
        phrase = s
    elif low in direct_map:
        phrase = direct_map[low]
    else:
        phrase = f"для {s}"

    if not phrase.endswith("."):
        phrase += "."

    return phrase + " "


def _platform_phrase(v: Any) -> str:
    if not isinstance(v, str):
        return ""
    s = v.strip().lower()
    if not s:
        return ""
    if s in {"pc", "пк", "desktop"}:
        return "Версия для ПК. "
    if s in {"laptop", "ноутбук", "notebook"}:
        return "Версия для ноутбука. "
    return f"Версия: {v.strip()}. "


def _gpu_is_old(attrs: Dict[str, Any]) -> bool:
    manufacturer = str(attrs.get("manufacturer", "")).strip().lower()
    version = str(attrs.get("version", "")).strip().lower()

    text = f"{manufacturer} {version}"

    old_markers = [
        "gtx 4", "gtx 5", "gtx 6", "gtx 7", "gtx 8", "gtx 9",
        "gt ", "gts ", "9800", "8800", "hd 4", "hd 5", "hd 6", "hd 7",
        "r7 ", "r9 2", "r9 3", "rx 4", "rx 5", "quadro 2000", "quadro 4000"
    ]
    mid_old_markers = [
        "gtx 10", "gtx 1050", "gtx 1060", "gtx 1070", "gtx 1080",
        "rx 560", "rx 570", "rx 580"
    ]

    for m in old_markers:
        if m in text:
            return True
    for m in mid_old_markers:
        if m in text:
            return True

    return False


def _build_sneakers(attrs: Dict[str, Any], phrases: dict, rng: random.Random) -> Dict[str, str]:
    out: Dict[str, str] = {}

    title = _title_from(attrs, ["brand", "model"]) or "Кроссовки"
    out["title"] = title
    out["purpose_phrase"] = _purpose_phrase(attrs.get("purpose"))

    size = _as_num(attrs.get("size_eu"))
    out["size_phrase"] = f"Размер {_fmt(size)} EU. " if isinstance(size, (int, float)) and size > 0 else ""

    material = attrs.get("material_upper")
    ms = material.strip() if isinstance(material, str) else ""
    out["material_phrase"] = f"Верх из материала «{ms}» обеспечивает комфорт. " if ms else ""

    season = attrs.get("season")
    ss = season.strip() if isinstance(season, str) else ""
    out["season_phrase"] = f"Подойдут на сезон: {ss}. " if ss else ""

    color = attrs.get("color")
    cs = color.strip() if isinstance(color, str) else ""
    out["color_phrase"] = f"Цвет: {cs}. " if cs else ""

    comfort_pool = phrases.get("sneakers_comfort", [])
    out["comfort_phrase"] = (rng.choice(comfort_pool).strip() + ". ") if comfort_pool else ""

    feat = attrs.get("key_feature")
    fs = feat.strip() if isinstance(feat, str) else ""
    out["feature_phrase"] = f"Особенность — {fs}. " if fs else ""

    return out


def _build_smartphone(attrs: Dict[str, Any], phrases: dict, rng: random.Random) -> Dict[str, str]:
    out: Dict[str, str] = {}

    out["title"] = _title_from(attrs, ["brand", "model"]) or "Смартфон"

    use_cases = phrases.get("use_case_smartphone", [])
    use_case = rng.choice(use_cases).strip() if use_cases else ""
    out["use_case_phrase"] = f" — {use_case}. " if use_case else ". "

    screen = _as_num(attrs.get("screen_size_in"))
    out["screen_phrase"] = f"Экран {_fmt(screen)} дюйма удобен для контента. " if isinstance(screen, (int, float)) and screen > 0 else ""

    ram = _as_num(attrs.get("ram_gb"))
    storage = _as_num(attrs.get("storage_gb"))
    if isinstance(ram, (int, float)) and ram > 0 and isinstance(storage, (int, float)) and storage > 0:
        out["perf_phrase"] = f"{_fmt(ram)} ГБ RAM и {_fmt(storage)} ГБ памяти подходят для приложений и файлов. "
    elif isinstance(storage, (int, float)) and storage > 0:
        out["perf_phrase"] = f"{_fmt(storage)} ГБ памяти хватит для фото, файлов и приложений. "
    elif isinstance(ram, (int, float)) and ram > 0:
        out["perf_phrase"] = f"{_fmt(ram)} ГБ RAM помогают в многозадачности. "
    else:
        out["perf_phrase"] = ""

    battery = _as_num(attrs.get("battery_mah"))
    out["battery_phrase"] = f"Аккумулятор {_fmt(battery)} мА·ч помогает дольше оставаться на связи. " if isinstance(battery, (int, float)) and battery > 0 else ""

    camera = _as_num(attrs.get("camera_mp"))
    out["camera_phrase"] = f"Камера {_fmt(camera)} Мп пригодится для фото и видео. " if isinstance(camera, (int, float)) and camera > 0 else ""

    extra_pool = phrases.get("smartphone_extra", [])
    out["extra_phrase"] = (rng.choice(extra_pool).strip() + ". ") if extra_pool else ""

    feat = attrs.get("key_feature")
    fs = feat.strip() if isinstance(feat, str) else ""
    out["feature_phrase"] = f"Дополнительное преимущество — {fs}. " if fs else ""

    return out


def _build_gpu(attrs: Dict[str, Any], phrases: dict, rng: random.Random) -> Dict[str, str]:
    out: Dict[str, str] = {}

    out["title"] = _title_from(attrs, ["manufacturer", "version"]) or "Видеокарта"
    out["platform_phrase"] = _platform_phrase(attrs.get("platform"))

    cooling = attrs.get("cooling")
    cs = cooling.strip() if isinstance(cooling, str) else ""
    out["cooling_phrase"] = f"Охлаждение: {cs}. " if cs else ""

    mem = _as_num(attrs.get("memory_gb"))
    out["memory_phrase"] = f"Память: {_fmt(mem)} ГБ. " if isinstance(mem, (int, float)) and mem > 0 else ""

    clock = _as_num(attrs.get("clock_mhz"))
    out["clock_phrase"] = f"Частота: {_fmt(clock)} МГц. " if isinstance(clock, (int, float)) and clock > 0 else ""

    old_gpu = _gpu_is_old(attrs)

    if old_gpu:
        values = phrases.get("gpu_use_case_old", [])
        feats = phrases.get("gpu_features_old", [])
        adjs = phrases.get("adj_gpu_old", [])
    else:
        values = phrases.get("gpu_use_case", [])
        feats = phrases.get("gpu_features", [])
        adjs = phrases.get("adj_gpu_modern", [])

    out["gpu_use_case_phrase"] = (rng.choice(values).strip() + ". ") if values else ""
    out["gpu_feature_phrase"] = (rng.choice(feats).strip() + ". ") if feats else ""
    out["gpu_adj"] = rng.choice(adjs).strip() if adjs else ""

    feat = attrs.get("key_feature")
    fs = feat.strip() if isinstance(feat, str) else ""
    out["feature_phrase"] = f"Особенность — {fs}. " if fs else ""

    return out


SUPPORTED_CATEGORIES = {"smartphone", "sneakers", "gpu"}


def load_assets(base_dir: Union[str, Path, None] = None) -> Tuple[dict, dict]:
    if base_dir is None:
        base_dir = Path(__file__).parent
    base_dir = Path(base_dir)
    templates = _load_json(base_dir / "templates" / "templates.json")
    phrases = _load_json(base_dir / "templates" / "phrases.json")
    return templates, phrases


def normalize_input(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("payload должен быть объектом JSON")

    raw_cat = (payload.get("category") or "").strip()
    if not raw_cat:
        raise ValueError("Не указана category")

    category = _normalize_category(raw_cat)

    if category not in SUPPORTED_CATEGORIES:
        raise ValueError("Unknown category: " + raw_cat)

    if isinstance(payload.get("attributes"), dict):
        attrs = payload["attributes"] or {}
    else:
        attrs = {k: v for k, v in payload.items() if k not in {"category", "seed"}}

    key_map = {
        "ram": "ram_gb",
        "rom": "storage_gb",
        "storage": "storage_gb",
        "screen": "screen_size_in",
        "battery": "battery_mah",
        "camera": "camera_mp",
        "maker": "manufacturer",
        "brand": "manufacturer",
        "model": "version",
        "gpu_model": "version",
        "mem": "memory_gb",
        "vram": "memory_gb",
        "memory": "memory_gb",
        "clock": "clock_mhz",
        "freq": "clock_mhz",
        "frequency": "clock_mhz",
        "type": "platform",
    }
    attrs = {key_map.get(k, k): v for k, v in attrs.items()}

    for k in ["ram_gb", "storage_gb", "screen_size_in", "battery_mah", "camera_mp", "size_eu", "memory_gb", "clock_mhz"]:
        if k in attrs:
            n = _as_num(attrs[k])
            if n is not None:
                attrs[k] = n

    return {"category": category, "attributes": attrs}


def generate_description(item: dict, templates: dict, phrases: dict, seed: Union[int, None] = None) -> str:
    rng = random.Random(seed)

    category = (item.get("category") or "").strip()
    attrs: Dict[str, Any] = item.get("attributes", {}) or {}

    if category not in templates:
        raise ValueError("Unknown category: " + category)

    template = rng.choice(templates[category])

    values: Dict[str, Any] = {}
    for k, v in attrs.items():
        values[k] = _fmt(v)

    if category == "gpu":
        gpu_block = _build_gpu(attrs, phrases, rng)
        values.update(gpu_block)
        values["adj"] = gpu_block.get("gpu_adj", "")
    elif category == "smartphone":
        values["adj"] = (rng.choice(phrases.get("adj", [])).strip() if phrases.get("adj") else "")
        values.update(_build_smartphone(attrs, phrases, rng))
    elif category == "sneakers":
        values["adj"] = (rng.choice(phrases.get("adj", [])).strip() if phrases.get("adj") else "")
        values.update(_build_sneakers(attrs, phrases, rng))

    cta_list = phrases.get("cta", [])
    values["cta"] = (rng.choice(cta_list).strip() if cta_list else "")

    text = template.format_map(SafeDict(values))
    return _clean_text(text)