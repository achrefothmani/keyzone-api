# Keyzone CRM API

Production-ready FastAPI backend for the Keyzone real-estate CRM. Built with
**FastAPI · async SQLAlchemy 2 · PostgreSQL 15 · Alembic · Docker**.

## Stack

- **FastAPI 0.115** – async REST API + OpenAPI docs at `/docs`
- **SQLAlchemy 2** with `asyncpg` driver – async ORM
- **Alembic** – schema migrations
- **Pydantic v2** – request/response validation, settings
- **PostgreSQL 15** – primary store
- **JWT** auth (HS256) with bcrypt password hashing
- **Pytest + httpx** – test suite (uses in-memory SQLite via `aiosqlite`)
- **Docker Compose** – api + postgres + pgadmin
- **uv** – fast Python package manager

## Project layout

```
app/
  api/v1/routes/    # auth, users, properties, images
  core/             # settings, security, logging, error handlers
  db/               # Base, async session
  models/           # User, Property, PropertyImage (+ enums)
  schemas/          # Pydantic models
  repositories/     # Data access (filters, pagination)
  services/         # Business logic (email auto-gen, references…)
  utils/            # slug helpers, reference generator
alembic/            # migrations
tests/              # pytest suite (in-memory SQLite)
main.py             # FastAPI app + CORS + lifespan
```

---

## 🚀 Quick start

### Option 1 — Docker (recommended)

The fastest path: spin up API + Postgres + pgAdmin with one command.

```bash
cp .env.example .env       # tweak SECRET_KEY etc.
docker compose up --build
```

Running services:

| Service  | URL                          | Credentials                     |
| -------- | ---------------------------- | ------------------------------- |
| Swagger  | http://localhost:8000/docs   | —                               |
| ReDoc    | http://localhost:8000/redoc  | —                               |
| API root | http://localhost:8000        | —                               |
| pgAdmin  | http://localhost:5050        | admin@keyzone.local / admin     |
| Postgres | localhost:5432               | admin / admin (db: realestate)  |

The API container runs `alembic upgrade head` on startup, so the schema is
applied automatically.

Stop everything:

```bash
docker compose down              # keep data
docker compose down -v           # also delete the postgres volume
```

### Option 2 — Local with `uv`

