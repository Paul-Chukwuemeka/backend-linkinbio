# LinkForge — Link-in-Bio Page Builder

A full-stack link-in-bio platform where users can create a personalized, shareable profile page that hosts all their important links in one place. Think Linktree, but self-hosted and fully customizable.

---

## Overview

LinkForge lets users sign up, build a public profile page with a unique URL (e.g. `linkforge.app/paul`), and manage an ordered list of links with custom labels and icons. Visitors can hit that URL and see a clean, styled page with all their links — no account needed on their end.

---

## Tech Stack

| Layer       | Technology                          |
|-------------|--------------------------------------|
| Frontend    | Next.js (App Router) + Tailwind CSS  |
| Backend     | FastAPI                              |
| Database    | SQLite (via SQLAlchemy)              |
| Auth        | JWT (access + refresh tokens)        |
| Deployment  | Vercel (frontend) + Fly.io (backend) |

---

## Core Features

### MVP
- **Auth** — Register, log in, log out with JWT-based authentication
- **Profile setup** — Set a display name, bio, avatar, and unique username/slug
- **Link management** — Add, edit, reorder, and delete links (title + URL)
- **Public profile page** — A shareable `/:username` page, no login required
- **Basic theming** — Choose from a few preset color themes for your page

### Post-MVP
- Custom themes (background color, font, button style)
- Link click analytics (count hits per link)
- Social media icon auto-detection from URL
- QR code generation for your profile URL
- Custom domain support

---

## Project Structure

```
linkforge/
├── frontend/               # Next.js app
│   ├── app/
│   │   ├── [username]/     # Public profile page (SSR)
│   │   ├── dashboard/      # Authenticated link editor
│   │   ├── login/
│   │   └── register/
│   ├── components/
│   └── lib/                # API client, auth helpers
│
└── backend/                # FastAPI app
    ├── main.py
    ├── routers/
    │   ├── auth.py
    │   ├── links.py
    │   └── profile.py
    ├── models.py            # SQLAlchemy models
    ├── schemas.py           # Pydantic schemas
    └── database.py
```

---

## Data Models

### User
```
id, username (unique), email, hashed_password,
display_name, bio, avatar_url, theme, created_at
```

### Link
```
id, user_id (FK), title, url, is_active,
position (for ordering), created_at
```

---

## API Endpoints (High-Level)

| Method | Route                   | Description                    |
|--------|-------------------------|--------------------------------|
| POST   | `/auth/register`        | Create account                 |
| POST   | `/auth/login`           | Get JWT tokens                 |
| GET    | `/profile/me`           | Get current user's profile     |
| PATCH  | `/profile/me`           | Update profile info/theme      |
| GET    | `/profile/:username`    | Get public profile + links     |
| GET    | `/links`                | List current user's links      |
| POST   | `/links`                | Add a new link                 |
| PATCH  | `/links/:id`            | Edit a link                    |
| DELETE | `/links/:id`            | Delete a link                  |
| PATCH  | `/links/reorder`        | Update link positions (batch)  |

---

## Pages

| Route              | Description                                        |
|--------------------|----------------------------------------------------|
| `/register`        | Sign-up form                                       |
| `/login`           | Login form                                         |
| `/dashboard`       | Link editor — add/edit/delete/reorder links        |
| `/dashboard/appearance` | Theme and profile customization              |
| `/u/:username`       | Public-facing profile page (SSR for SEO)           |

---

## Development Phases

### Phase 1 — Foundation (Week 1)
- [ ] Project scaffolding (Next.js + FastAPI)
- [ ] SQLite + SQLAlchemy setup
- [ ] Auth endpoints + JWT middleware
- [ ] Register/Login pages

### Phase 2 — Core Features (Week 2)
- [ ] Link CRUD API + dashboard UI
- [ ] Drag-to-reorder links
- [ ] Public profile page (`/:username`)

### Phase 3 — Polish (Week 3)
- [ ] Preset themes
- [ ] Avatar upload
- [ ] Mobile responsiveness
- [ ] Deployment

---

## Notes

- SQLite is fine for a weekend/side project scale. Swap in PostgreSQL later if needed.
- The `/:username` route should be server-rendered (Next.js SSR) for SEO and fast first load.
- FastAPI's `StaticFiles` can serve the SQLite DB locally during dev — no separate DB server needed.
- Keep the link reorder logic simple: store an integer `position` per link and do a batch PATCH on drag-end.