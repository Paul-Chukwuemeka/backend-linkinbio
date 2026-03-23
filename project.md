# LinkForge

LinkForge is a link-in-bio platform where users can create a public profile page and organize links into cards and collections.

This workspace currently contains the backend. The frontend is planned separately and is documented here so both sides stay aligned.

---

## Product Overview

- Users sign up, log in, and manage their content from an authenticated dashboard
- Each user has a public profile page identified by username
- Content is organized into cards
- Each card can contain top-level links and collections
- Collections can contain ordered links

---

## Frontend

### Frontend Goals

- Provide auth screens for sign up and login
- Provide a dashboard for managing cards, links, collections, and profile settings
- Provide a public profile page for visitors
- Support drag-and-drop ordering for top-level card items and links inside collections

### Planned Frontend Stack

| Layer | Technology |
|------|------------|
| Framework | Next.js (App Router) |
| Styling | Tailwind CSS |
| State / Data | API client + auth helpers |
| Deployment | Vercel |

### Planned Frontend Pages

| Route | Description |
|------|-------------|
| `/register` | Sign-up form |
| `/login` | Login form |
| `/dashboard` | Main editor for cards, links, and collections |
| `/dashboard/appearance` | Profile and theme settings |
| `/u/:username` | Public-facing profile page |

### Planned Frontend Structure

```text
frontend/
├── app/
│   ├── login/
│   ├── register/
│   ├── dashboard/
│   ├── dashboard/appearance/
│   └── u/[username]/
├── components/
└── lib/
```

---

## Backend

### Current Backend Stack

| Layer | Technology |
|------|------------|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Auth | JWT access + refresh tokens |
| Database | Configured via `CONNECTION_STRING` |

### Current Backend Structure

```text
backend/
├── alembic/
├── lib/
│   ├── auth.py
│   ├── database.py
│   └── security.py
├── models/
│   ├── userModel.py
│   ├── cardModel.py
│   ├── CollectionModel.py
│   └── LinkModel.py
├── routes/
│   ├── auth.py
│   ├── cards.py
│   ├── collections.py
│   ├── links.py
│   ├── profile.py
│   └── protected.py
├── schemas/
└── main.py
```

### Current Backend Models

#### User

```text
id
username
email
password
fullname
bio
avatar_url
theme
```

#### Card

```text
id
user_id
name
```

#### Collection

```text
id
card_id
title
position
```

#### Link

```text
id
card_id
collection_id
title
url
position
```

### Current Backend API

#### Auth

| Method | Route | Description |
|------|-------|-------------|
| `POST` | `/auth/signup` | Create account |
| `POST` | `/auth/login` | Log in and get access + refresh tokens |
| `POST` | `/auth/refresh` | Refresh token pair |
| `GET` | `/auth/me` | Get authenticated user |

#### Profile

| Method | Route | Description |
|------|-------|-------------|
| `GET` | `/profile/me` | Get current user's profile |
| `PATCH` | `/profile/me` | Update username, fullname, bio, avatar, and theme |
| `GET` | `/profile/{username}` | Get public profile |

#### Cards

| Method | Route | Description |
|------|-------|-------------|
| `GET` | `/cards/me` | List current user's cards |
| `POST` | `/cards` | Create a card |
| `GET` | `/cards/{card_id}` | Get one card |
| `PATCH` | `/cards/{card_id}` | Update card name |
| `DELETE` | `/cards/{card_id}` | Delete a card |
| `GET` | `/cards/{card_id}/items` | Get mixed top-level items for a card |
| `PATCH` | `/cards/{card_id}/items/reorder` | Reorder top-level links and collections |

#### Collections

| Method | Route | Description |
|------|-------|-------------|
| `GET` | `/collections` | List collections for a card |
| `POST` | `/collections` | Create a collection |
| `PATCH` | `/collections/{collection_id}` | Update collection title |
| `DELETE` | `/collections/{collection_id}` | Delete a collection |

#### Links

| Method | Route | Description |
|------|-------|-------------|
| `GET` | `/links` | List links for a card or collection |
| `POST` | `/links` | Create a link |
| `PATCH` | `/links/reorder` | Reorder links inside a collection |
| `PATCH` | `/links/{link_id}` | Update a link |
| `PATCH` | `/links/{link_id}/move` | Move a link between top-level and collections |
| `DELETE` | `/links/{link_id}` | Delete a link |

#### Utility

| Method | Route | Description |
|------|-------|-------------|
| `GET` | `/health` | Basic health endpoint |
| `GET` | `/protected/ping` | Auth-protected test route |

### Backend Auth Notes

- Access tokens are used on protected API requests
- Refresh tokens are used to obtain a new token pair
- Protected routes resolve the current user from the access token subject
- Logout and server-side token revocation are not implemented yet

---

## Shared Product Features

### Current Core Scope

- Auth with access and refresh tokens
- Public profile retrieval by username
- Profile editing for authenticated users
- Card CRUD
- Collection CRUD
- Link CRUD
- Reordering of mixed top-level card items
- Reordering of links inside collections

### Later / Extended Scope

- Richer theme presets and custom themes
- Link click analytics
- Social icon detection from URLs
- QR code generation
- Custom domains
- Avatar upload pipeline

---

## Development Notes

- The backend now uses Alembic for schema migrations
- The app should not create tables automatically on import
- Ordered content is driven by `position` for links and collections
- Card order is currently deterministic but not user-reorderable
- The frontend should treat the backend API contract above as the source of truth, not older route names like `/auth/register`
