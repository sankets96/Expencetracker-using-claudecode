import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

DATABASE = "expense_tracker.db"

def get_db():
    """
    Opens a SQLite connection to the application database.
    Configures row_factory = sqlite3.Row and enables foreign-key enforcement.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """
    Creates the required database tables (users and expenses) if they do not exist.
    """
    with get_db() as conn:
        # Create users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        # Create expenses table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()

def seed_db():
    """
    Populates the database with initial demo data if it is empty.
    """
    with get_db() as conn:
        # Idempotency check: return early if users already exist
        cursor = conn.execute("SELECT 1 FROM users LIMIT 1")
        if cursor.fetchone():
            return

        # Demo User
        demo_password_hash = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", demo_password_hash)
        )
        user_id = cursor.lastrowid

        # Sample Expenses
        # Categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
        current_month = datetime.now().strftime("%Y-%m")

        expenses = [
            (user_id, 15.50, 'Food', f"{current_month}-01", "Lunch at Cafe"),
            (user_id, 30.00, 'Transport', f"{current_month}-02", "Gas refill"),
            (user_id, 120.00, 'Bills', f"{current_month}-03", "Monthly Internet"),
            (user_id, 45.00, 'Health', f"{current_month}-04", "Pharmacy"),
            (user_id, 20.00, 'Entertainment', f"{current_month}-05", "Movie ticket"),
            (user_id, 65.00, 'Shopping', f"{current_month}-06", "New T-shirt"),
            (user_id, 12.00, 'Other', f"{current_month}-07", "Parking fee"),
            (user_id, 22.00, 'Food', f"{current_month}-08", "Dinner"),
        ]

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()

def create_user(name, email, password_hash):
    """
    Creates a new user in the database.
    Returns True if successful, False if the email already exists (IntegrityError).
    """
    conn = get_db()
    try:
        with conn:
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_email(email):
    """
    Retrieves a user by their email address.
    Returns a sqlite3.Row object or None if not found.
    """
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()

def get_expenses_by_user(user_id):
    """
    Retrieves all expenses for a given user, ordered by date descending.
    """
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC", (user_id,)
        ).fetchall()
    finally:
        conn.close()

def create_expense(user_id, amount, category, date, description):
    """
    Adds a new expense record to the database.
    """
    conn = get_db()
    try:
        with conn:
            conn.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                (user_id, amount, category, date, description)
            )
    finally:
        conn.close()

def get_expense_by_id(expense_id, user_id):
    """
    Retrieves a specific expense by ID, ensuring it belongs to the given user.
    """
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id)
        ).fetchone()
    finally:
        conn.close()

def update_expense(expense_id, user_id, amount, category, date, description):
    """
    Updates an existing expense record for a specific user.
    """
    conn = get_db()
    try:
        with conn:
            conn.execute(
                "UPDATE expenses SET amount = ?, category = ?, date = ?, description = ? WHERE id = ? AND user_id = ?",
                (amount, category, date, description, expense_id, user_id)
            )
    finally:
        conn.close()

def delete_expense(expense_id, user_id):
    """
    Deletes an expense record for a specific user.
    """
    conn = get_db()
    try:
        with conn:
            conn.execute(
                "DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id)
            )
    finally:
        conn.close()
