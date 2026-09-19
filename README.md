# AI-Enhanced Task Manager API

A role-based task management REST API built with Django REST Framework, JWT
authentication, and Groq-powered AI task planning assistance.

## Features

- **JWT authentication** (login, refresh, register) via `djangorestframework-simplejwt`
- **Role-based access control (RBAC)**: Admins manage everything; Members only
  see/edit tasks assigned to them
- **Projects & Tasks** with status, priority, due dates, and assignment
- **Filtering, search, and pagination** on the tasks list (`?status=`, `?priority=`,
  `?search=`, `?ordering=`)
- **AI task planning**: `POST /api/tasks/{id}/ai-suggest/` calls Groq's LLaMA
  model to suggest a priority level and subtasks for a given task
- **Auto-generated API docs** via drf-spectacular / Swagger UI
- **9 passing pytest tests** covering auth and RBAC enforcement

## Project structure

```
taskmanager/          # project settings, root urls
accounts/              # custom User model (with role field), register/login
tasks/                 # Project & Task models, viewsets, permissions, AI util
  ai_utils.py           # Groq API wrapper
  permissions.py         # RBAC permission classes
  tests/test_tasks.py    # pytest suite
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env            # then fill in SECRET_KEY and GROQ_API_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Get a Groq API key for free at https://console.groq.com — needed only for the
`/ai-suggest/` endpoint; everything else works without it.

## Running tests

```bash
pytest -v
```

## API quick reference

| Endpoint | Method | Who |
|---|---|---|
| `/api/auth/register/` | POST | Anyone |
| `/api/auth/login/` | POST | Anyone |
| `/api/auth/login/refresh/` | POST | Anyone (with refresh token) |
| `/api/projects/` | GET, POST | Authenticated (POST = Admin only) |
| `/api/tasks/` | GET, POST | Authenticated (scoped by role) |
| `/api/tasks/{id}/` | GET, PATCH, DELETE | Owner (assignee) or Admin |
| `/api/tasks/{id}/ai-suggest/` | POST | Owner (assignee) or Admin |
| `/api/docs/` | GET | Swagger UI |

### Example: login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}'
```

Use the returned `access` token as `Authorization: Bearer <token>` on all
other requests.

### Example: AI suggestion

```bash
curl -X POST http://localhost:8000/api/tasks/1/ai-suggest/ \
  -H "Authorization: Bearer <access_token>"
```

Returns something like:
```json
{"priority": "HIGH", "subtasks": ["Wireframe layout", "Get design approval", "Implement in code"]}
```

## Deployment

Works on Render/Railway the same way as any Django app: set `DEBUG=False`,
add your GROQ_API_KEY and a real SECRET_KEY as environment variables, point
`ALLOWED_HOSTS` at your domain, and swap SQLite for PostgreSQL if you want
persistence across deploys.
