from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

from models import db, GenerationHistory
from database import save_generation, get_recent_history, get_history_by_category
from generator_engine import load_assets, normalize_input, generate_description


def create_app() -> Flask:
    app = Flask(__name__)

    # CORS нужен, если фронт на другом порту (например 8000) вызывает API на 5000
    CORS(app)

    basedir = Path(__file__).resolve().parent
    instance_path = basedir / "instance"
    instance_path.mkdir(exist_ok=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{instance_path / 'generations.db'}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # assets (templates/phrases) загружаем один раз
    templates, phrases = load_assets(basedir)

    with app.app_context():
        db.create_all()

    @app.get("/ping")
    def ping():
        return jsonify({"status": "ok", "message": "Server is running"})

    @app.post("/api/generate")
    def api_generate():
        try:
            payload = request.get_json(force=True, silent=False)
            if payload is None:
                return jsonify({"success": False, "error": "Нет JSON в запросе"}), 400

            # seed может быть в body (для одного или для batch), либо query (?seed=123)
            seed_qs = request.args.get("seed")
            seed_body = payload.get("seed") if isinstance(payload, dict) else None
            seed_raw = seed_qs if seed_qs is not None else seed_body
            seed_base = int(seed_raw) if seed_raw not in (None, "") else None

            items = payload if isinstance(payload, list) else [payload]

            results = []
            for idx, it in enumerate(items):
                norm = normalize_input(it)

                # чтобы batch с одним seed не выдавал одинаковый текст
                seed = None if seed_base is None else (seed_base + idx)

                text = generate_description(norm, templates, phrases, seed=seed)
                saved = save_generation(
                    category=norm["category"], input_dict=norm, generated_text=text
                )
                results.append(
                    {
                        "category": norm["category"],
                        "description": text,
                        "saved_to_history": saved,
                    }
                )

            return jsonify(
                {
                    "success": True,
                    "count": len(results),
                    "results": results,
                }
            )

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.get("/api/history")
    def api_history():
        try:
            category = request.args.get("category")
            limit_raw = request.args.get("limit", "50")
            try:
                limit = max(1, min(200, int(limit_raw)))
            except Exception:
                limit = 50

            if category:
                history_list = get_history_by_category(category, limit=limit)
            else:
                history_list = get_recent_history(limit=limit)

            return jsonify(
                {
                    "success": True,
                    "count": len(history_list),
                    "history": history_list,
                }
            )
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.get("/api/history/<int:record_id>")
    def api_history_record(record_id: int):
        try:
            record = GenerationHistory.query.get(record_id)
            if not record:
                return (
                    jsonify({"success": False, "error": f"ID {record_id} не найден"}),
                    404,
                )
            return jsonify({"success": True, "record": record.to_dict()})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
