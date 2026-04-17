# LinkForge Backend

FastAPI REST API for LinkForge — a link-in-bio page builder.

## Tech Stack

- **FastAPI** 0.135 — API framework
- **SQLAlchemy** 2.0 — ORM (declarative mapped columns)
- **Alembic** 1.18 — database migrations
- **PostgreSQL** — via `psycopg2-binary`
- **Argon2** — password hashing (`passlib` + `argon2-cffi`)
- **python-jose** — JWT access + refresh tokens
- **boto3** — Cloudflare R2 (S3-compatible) for avatar uploads
- **Uvicorn** — ASGI server

## Requirements

- Python 3.12+
- PostgreSQL database
- Cloudflare R2 bucket (for avatar uploads)

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database and R2 credentials

# Run migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload --port 8000
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `CONNECTION_STRING` | PostgreSQL connection URL | — (required) |
| `SECRET_KEY` | JWT signing secret | — (required) |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `localhost:3000,3001` |
| `CLOUDFLARE_R2_API` | R2 S3-compatible endpoint URL | — |
| `R2_ACCESS_KEY_ID` | R2 access key | — |
| `R2_SECRET_ACCESS_KEY` | R2 secret key | — |
| `BUCKET_NAME` | R2 bucket name | `linkinbio` |
| `R2_PUBLIC_URL` | Public URL prefix for uploaded files | — |

## Data Model

```
User
└── Card(s)           — JSONB style, belongs to user
    ├── Link(s)       — top-level (collection_id = NULL)
    └── Collection(s) — groups of links
        └── Link(s)   — nested inside collection
```

- Each user has a `current_card` pointing to their active card
- Cards store full theming in a `style` JSONB column
- Links and collections share a unified `position` ordering on each card

## API Routes

### Auth — `/auth`
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/signup` | Register (creates user + default card) |
| POST | `/auth/login` | Login (case-insensitive username) |
| POST | `/auth/refresh` | Rotate access + refresh tokens |
| GET | `/auth/me` | Current authenticated user |

### Cards — `/cards`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/cards/me` | List user's cards |
| POST | `/cards` | Create a new card |
| GET | `/cards/{id}/list` | Card with merged items list |
| GET | `/cards/{id}` | Public card view (includes user) |
| PATCH | `/cards/{id}` | Rename card |
| PATCH | `/cards/{id}/style` | Update card style (JSONB) |
| DELETE | `/cards/{id}` | Delete card |
| PATCH | `/cards/{id}/reorder` | Reorder top-level items |

### Links — `/links`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/links` | List links (by card_id, collection_id) |
| POST | `/links` | Create link (auto-positions) |
| PATCH | `/links/reorder` | Reorder links within a collection |
| PATCH | `/links/{id}` | Update link (title, url, move) |
| PATCH | `/links/{id}/move` | Move link between collections |
| DELETE | `/links/{id}` | Delete link |

### Collections — `/collections`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/collections` | List collections (by card_id) |
| POST | `/collections` | Create collection |
| PATCH | `/collections/{id}` | Rename collection |
| DELETE | `/collections/{id}` | Delete collection (cascades links) |

### Profile — `/profile`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/profile/me` | Authenticated user's profile |
| POST | `/profile/upload-avatar` | Upload avatar to R2 |
| PATCH | `/profile/me` | Update profile fields |
| GET | `/profile/{username}` | Public profile (current card) |
| PATCH | `/profile/current` | Set active card |

### Other
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/protected/ping` | Auth test endpoint |

## Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── requirements.txt     # Python dependencies
├── alembic.ini          # Alembic config
├── alembic/             # Migration scripts
├── models/
│   ├── userModel.py     # User model
│   ├── cardModel.py     # Card model + DEFAULT_STYLE
│   ├── LinkModel.py     # Link model
│   └── CollectionModel.py  # Collection model
├── routes/
│   ├── auth.py          # Signup, login, refresh, me
│   ├── cards.py         # Card CRUD + reorder
│   ├── links.py         # Link CRUD + reorder + move
│   ├── collections.py   # Collection CRUD
│   ├── profile.py       # Profile + avatar upload
│   └── protected.py     # Auth test
├── schemas/
│   ├── auth.py          # Auth request/response schemas
│   ├── cards.py         # Card schemas + CardStyle
│   ├── links.py         # Link schemas
│   ├── collections.py   # Collection schemas
│   └── profile.py       # Profile schemas
└── lib/
    ├── database.py      # SQLAlchemy engine + session
    ├── auth.py          # get_current_user dependency
    ├── security.py      # Password hashing + JWT
    ├── cors.py          # CORS origin config
    └── s3.py            # Cloudflare R2 upload
```
