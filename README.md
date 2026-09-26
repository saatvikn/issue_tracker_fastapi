# Issue Tracker API

A small FastAPI project for learning how to build a REST API. It lets you create, list, view, update, and delete issues. Issues are stored in a local JSON file (no database setup).

## What it covers

- API routes and HTTP status codes
- Request validation and response models with Pydantic
- Enums for issue priority and status
- JSON file persistence
- Middleware that adds an `X-Process-Time` response header
- Automatic interactive API documentation from FastAPI

## Requirements

- Python 3.10 or newer
- `pip`

## Run locally

From the project root, create a virtual environment and install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the development server:

```powershell
python -m uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` to try the endpoints in Swagger UI, or `http://127.0.0.1:8000/redoc` for ReDoc.

## API endpoints

All issue routes start with `/api/v1/issues`.

| Method | Path | Description | Success status |
| --- | --- | --- | --- |
| GET | `/api/v1/issues/` | List all issues | 200 |
| GET | `/api/v1/issues/{issue_id}` | Get one issue | 200 |
| POST | `/api/v1/issues/` | Create an issue | 201 |
| PUT | `/api/v1/issues/{issue_id}` | Update supplied fields | 200 |
| DELETE | `/api/v1/issues/{issue_id}` | Delete an issue | 204 |

Requests for an unknown issue ID return `404`.

### Issue fields

| Field | Create | Update | Values or validation |
| --- | --- | --- | --- |
| `title` | Required | Optional | 3 to 100 characters on creation; up to 100 on update |
| `description` | Required | Optional | 5 to 1000 characters on creation; up to 1000 on update |
| `priority` | Optional | Optional | `low`, `medium`, `high`; defaults to `medium` |
| `status` | Set by server | Optional | `open`, `in_progress`, `closed`; new issues start as `open` |
| `id` | Set by server | N/A | UUID string |

### Example requests (PowerShell)

Create an issue:

```powershell
$issue = Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/api/v1/issues/ `
  -ContentType 'application/json' `
  -Body '{"title":"Fix login error","description":"Login fails with valid credentials","priority":"high"}'
$issue
```

List issues and update the issue you created:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/issues/

Invoke-RestMethod -Method Put `
  -Uri "http://127.0.0.1:8000/api/v1/issues/$($issue.id)" `
  -ContentType 'application/json' `
  -Body '{"status":"in_progress"}'
```

## Storage and project structure

The app creates `data/issues.json` when the first issue is saved. The file is relative to the directory where you start the server and is ignored by Git. This simple storage is intended for learning and local use.

```text
main.py                  FastAPI app, CORS, and middleware setup
app/routes/issues.py     Issue CRUD endpoints
app/schemas.py           Request and response models
app/storage.py           JSON file reads and writes
app/middleware/timer.py  Response timing header
requirements.txt         Python dependencies
```

The app currently allows requests from any CORS origin and does not implement authentication or concurrent write protection.
