# Database Setup Specification

## 1. Overview

Replace the stub implementation in `database/db.py` with a working SQLite-based data layer.

This step establishes the database foundation for the Spendly application. All future features, including authentication, user profiles, and expense tracking, depend on this implementation.

The database must be initialized automatically when the application starts.

---

## 2. Dependencies

This is the first implementation step.

**Depends on:** Nothing

---

## 3. Routes

No new routes are required.

Existing placeholder routes in `app.py` must remain unchanged.

---

## 4. Database Schema

### 4.1 `users` Table

| Column          | Type    | Constraints                |
| --------------- | ------- | -------------------------- |
| `id`            | INTEGER | Primary key, autoincrement |
| `name`          | TEXT    | NOT NULL                   |
| `email`         | TEXT    | UNIQUE, NOT NULL           |
| `password_hash` | TEXT    | NOT NULL                   |
| `created_at`    | TEXT    | DEFAULT `datetime('now')`  |

### 4.2 `expenses` Table

| Column        | Type    | Constraints                        |
| ------------- | ------- | ---------------------------------- |
| `id`          | INTEGER | Primary key, autoincrement         |
| `user_id`     | INTEGER | Foreign key → `users.id`, NOT NULL |
| `amount`      | REAL    | NOT NULL                           |
| `category`    | TEXT    | NOT NULL                           |
| `date`        | TEXT    | NOT NULL, `YYYY-MM-DD` format      |
| `description` | TEXT    | Nullable                           |
| `created_at`  | TEXT    | DEFAULT `datetime('now')`          |

### Foreign Key Relationship

```text
users.id
   │
   │ 1:N
   ▼
expenses.user_id
```

The database must enforce this relationship using a foreign key constraint.

---

## 5. Functions to Implement

All functions must be implemented in:

```text
database/db.py
```

### 5.1 `get_db()`

Open a SQLite connection to the application database.

The database file should be:

```text
spendly.db
```

or:

```text
expense_tracker.db
```

The database file must be located in the project root.

The connection must configure:

```python
connection.row_factory = sqlite3.Row
```

and enable foreign-key enforcement:

```sql
PRAGMA foreign_keys = ON
```

The function must return the active SQLite connection.

#### Expected behavior

`get_db()` must provide:

* SQLite database connection
* Dictionary-like row access through `sqlite3.Row`
* Foreign-key enforcement enabled on every connection

---

### 5.2 `init_db()`

Create the required database tables.

The function must:

* Create the `users` table.
* Create the `expenses` table.
* Use `CREATE TABLE IF NOT EXISTS`.
* Be safe to call multiple times.
* Not delete existing data.
* Ensure the schema is available before application routes are used.

#### Required behavior

Calling:

```python
init_db()
```

multiple times must not cause errors or duplicate tables.

---

### 5.3 `seed_db()`

Populate the database with initial demo data.

Before inserting anything, check whether the `users` table already contains data.

If users already exist:

```text
Return early.
```

Do not insert duplicate demo data.

#### Demo User

Insert exactly one demo user:

```text
Name: Demo User
Email: demo@spendly.com
Password: demo123
```

The password must **never be stored as plain text**.

Hash the password using `werkzeug.security`.

For example:

```python
from werkzeug.security import generate_password_hash
```

The stored value must be a password hash.

#### Sample Expenses

Insert **8 sample expenses**.

Requirements:

* All expenses must belong to the demo user.
* Use multiple categories.
* Dates must be within the current month.
* Dates must use `YYYY-MM-DD`.
* Every fixed category must have at least one expense.

---

## 6. Fixed Expense Categories

Only the following category values should be used for seeded expenses:

```text
Food
Transport
Bills
Health
Entertainment
Shopping
Other
```

There must be at least one seeded expense for each category.

Because there are 7 categories and 8 expenses, one category may contain two expenses.

---

## 7. Changes to `app.py`

Update:

```text
app.py
```

to import:

```python
get_db
init_db
seed_db
```

The application must initialize the database during startup.

The startup flow should ensure:

```text
Application starts
       ↓
Application context available
       ↓
init_db()
       ↓
seed_db()
       ↓
Routes become available
```

Use:

```python
with app.app_context():
    init_db()
    seed_db()
```

The existing placeholder routes must remain unchanged.

---

## 8. Files to Change

### `database/db.py`

Implement:

* `get_db()`
* `init_db()`
* `seed_db()`

### `app.py`

Add:

* Required imports
* Database initialization
* Database seeding during application startup

---

## 9. Files to Create

None.

The implementation must use the existing project structure.

---

## 10. Dependencies

No new Python packages are required.

Use:

### Python Standard Library

```python
sqlite3
```

### Existing Dependency

```python
werkzeug.security
```

Do not introduce an ORM or additional database package.

---

## 11. Implementation Rules

### 11.1 No ORM

Do not use:

```text
SQLAlchemy
Peewee
Django ORM
```

