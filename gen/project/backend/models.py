from __future__ import annotations

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class GenerationHistory(db.Model):
    __tablename__ = "generation_history"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(64), nullable=False, index=True)
    input_data = db.Column(db.Text, nullable=False)
    generated_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "input_data": self.input_data,
            "generated_text": self.generated_text,
            "created_at": self.created_at.isoformat() + "Z",
        }
