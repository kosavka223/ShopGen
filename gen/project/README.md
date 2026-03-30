# SHOP_GEN + API + сайт (локальная проверка)

Структура:
- `backend/` — Flask API + SQLite (история генераций)
- `frontend/` — статическая страница `index.html` с кнопкой «Сгенерировать»

## 1) Запуск backend

```bash
cd backend
python -m venv .venv
# Windows:
#   .venv\Scripts\activate
# macOS/Linux:
#   source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Проверка:
```bash
curl http://127.0.0.1:5000/ping
```

## 2) Запуск фронта (сайт)

Во **втором** терминале:

```bash
cd frontend
python -m http.server 8000
```

Открой в браузере:
- `http://127.0.0.1:8000/index.html`

## 3) Проверка, что “всё записывается”

1) На сайте нажми «Сгенерировать» (включен чекбокс “через API”).
2) Открой историю:
   - `http://127.0.0.1:5000/api/history`
3) Файл БД лежит тут:
   - `backend/instance/generations.db`

Дополнительно:
```bash
curl "http://127.0.0.1:5000/api/history?category=sneakers&limit=10"
```

## Формат входных данных

Рекомендуемый формат (как в текущем `index.html`):

```json
{
  "category": "sneakers",
  "attributes": {
    "brand": "Reebok",
    "model": "Royal",
    "purpose": "город"
  }
}
```

API также принимает старый “плоский” формат (частично), но лучше использовать `attributes`.