Use SQLite directly through Python's `sqlite3` module.

---

### 11.2 Parameterized Queries

All SQL queries involving dynamic values must use parameterized queries.

Correct:

```python
cursor.execute(
    "SELECT * FROM users WHERE email = ?",
    (email,)
)
```

Incorrect:

```python
cursor.execute(
    f"SELECT * FROM users WHERE email = '{email}'"
)
```

Never use string formatting, f-strings, or concatenation to insert values into SQL queries.

---

### 11.3 Foreign-Key Enforcement

Every database connection created by `get_db()` must execute:

```sql
PRAGMA foreign_keys = ON
```

Do not enable it only once globally.

---

### 11.4 Amount Storage

Expense amounts must be stored as:

```text
REAL
```

and represented as Python floating-point values.

Do not store expense amounts as integers.

---

### 11.5 Password Security

Passwords must be hashed using Werkzeug.

Use:

```python
generate_password_hash()
```

Never store:

```text
demo123
```

directly in `password_hash`.

---

### 11.6 Seed Protection

`seed_db()` must be idempotent.

Running:

```python
seed_db()
```

multiple times must not create duplicate users or expenses.

The existence of any user in the `users` table should cause the function to return without inserting demo data.

---

### 11.7 Date Format

All expense dates must follow:

```text
YYYY-MM-DD
```

Example:

```text
2026-09-03
2026-09-07
2026-09-10
```

Seeded dates must belong to the current month when the seed operation runs.

---

## 12. Expected Behavior

### `get_db()`

Must return a working SQLite connection with:

* `sqlite3.Row` row factory.
* Foreign-key enforcement enabled.

---

### `init_db()`

Must:

* Create `users`.
* Create `expenses`.
* Apply all required constraints.
* Be safe to execute repeatedly.
* Preserve existing data.

---

### `seed_db()`

Must:

* Check whether users already exist.
* Insert the demo user only when the database is empty.
* Store a hashed password.
* Insert 8 sample expenses.
* Associate all expenses with the demo user.
* Cover all 7 categories.
* Avoid duplicate seed data on subsequent runs.

---

### Database Constraints

The database must enforce:

**Unique email**

```text
users.email → UNIQUE
```

**Valid user relationship**

```text
expenses.user_id → users.id
```

**Required fields**

```text
users.name
users.email
users.password_hash

expenses.user_id
expenses.amount
expenses.category
expenses.date
```

must not accept `NULL`.

---

## 13. Error Handling Expectations

Database errors should not be silently swallowed.

### Duplicate Email

Attempting to insert an existing email must result in a SQLite `UNIQUE` constraint error.

Example:

```text
sqlite3.IntegrityError
```

---

### Invalid User ID

Attempting to insert an expense with a non-existent `user_id` must fail because of the foreign-key constraint.

Example:

```text
sqlite3.IntegrityError
```

---

### Invalid SQL

Invalid SQL queries should raise the appropriate SQLite error.

Do not hide database errors during development.

Errors should remain clear enough to diagnose the underlying problem.

---

## 14. Acceptance Criteria

The implementation is complete when all of the following are true:

* [ ] Database file is automatically created when the application starts.
* [ ] `users` table exists.
* [ ] `expenses` table exists.
* [ ] `users.id` is an autoincrementing primary key.
* [ ] `expenses.id` is an autoincrementing primary key.
* [ ] `users.email` has a UNIQUE constraint.
* [ ] `expenses.user_id` has a foreign-key relationship with `users.id`.
* [ ] Foreign-key enforcement is enabled.
* [ ] `amount` is stored as `REAL`.
* [ ] `created_at` defaults to `datetime('now')`.
* [ ] Demo user exists.
* [ ] Demo password is stored as a Werkzeug hash.
* [ ] Exactly 8 sample expenses are created during initial seeding.
* [ ] All 7 required categories are represented.
* [ ] Seed expense dates use `YYYY-MM-DD`.
* [ ] Seed expense dates belong to the current month.
* [ ] Running the application repeatedly does not duplicate seed data.
* [ ] `init_db()` can safely be called multiple times.
* [ ] Duplicate email insertion fails.
* [ ] Invalid foreign-key insertion fails.
* [ ] All dynamic SQL values use parameterized queries.
* [ ] No ORM is introduced.
* [ ] Application starts without errors.
* [ ] Existing routes remain unchanged.

---

## 15. Definition of Done

This specification is considered implemented when:

1. The application creates the SQLite database automatically on startup.
2. Both required tables are created with the correct schema and constraints.
3. Foreign-key enforcement is working.
4. The demo user exists with a securely hashed password.
5. Eight sample expenses exist across all required categories.
6. Seed data is not duplicated on repeated application starts.
7. All SQL queries use parameterized parameters where applicable.
8. No ORM or additional dependency is introduced.
9. The application starts successfully without breaking existing routes.
10. The database layer is ready for the next Spendly feature.
