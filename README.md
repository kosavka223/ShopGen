# ShopGen

ShopGen — это веб-приложение для генерации карточек и текстовых описаний товаров по заданным параметрам.

Проект объединяет:
- веб-интерфейс для ввода параметров товара,
- Flask API для генерации описаний,
- SQLite-базу для хранения истории генераций,
- деплой на Render.

Сейчас проект поддерживает 3 категории товаров:
- смартфоны,
- кроссовки,
- видеокарты.

## Демо

Сайт: `https://c-site-project.onrender.com/`

## Что умеет проект

- генерировать описание товара по параметрам;
- работать через веб-интерфейс;
- работать через API;
- сохранять историю генераций в SQLite;
- фильтровать историю по категории;
- использовать seed для воспроизводимого результата;
- обрабатывать как один объект, так и список объектов для batch-генерации.

## Стек

- Python
- Flask
- Flask-CORS
- Flask-SQLAlchemy
- SQLite
- Gunicorn
- HTML / frontend_override

## Структура проекта

```texуйt
ShopGen/
├── app.py
├── database.py
├── generator_engine.py
├── models.py
├── requirements.txt
├── render-build.sh
├── render-start.sh
├── frontend_override/
│   └── index.html
└── templates/
    ├── templates.json
    └── phrases.json
