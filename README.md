# Issue Tracker API

A small FastAPI project for learning how to build a database-backed REST API. It lets you create, list, view, update, and delete issues. Issues are stored in PostgreSQL using SQLAlchemy 2.0, and Alembic manages changes to the database structure.

## What it covers

- API routes and HTTP status codes
- Request validation and response models with Pydantic
- Enums for issue priority and status
- PostgreSQL persistence using SQLAlchemy 2.0
- A database Session for each request
- Database migrations using Alembic
- Configuration through `.env` files
- Automated API tests using pytest and FastAPI's `TestClient`
- Middleware that adds an `X-Process-Time` response header
- Automatic interactive API documentation from FastAPI

## Requirements

- Python 3.12 (used for development and testing)
- `pip`
- PostgreSQL installed and running locally
- SQL Shell (`psql`) or another PostgreSQL client

## Run locally

From the project root, create a virtual environment and install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Create the databases

For a fresh setup, open SQL Shell (`psql`) and connect as the PostgreSQL administrator, usually `postgres`. Create an application login:

```sql
CREATE ROLE issue_tracker_user LOGIN;
```

Set its password using the psql command below, then enter and confirm the password when prompted:

```text
\password issue_tracker_user
```

Create separate development and test databases owned by that login:

```sql
CREATE DATABASE issue_tracker OWNER issue_tracker_user;
CREATE DATABASE issue_tracker_test OWNER issue_tracker_user;
```

These commands only need to be run once for a new local setup.

### Configure the connection

For a fresh setup, copy the example configuration to `.env` in the project root:

```powershell
Copy-Item -LiteralPath .env.example -Destination .env
```

Edit the copied file to configure your development database:

```ini
DATABASE_URL=postgresql+psycopg://issue_tracker_user:YOUR_URL_ENCODED_PASSWORD@localhost:5432/issue_tracker
```

Replace `YOUR_URL_ENCODED_PASSWORD` with the application login's password, URL-encoding special characters such as `@` as `%40` and `/` as `%2F`. Adjust the host or port if your PostgreSQL server uses different settings.

The URL specifies the database type (`postgresql`), Python driver (`psycopg`), login, password, server address, port, and database name. `app/database.py` loads `.env` and creates the SQLAlchemy Engine from this value. An existing `DATABASE_URL` environment variable takes precedence over `.env`.

For automated tests, also copy the example to `.env.test`:

```powershell
Copy-Item -LiteralPath .env.example -Destination .env.test
```

Edit its password and change the database name to `issue_tracker_test`:

```ini
DATABASE_URL=postgresql+psycopg://issue_tracker_user:YOUR_URL_ENCODED_PASSWORD@localhost:5432/issue_tracker_test
```

Both local configuration files are ignored by Git. `.env.example` contains placeholders and can be committed. Keep actual passwords out of source files and commits.

### Apply migrations and start the server

From the project root, apply the existing migrations to the development database:

```powershell
python -m alembic upgrade head
```

Then start the development server:

```powershell
python -m uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` to try the endpoints in Swagger UI, or `http://127.0.0.1:8000/redoc` for ReDoc.

## Run the tests

Tests use the separate `issue_tracker_test` PostgreSQL database. Before the first test run, apply the migrations to it:

```powershell
python -m dotenv -f .env.test run -- .\.venv\Scripts\python.exe -m alembic upgrade head
```

The `dotenv` command loads `.env.test` for the migration process. The explicit executable path selects the project's virtual environment on Windows. Repeat this command after adding new migrations so the test database stays up to date.

Run the suite from the project root:

```powershell
python -m pytest -v
```

`tests/conftest.py` loads `.env.test` before importing the application. Its client fixture checks that the database is named `issue_tracker_test`, then deletes all issue rows before and after each test. The test database should be dedicated to this suite.

The tests cover:

- Creating an issue and checking its response fields and defaults
- Rejecting invalid input with `422`
- Fetching the correct issue by ID
- Returning `404` for an unknown ID
- Updating an issue and fetching the saved changes
- Deleting an issue with `204` and returning `404` when fetching it afterward

## Database migrations

When changing database columns or constraints:

1. Update the SQLAlchemy model in `app/models.py`.
2. Generate a migration:

   ```powershell
   python -m alembic revision --autogenerate -m "Describe the schema change"
   ```

3. Review the generated file in `alembic/versions/`, including its `upgrade()` and `downgrade()` operations.
4. Apply it:

   ```powershell
   python -m alembic upgrade head
   ```

`head` means the latest migration revision. To inspect the development database's current revision:

```powershell
python -m alembic current
```

Alembic records the applied revision in the database's `alembic_version` table. Each database has its own migration state. Generating a migration creates a Python script; applying it changes the database structure.

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
Invalid request data returns `422`. Successful deletion returns `204` with an empty response body.

### Issue fields

| Field | Create | Update | Values or validation |
| --- | --- | --- | --- |
| `title` | Required | Optional | 3 to 100 characters on creation; up to 100 on update |
| `description` | Required | Optional | 5 to 1000 characters on creation; up to 1000 on update |
| `priority` | Optional | Optional | `low`, `medium`, `high`; defaults to `medium` |
| `status` | Set by server | Optional | `open`, `in_progress`, `closed`; new issues start as `open` |
| `id` | Set by server | N/A | UUID string |
| `created_at` | Set by server | N/A | Timestamp with time zone; initialized by PostgreSQL on creation |
| `updated_at` | Set by server | Set by server | Timestamp with time zone; initialized on creation and refreshed when SQLAlchemy updates the row |

PUT updates the supplied non-null fields. Other fields keep their existing values. Responses include the ID, issue fields, and both timestamps; timestamps are serialized as strings in JSON.

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

The API stores issues in the PostgreSQL `issues` table:

```text
FastAPI -> SQLAlchemy ORM -> PostgreSQL
```

The SQLAlchemy `Issue` model maps Python objects to database rows. The Pydantic schemas (`IssueCreate`, `IssueUpdate`, and `IssueOut`) define API validation and response fields. Each request using the database dependency gets its own Session; write endpoints commit their transactions to persist changes.

```text
main.py                       FastAPI app, CORS, and middleware setup
app/database.py               Engine, declarative Base, and Session dependency
app/models.py                 SQLAlchemy table mappings
app/schemas.py                Pydantic request and response schemas
app/enums.py                  Shared priority and status choices
app/routes/issues.py          Issue CRUD endpoints
app/middleware/timer.py       Response timing header
alembic.ini                   Alembic configuration
alembic/env.py                Database connection and model metadata for migrations
alembic/versions/             Versioned database migration scripts
tests/conftest.py             Test configuration and database cleanup
tests/test_issues.py          API behavior tests
requirements.txt              Python dependencies
.env.example                  Example database configuration with placeholders
```

The app currently allows requests from any CORS origin and does not implement authentication.
