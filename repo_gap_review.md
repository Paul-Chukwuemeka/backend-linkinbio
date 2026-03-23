# Backend Gap Review

Reviewed on 2026-03-23 for the current backend workspace only.

## Severity Legend

- `Critical`: blocks startup or core runtime behavior now
- `High`: major product/API capability missing or behavior likely to break expected flows
- `Medium`: important mismatch, incomplete validation, or maintainability gap
- `Low`: hygiene, tooling, or project-setup gap

## Critical

### 1. Application startup is coupled to a live database connection

- Severity: `Critical`
- Missing: safe startup/import path when the database is unavailable
- Evidence:
  - `main.py:11` runs `Base.metadata.create_all(bind=engine)` at import time
  - `lib/database.py:9-14` requires `CONNECTION_STRING` and creates the engine immediately
- Impact:
  - Importing the app fails if the configured database is not reachable
  - This was observed during review when `import main` raised `sqlalchemy.exc.OperationalError`

## High

### 2. Profile setup is largely unimplemented

- Severity: `High`
- Missing:
  - profile update endpoint
  - authenticated profile read at `/profile/me`
  - profile fields for bio, avatar, theme, and richer display customization
- Evidence:
  - `routes/profile.py:11-17` only exposes public `GET /profile/{username}`
  - `routes/auth.py:66-68` exposes `GET /auth/me`, not `GET /profile/me`
  - `models/userModel.py:18-23` only stores `username`, `password`, `email`, `fullname`
  - `schemas/profile.py:7-13` only returns `id`, `username`, `fullname`, `cards`
- Impact:
  - the repo does not satisfy the documented profile setup feature
  - public profiles cannot expose theme/avatar/bio because the data is absent

### 3. Auth flow is incomplete

- Severity: `High`
- Missing:
  - refresh tokens
  - logout endpoint/flow
- Evidence:
  - `project.md:20` describes `JWT (access + refresh tokens)`
  - `project.md:28` lists register, log in, and log out
  - `schemas/auth.py:26-29` returns only `access_token`
  - `routes/auth.py:15-68` has signup, login, and me routes only
- Impact:
  - clients cannot refresh sessions without full re-login
  - logout semantics are undefined

### 4. Card deletion is missing

- Severity: `High`
- Missing: delete endpoint for cards
- Evidence:
  - `routes/cards.py:22-246` contains list, create, get, update, and reorder handlers
  - there is no `@router.delete("/{card_id}")` route
- Impact:
  - users can create cards but cannot remove them through the API

### 5. Collection reorder is missing despite schema support

- Severity: `High`
- Missing: route for batch reordering collections
- Evidence:
  - `schemas/collections.py:23-30` defines `CollectionReorderItem` and `CollectionReorderRequest`
  - `routes/collections.py:14-18` imports `CollectionReorderRequest`
  - `routes/collections.py:24-154` never uses it
- Impact:
  - collection ordering can only be changed indirectly through mixed card-item reorder
  - the collection-specific reorder contract appears unfinished

### 6. Ordered reads are not guaranteed after reordering

- Severity: `High`
- Missing: stable ordering on ORM relationships used by public and card detail responses
- Evidence:
  - `models/cardModel.py:25-30` defines `links` and `collections` relationships without `order_by`
  - `models/CollectionModel.py:27-29` defines `links` without `order_by`
  - `schemas/cards.py:16-23` and `schemas/profile.py:7-13` serialize those relationship lists directly
- Impact:
  - reorder endpoints may succeed while subsequent reads return items in database/default relationship order
  - this is especially risky for `GET /profile/{username}` and `GET /cards/{card_id}`

## Medium

### 7. Project spec and implemented auth routes do not match

- Severity: `Medium`
- Missing: either the documented `/auth/register` route or updated documentation
- Evidence:
  - `project.md:89` documents `POST /auth/register`
  - `routes/auth.py:15` implements `POST /auth/signup`
- Impact:
  - frontend/client integration will break if it follows the current project spec

### 8. Documented user and link fields are missing from the models

- Severity: `Medium`
- Missing:
  - user: `bio`, `avatar_url`, `theme`, `created_at`
  - link: `is_active`, `created_at`
- Evidence:
  - `project.md:71-80` lists those fields in the data model
  - `models/userModel.py:15-23` and `models/LinkModel.py:17-35` do not define them
- Impact:
  - the persisted schema does not match the product spec
  - future features will require schema expansion before implementation can begin

### 9. Link reorder inside collections is only partially validated

- Severity: `Medium`
- Missing:
  - duplicate position validation
  - contiguous/full-payload validation similar to top-level card reorder
- Evidence:
  - `routes/links.py:117-172` only checks duplicate ids and existence
  - `routes/cards.py:181-202` performs stricter validation for top-level mixed-item reorder
- Impact:
  - collection link ordering can drift into duplicate or partial states more easily than top-level ordering

### 10. Input validation is weaker than the domain suggests

- Severity: `Medium`
- Missing:
  - typed email validation
  - typed URL validation
- Evidence:
  - `schemas/auth.py:14-18` uses plain `str` for email
  - `schemas/links.py:5-15` uses plain `str` for URL
- Impact:
  - invalid emails and malformed URLs can pass validation and become stored data

### 11. Database strategy in docs and runtime setup is out of sync

- Severity: `Medium`
- Missing: one clear database story across docs, env setup, and dependencies
- Evidence:
  - `project.md:19` says SQLite
  - `lib/database.py:9-14` expects a generic `CONNECTION_STRING`
  - `requirements.txt:14` includes `psycopg2-binary`
- Impact:
  - onboarding and deployment assumptions are unclear
  - current environment appears closer to PostgreSQL than SQLite

## Low

### 12. Schema migrations are missing

- Severity: `Low`
- Missing: Alembic or equivalent migration workflow
- Evidence:
  - no `alembic.ini` or `alembic/` directory was found in the backend repo
  - `main.py:11` relies on `create_all()` instead
- Impact:
  - schema evolution will become brittle once production data exists

### 13. Automated tests are missing

- Severity: `Low`
- Missing: test suite and test runner config
- Evidence:
  - no `tests/`, `pytest.ini`, or `pyproject.toml` was found in the backend repo
  - `requirements.txt` contains no test tooling
- Impact:
  - regressions in auth, ordering, and ownership checks are easy to miss

### 14. Setup documentation is missing

- Severity: `Low`
- Missing:
  - backend `README`
  - `.env.example`
  - documented local run steps
- Evidence:
  - no backend `README*` file was found
  - runtime-required env vars are implied by `lib/database.py` and `lib/security.py`
- Impact:
  - a new developer has no authoritative setup path

## Notes

- This review covers the backend repo currently present in the workspace.
- The workspace root is not a Git repository, so no history or tracked-file review was possible.
