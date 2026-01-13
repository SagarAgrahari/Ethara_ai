# HRMS Lite (Django)

Lightweight Human Resource Management System (HRMS Lite) built with Django and Django REST Framework.

Quick start

1. Create a virtual environment and activate it.

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Apply migrations and run server

```bash
python manage.py migrate
python manage.py runserver
```

3. Open http://127.0.0.1:8000/ to view the app.

Notes
- Database: SQLite (configured in settings).
- APIs: REST endpoints under `/api/`.
