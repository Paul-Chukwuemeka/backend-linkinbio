# Backend Gap Review

Reviewed on 2026-03-23 for the current backend workspace only.

## Severity Legend

- `Critical`: blocks startup or core runtime behavior now
- `High`: major product/API capability missing or behavior likely to break expected flows
- `Medium`: important mismatch, incomplete validation, or maintainability gap
- `Low`: hygiene, tooling, or project-setup gap

## Resolved Since Initial Review

- Safe app import/startup path: `main.py` no longer touches the database at import time, and `lib/database.py` now exposes lazy engine/session getters.
- Profile setup API: `GET /profile/me` and `PATCH /profile/me` now exist, and `User` now has `bio`, `avatar_url`, and `theme`.
- Auth refresh support: auth responses now include both `access_token` and `refresh_token`, and `POST /auth/refresh` exists.
- Card deletion: `DELETE /cards/{card_id}` now exists.
- Ordered relationship reads: `card.links`, `card.collections`, `collection.links`, and `user.cards` now have deterministic ordering.
- Alembic scaffolding exists and loads successfully.

## Current Open Issues

## High

### 1. Logout and server-side session revocation are still missing

- Severity: `High`
- Missing:
  - logout endpoint/flow
  - server-side revocation for refresh tokens
- Evidence:
  - `project.md:28` documents "Register, log in, log out with JWT-based authentication"
  - `routes/auth.py` currently exposes `signup`, `login`, `refresh`, and `me`, but no logout route
  - refresh tokens are stateless JWTs in `lib/security.py`; there is no session table or revocation store
- Impact:
  - clients cannot perform a true server-side logout
  - a leaked refresh token remains usable until expiry

### 2. Alembic migration history cannot bootstrap a fresh database

- Severity: `High`
- Missing:
  - an initial schema migration that creates the base tables
- Evidence:
  - `alembic/versions/e88fd052f423_update.py` only adds `bio`, `avatar_url`, and `theme` to `users`
  - `alembic/versions/f5e9e5f431e4_update.py` is a no-op
  - `alembic upgrade head --sql` emits `ALTER TABLE users ADD COLUMN ...` without any `CREATE TABLE users`, `cards`, `links`, or `collections`
- Impact:
  - Alembic can patch an existing database but cannot initialize a new one from scratch
  - schema history is not yet reliable for new environments

## Medium

### 3. Project spec and implemented auth routes still do not match

- Severity: `Medium`
- Missing:
  - either the documented `/auth/register` route or updated documentation
- Evidence:
  - `project.md:89` documents `POST /auth/register`
  - `routes/auth.py` implements `POST /auth/signup`
- Impact:
  - frontend/client integration will break if it follows `project.md` literally

### 4. Project spec and implemented profile/auth capabilities are still partially out of sync

- Severity: `Medium`
- Missing:
  - documentation updates for refresh flow and current route set
- Evidence:
  - `project.md` does not mention `POST /auth/refresh`
  - `project.md` still treats logout as present, but it is not implemented
- Impact:
  - the code and the written contract now diverge in multiple places

### 5. Data model still does not fully match the documented product spec

- Severity: `Medium`
- Missing:
  - user: `created_at`, and a decision between `display_name` vs the current `fullname`
  - link: `is_active`, `created_at`
- Evidence:
  - `project.md:71-80` lists those fields in the data model
  - `models/userModel.py` now has `bio`, `avatar_url`, and `theme`, but still no `created_at`
  - `models/LinkModel.py` still has no `is_active` or `created_at`
- Impact:
  - the persisted schema still does not fully match the project spec
  - future product features will need more schema changes

### 6. Link reorder inside collections is still only partially validated

- Severity: `Medium`
- Missing:
  - duplicate position validation
  - full/contiguous payload validation comparable to top-level mixed-item reorder
- Evidence:
  - `routes/links.py` checks duplicate ids and existence only
  - `routes/cards.py` does stricter validation for top-level mixed-item reorder
- Impact:
  - collection link ordering can drift into duplicate or partial states more easily than top-level ordering

### 7. Input validation is still weaker than the domain suggests

- Severity: `Medium`
- Missing:
  - typed email validation
  - typed URL validation
- Evidence:
  - `schemas/auth.py` uses plain `str` for email
  - `schemas/links.py` uses plain `str` for URL
- Impact:
  - invalid emails and malformed URLs can pass validation and become stored data

### 8. Database strategy in docs and runtime setup is still out of sync

- Severity: `Medium`
- Missing:
  - one clear database story across docs, env setup, and dependencies
- Evidence:
  - `project.md:19` says SQLite
  - `lib/database.py` expects `CONNECTION_STRING`
  - the current environment and dependencies are PostgreSQL-oriented
- Impact:
  - onboarding and deployment assumptions remain unclear

## Low

### 9. Automated tests are still missing

- Severity: `Low`
- Missing:
  - test suite
  - test runner config
- Evidence:
  - no `tests/`, `pytest.ini`, or `pyproject.toml` was found in the backend repo
- Impact:
  - regressions in auth, ordering, and ownership checks are easy to miss

### 10. Setup documentation is still missing

- Severity: `Low`
- Missing:
  - backend `README`
  - `.env.example`
  - documented local run steps
- Evidence:
  - no backend `README*` file was found
  - runtime-required env vars are implied by `lib/database.py` and `lib/security.py`
- Impact:
  - a new developer still has no authoritative setup path

### 11. Collection-only reorder artifacts are still unused

- Severity: `Low`
- Missing:
  - cleanup of unused schema/imports, or a deliberate collection-only reorder route
- Evidence:
  - `schemas/collections.py` still defines `CollectionReorderRequest`
  - `routes/collections.py` still imports it but does not use it
- Impact:
  - the API surface looks more complex than it really is
  - this can mislead future implementation or client work

## Notes

- This review covers the backend repo currently present in the workspace.
- The workspace root is not a Git repository, so no history or tracked-file review was possible.
