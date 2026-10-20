# Issue Tracker API

A small FastAPI project for learning how to build a database-backed REST API. It lets you create, list, view, update, and delete issues. Issues are stored in PostgreSQL using SQLAlchemy 2.0, and Alembic manages changes to the database structure.

## Choose a setup

- [Run with Docker Compose](#run-with-docker-compose): Docker runs both the API and PostgreSQL.
- [Run locally without Docker](#run-locally-without-docker): use a local Python virtual environment and PostgreSQL installation.
- [Run the tests](#run-the-tests): use the local virtual environment and a separate test database.
- [Database migrations](#database-migrations): generate, review, and apply schema changes.

Commands below use Windows PowerShell and run from the project root, where `main.py` and `docker-compose.yml` live. Both app setups expose port `8000`; stop one before starting the other. Their databases are separate, so issues created in one setup do not automatically appear in the other.

## What it covers

- API routes and HTTP status codes
- Request validation and response models with Pydantic
- Enums for issue priority and status
- PostgreSQL persistence using SQLAlchemy 2.0
- A database Session for each request
- Database migrations using Alembic
- Configuration through `.env` files
- Docker images, containers, networking, and persistent volumes with Docker Compose
- Automated API tests using pytest and FastAPI's `TestClient`
- Middleware that adds an `X-Process-Time` response header
- Automatic interactive API documentation from FastAPI

## Requirements

For the Docker setup:

- Docker Desktop running with Linux containers and Docker Compose
- Port `8000` available on your computer

Docker supplies Python and PostgreSQL. For running the app and tests directly on your computer instead:

- Python 3.12 (used for development and testing)
- `pip`
- PostgreSQL installed and running locally
- SQL Shell (`psql`) or another PostgreSQL client

## Configuration reference

Keep all three settings in `.env` to support both setups:

| Setting | Used by | Value |
| --- | --- | --- |
| `DATABASE_URL` | Local Uvicorn and Alembic | Local PostgreSQL URL using `localhost:5432` |
| `POSTGRES_PASSWORD` | Compose's `db` service | Raw password chosen for the Docker database login |
| `DOCKER_DATABASE_URL` | Compose's `api` service | Docker PostgreSQL URL using `db:5432`, with that same Docker password URL-encoded |

The local and Docker database passwords may differ. Keep the two Docker settings consistent with each other. `.env.test` supplies a separate `DATABASE_URL` pointing to the local `issue_tracker_test` database. `.env` and `.env.test` are ignored by Git and excluded from the Docker build; `.env.example` contains placeholders for sharing the required settings.

## Run with Docker Compose

### 1. Start Docker and configure the connection

Open Docker Desktop and wait for its engine to start. Verify that Docker can reach the engine and that Compose is available:

```powershell
docker version
docker compose version
```

`docker version` should show both Client and Server information.

For a fresh checkout, copy the example configuration from the project root:

```powershell
Copy-Item -LiteralPath .env.example -Destination .env
```

If `.env` already exists, edit it instead of overwriting it. Set these two Docker settings:

```ini
POSTGRES_PASSWORD='YOUR_CHOSEN_PASSWORD'
DOCKER_DATABASE_URL='postgresql+psycopg://issue_tracker_user:YOUR_URL_ENCODED_PASSWORD@db:5432/issue_tracker'
```

Use the same password in both settings: the original password in `POSTGRES_PASSWORD`, and its URL-encoded form in `DOCKER_DATABASE_URL`. For example, `@` becomes `%40` in the URL. Compose passes `DOCKER_DATABASE_URL` to the API container as `DATABASE_URL`. The separate `DATABASE_URL` setting in `.env` is for running Python directly on your computer.

### 2. Build and start the stack

Start the stack:

```powershell
docker compose up --build
```

Open [Swagger UI](http://localhost:8000/docs). Compose starts two services:

- `db`: PostgreSQL 17, with database `issue_tracker` and login `issue_tracker_user`.
- `api`: the FastAPI image built from `Dockerfile`, exposed on your computer at port `8000`.

The API waits for the database health check, runs `python -m alembic upgrade head`, and starts Uvicorn if migrations succeed. Inside the API container, `db:5432` reaches PostgreSQL through the Compose network; `localhost` would refer to the API container itself. PostgreSQL's port is not published to the host.

On the first run, PostgreSQL creates the login and database, and Alembic creates the application tables. You do not need to create the database manually or install Python packages on your computer for this setup.

Useful commands from another terminal:

```powershell
docker compose ps
docker compose logs api
docker compose logs db
docker compose exec api python -m alembic current
docker compose exec api python -m alembic upgrade head
```

Source files are copied into the image. After changing code or adding migration files, rebuild with `docker compose up --build` so the container receives the changes. Migration generation and review are described below; startup applies existing migration files.

### 3. Verify CRUD and persistence

In Swagger UI, use the `/api/v1/issues` endpoints to check:

1. Create an issue: expect `201` and save its ID.
2. Fetch that ID: expect `200` and the saved fields.
3. Update it: expect `200`; fetch it again to confirm the changes.

Keep the issue for the restart check. Press Ctrl+C in the stack's terminal, then run:

```powershell
docker compose down
docker compose up --build
```

Fetch the saved ID: the issue should still exist. The named volume `postgres_data` stores PostgreSQL's data outside the container. Ordinary `docker compose down` preserves it; `docker compose down -v` deletes it. PostgreSQL initialization settings apply when that volume is empty; changing `POSTGRES_PASSWORD` later does not change an existing database password.

Finally, delete that issue: expect `204`, followed by `404` when fetching its ID. You can also inspect the stored rows directly:

```powershell
docker compose exec db psql -U issue_tracker_user -d issue_tracker -c "SELECT id, title, status FROM issues;"
```

To stop the stack, press Ctrl+C in its terminal and run `docker compose down`. Use the same Compose project name between runs to reuse the same volume.

## Run locally without Docker

### 1. Install the Python dependencies

From the project root, create a virtual environment and install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Create the databases

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

### 3. Configure the connection

For a fresh setup, copy the example configuration to `.env` in the project root:

```powershell
Copy-Item -LiteralPath .env.example -Destination .env
```

If you already configured `.env` for Docker, keep it and edit its existing `DATABASE_URL` line. Leave `POSTGRES_PASSWORD` and `DOCKER_DATABASE_URL` in place; the local app does not use them.

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

### 4. Apply migrations and start the server

From the project root, apply the existing migrations to the development database:

```powershell
python -m alembic upgrade head
```

Then start the development server:

```powershell
python -m uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` to try the endpoints in Swagger UI, or `http://127.0.0.1:8000/redoc` for ReDoc.

Press Ctrl+C to stop Uvicorn. In a new terminal, activate `.venv` again before running Python commands. PostgreSQL must remain running while the app or tests use it.

## Run the tests

These instructions run pytest on your computer using the local Python and PostgreSQL setup above. Compose creates the application database only. Tests use the separate `issue_tracker_test` PostgreSQL database. Before the first test run, apply the migrations to it:

```powershell
python -m dotenv -f .env.test run -- .\.venv\Scripts\python.exe -m alembic upgrade head
```

The `dotenv` command loads `.env.test` for the migration process. The explicit executable path selects the project's virtual environment on Windows. Repeat this command after adding new migrations so the test database stays up to date.

Run the suite from the project root:

```powershell
python -m pytest -v
```

The suite uses `TestClient` to call the application directly, so you do not need to start Uvicorn. The test database must be running and migrated.

`tests/conftest.py` loads `.env.test` before importing the application. Its client fixture checks that the database is named `issue_tracker_test`, then deletes all issue rows before and after each test. The test database should be dedicated to this suite.

The tests cover:

- Creating an issue and checking its response fields and defaults
- Rejecting invalid input with `422`
- Fetching the correct issue by ID
- Returning `404` for an unknown ID
- Updating an issue and fetching the saved changes
- Deleting an issue with `204` and returning `404` when fetching it afterward

## Database migrations

The generation commands below use the local virtual environment and the local `DATABASE_URL` in `.env`. Start from a database with all existing migrations applied (`python -m alembic upgrade head`).

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

Keep generated migration files in the repository alongside the model changes. Rebuild the Docker stack with `docker compose up --build` to include those files; the API startup command applies them to the Docker database. Apply them separately to the local test database using the command in [Run the tests](#run-the-tests).

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

Fetch the issue, then delete it:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/issues/$($issue.id)"

Invoke-RestMethod -Method Delete `
  -Uri "http://127.0.0.1:8000/api/v1/issues/$($issue.id)"
```

Deletion returns an empty response. Fetching that ID again returns `404`.

## Common setup problems

| Symptom | What to check |
| --- | --- |
| Docker cannot connect to `dockerDesktopLinuxEngine` | Start Docker Desktop, select Linux containers, and wait until `docker version` shows Server information. |
| Port `8000` is already in use | Stop the other Uvicorn process or Compose stack using it. |
| Local Python cannot import an installed package | Activate `.venv` and install dependencies with `python -m pip install -r requirements.txt` in that environment. |
| Database authentication fails | Check the password for the selected database and URL-encode it in the URL. For an existing Docker volume, use the password with which that database was initialized. |
| The API reports that the `issues` table does not exist | Apply migrations to the selected database. For Docker, inspect `docker compose logs api` for a failed startup migration. |
| Local tests reject the database configuration | Set `DATABASE_URL` in `.env.test` to the dedicated `issue_tracker_test` database and apply its migrations. |

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
Dockerfile                    Python image, dependencies, and API startup command
docker-compose.yml            API and PostgreSQL services, migrations, and data volume
.dockerignore                 Files excluded from the Docker build context
```

The app currently allows requests from any CORS origin and does not implement authentication.
