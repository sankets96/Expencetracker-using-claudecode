# Spec: Registration

## Overview

Registration lets a new visitor create a Spendly account by providing a full name, email address, and password. It is the first authentication step in the roadmap: Step 1 (database setup) provides the `users` table, and registration is what populates it with real accounts. Once a user exists, the later steps — login/logout (Step 3), profile (Step 4), and expense management (Steps 7–9) — can authenticate that user and associate their data with them. The feature must store passwords as Werkzeug hashes, never as plain text, and must reject duplicate emails using the `UNIQUE` constraint on `users.email`.

> **Note:** A working implementation of this feature already exists in `app.py` (`register()` route) and `templates/register.html`. This spec documents the target state and the small convention fixes required to bring the existing code fully in line with `CLAUDE.md`.

## Depends on

- **Step 01 — Database setup** — `database/db.py` must provide `get_db()`, `init_db()`, and `seed_db()`, and the `users` table must exist with a `UNIQUE` constraint on `email` and a `password_hash` column.

## Routes

- `GET /register` — renders the registration form — public
- `POST /register` — validates the submitted name/email/password, hashes the password, inserts the user, and redirects to the login page on success — public

## Database changes

No new tables, columns, or constraints.

The existing `users` table (from Step 1) is sufficient:

| Column          | Type    | Constraints                |
| --------------- | ------- | -------------------------- |
| `id`            | INTEGER | Primary key, autoincrement |
| `name`          | TEXT    | NOT NULL                   |
| `email`         | TEXT    | UNIQUE, NOT NULL           |
| `password_hash` | TEXT    | NOT NULL                   |
| `created_at`    | TEXT    | DEFAULT `datetime('now')`  |

The `UNIQUE` constraint on `email` is what the route relies on to reject duplicate registrations (a `sqlite3.IntegrityError` on insert).

## Templates

- **Create:** none — `templates/register.html` already exists.
- **Modify:** `templates/register.html`
  - Replace the hardcoded `action="/register"` with `action="{{ url_for('register') }}"` (the template currently violates the "never hardcode URLs" rule).
  - No other changes required; the form already extends `base.html` and uses the existing auth CSS classes.

## Files to change

- `app.py` — the `register()` route. Already implemented; verify it matches the behavior below and keep it as the single source of the registration flow.
- `templates/register.html` — fix the hardcoded form action (see Templates).

## Files to create

None.

## New dependencies

No new dependencies. Werkzeug (already in `requirements.txt`) provides `generate_password_hash`.

## Rules for implementation

- No SQLAlchemy or ORMs — use Python's `sqlite3` module directly.
- Parameterised queries only — never f-strings or string concatenation in SQL.
- Passwords hashed with Werkzeug's `generate_password_hash` — never store plain text.
- Use CSS variables — never hardcode hex values.
- All templates extend `base.html`.
- Never hardcode URLs in templates — always use `url_for()`.
- Use `abort()` for HTTP errors, not bare string returns.
- Keep the route's responsibility narrow: read the form, validate, insert, redirect.

## Definition of done

- [ ] `GET /register` renders the registration form with fields for name, email, and password.
- [ ] Submitting the form with all three fields creates a new row in `users`.
- [ ] The stored `password_hash` is a Werkzeug hash, not the plain-text password.
- [ ] Submitting with any field missing re-renders the form with an error message and does not insert a row.
- [ ] Submitting an email that already exists re-renders the form with an error message and does not insert a duplicate row.
- [ ] A successful registration redirects to the login page and shows a confirmation flash message.
- [ ] `templates/register.html` uses `url_for('register')` for the form action — no hardcoded URLs.
- [ ] All SQL in the registration flow uses `?` placeholders.
- [ ] The app starts without errors on port 5001 and the registration flow works end to end.
