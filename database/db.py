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
