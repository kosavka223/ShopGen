from __future__ import annotations

import json
from typing import Any, Dict, List

from models import db, GenerationHistory


def save_generation(category: str, input_dict: Dict[str, Any], generated_text: str) -> bool:
    """Сохраняет генерацию. Возвращает True/False."""
    from datetime import datetime

    row = GenerationHistory(
    category=category,
    input_data=json.dumps(input_dict, ensure_ascii=False),
    generated_text=generated_text,
    created_at=datetime.utcnow(),  # явно
    )
    try:
        row = GenerationHistory(
            category=category,
            input_data=json.dumps(input_dict, ensure_ascii=False),
            generated_text=generated_text,
        )
        db.session.add(row)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


def get_recent_history(limit: int = 50) -> List[dict]:
    rows = (
        GenerationHistory.query.order_by(GenerationHistory.id.desc()).limit(limit).all()
    )
    return [r.to_dict() for r in rows]


def get_history_by_category(category: str, limit: int = 50) -> List[dict]:
    rows = (
        GenerationHistory.query.filter_by(category=category)
        .order_by(GenerationHistory.id.desc())
        .limit(limit)
        .all()
    )
    return [r.to_dict() for r in rows]