[`uv`](https://docs.astral.sh/uv/) is a drop-in replacement for `pip` and
`venv`, ~10–100× faster.

```bash
# 1. Install uv (skip if already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create the venv (Python 3.11) and install deps
uv venv --python 3.11
uv pip install -r requirements.txt
source .venv/bin/activate

# 3. Configure env
cp .env.example .env
# point DATABASE_URL at your local Postgres or run only Postgres in Docker:
#   docker compose up postgres -d

# 4. Apply migrations and run
alembic upgrade head
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open <http://localhost:8000/docs>.

> **Hot reload**: `uvicorn ... --reload` watches the project tree.

---

## 🧪 Testing

The test suite uses **SQLite in-memory** via `aiosqlite` and overrides the auth
dependency, so **no Postgres or running server is required**.

```bash
# inside the activated uv venv
pytest                 # run everything
pytest -v              # verbose
pytest tests/test_properties.py -v   # one file
pytest -k "email"      # filter by name
```

Expected output:

```
tests/test_auth.py ...                                                   [ 27%]
tests/test_health.py ..                                                  [ 45%]
tests/test_properties.py ....                                            [ 81%]
tests/test_users.py ..                                                   [100%]
============================== 11 passed in ~2s ==============================
```

---

## 🛠 Common tasks

### Migrations

```bash
# Generate a new migration after editing models
alembic revision --autogenerate -m "add foo column"

# Apply
alembic upgrade head

# Rollback one revision
alembic downgrade -1

# Inside Docker
docker compose exec api alembic revision --autogenerate -m "..."
docker compose exec api alembic upgrade head
```

### Add or update a dependency

```bash
# add to requirements.txt, then
uv pip install -r requirements.txt
# or one-off:
uv pip install ruff
```

### Seed admin user

If you need to quickly initialize an admin user:

```bash
# Docker
docker compose exec api python -m scripts.seed_admin

# Local
PYTHONPATH=. python scripts/seed_admin.py
```

The default credentials are:
- **Email**: `admin@keyzonestates.tn`
- **Password**: `admin-password`

You can change these in `.env` via `FIRST_SUPERUSER_EMAIL` and `FIRST_SUPERUSER_PASSWORD`.

### Reset the database (Docker)

```bash
docker compose down -v && docker compose up --build
```

### Tail logs

```bash
docker compose logs -f api
docker compose logs -f postgres
```

---

## 📡 API surface (v1)

All routes live under `/api/v1`. Browsable + try-it-out at `/docs`.

### Auth
- `POST /auth/register` – create a user (email auto-generated)
- `POST /auth/login` – `{email,password}` → `{access_token, …}`
- `POST /auth/login/form` – OAuth2 password flow (used by Swagger's *Authorize* button)
- `GET  /auth/me` – current user

### Users (manager-restricted writes)
- `GET    /users` – filters: `zone`, `role`, `search`, `limit`, `offset`
- `POST   /users`
- `GET    /users/{id}`
- `PUT    /users/{id}` – password / role updates; email regenerates if name changes
- `DELETE /users/{id}`

### Properties
- `GET    /properties` – filters: `reference`, `type`, `vocation`, `status`,
  `city`, `furnished`, `min_price`, `max_price`, `responsible_id`, `search`;
  sorting via `sort_by` (`price|created_at|updated_at`) and `sort_dir`
- `POST   /properties`
- `GET    /properties/{id}`
- `PUT    /properties/{id}`
- `DELETE /properties/{id}` (soft delete – `is_deleted=true`)

### Property images
- `GET    /properties/{id}/images`
- `POST   /properties/{id}/images`
- `DELETE /images/{id}`

---

## 🧠 Business rules

- **Email auto-generation**: `prenom.nom@keyzonestates.tn`. Accents are stripped
  and a numeric suffix is appended on collision (e.g.
  `mehdi.trabelsi1@keyzonestates.tn`).
- **Property reference**: auto-generated as `KZ-XXXXXX` (hex) when not supplied.
- **Soft delete** for properties (`is_deleted` flag) so listings can be undeleted.
- **RBAC**: user create/update/delete restricted to `CHEF_AGENCE` and
  `COORDINATEUR`.

## 🗄️ Schema highlights

- Enums match the Next.js frontend exactly:
  - `PropertyType`: `Villa | Appartement | Studio | Local commercial | Terrain | Bureau`
  - `PropertyStatus`: `Disponible | Réservé | Vendu | Loué`
  - `PropertyVocation`: `Vente | Location`
  - `PropertyValidation`: `Validée | En attente | Brouillon`
  - `UserRole`: `CHEF_AGENCE | AGENT | COORDINATEUR`
- Indexed columns: `properties.city`, `properties.price`, `properties.type`,
  `properties.vocation`, `properties.status`, `properties.responsible_id`,
  `users.role`, `users.zone`.

---

## 🌐 Connecting from the Next.js frontend

CORS is preconfigured for `http://localhost:3000` and `http://localhost:3002`. To add more origins, edit
`BACKEND_CORS_ORIGINS` in `.env`:

```env
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:3002","https://crm.keyzonestates.tn"]
```

Quick smoke test from the frontend's working directory:

```bash
curl -s http://localhost:8000/health
# {"status":"ok"}

curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H 'content-type: application/json' \
  -d '{"nom":"Bahri","prenom":"Sami","password":"supersecret","role":"CHEF_AGENCE"}'
```

---

## 🔐 Environment variables

All defaults are safe for local Docker. **Override `SECRET_KEY` in production.**

| Variable | Default | Notes |
|----------|---------|-------|
| `PROJECT_NAME` | `Keyzone CRM API` | |
| `ENVIRONMENT` | `development` | |
| `SECRET_KEY` | `change-me` | **change in prod** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | |
| `POSTGRES_HOST` | `postgres` | use `localhost` outside Docker |
| `POSTGRES_DB/USER/PASSWORD` | `realestate/admin/admin` | |
| `DATABASE_URL` | derived | full async URL, overrides above |
| `SYNC_DATABASE_URL` | derived | used by Alembic |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:3000","http://localhost:3002"]` | JSON array or comma list |
| `EMAIL_DOMAIN` | `keyzonestates.tn` | suffix for auto-generated emails |
| `FIRST_SUPERUSER_EMAIL` | `admin@keyzonestates.tn` | initial admin email |
| `FIRST_SUPERUSER_PASSWORD` | `admin-password` | initial admin password |

---

## 🧰 Troubleshooting

- **`pg_config not found` when installing `psycopg2-binary` on Python 3.14+**:
  use Python 3.11 (the version pinned by Docker and `uv venv --python 3.11`).
- **Migrations fail with `enum already exists`**: a previous migration was
  half-applied. `docker compose down -v` to wipe the volume, then retry.
- **`401 Could not validate credentials`** in Swagger: click *Authorize* and use
  the OAuth2 form (`/auth/login/form`), or paste a token from `/auth/login`.
