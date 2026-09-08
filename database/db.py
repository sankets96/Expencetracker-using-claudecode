import sqlite3
from flask import g

DATABASE = "database.db"

def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def init_db():
    """Creates all tables using CREATE TABLE IF NOT EXISTS."""
    db = sqlite3.connect(DATABASE)

    # Users table
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Expenses table
    db.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    db.commit()
    db.close()
    print("Database initialized successfully.")

def seed_db():
    """Inserts sample data for development."""
    db = sqlite3.connect(DATABASE)

    # Seed users (passwords would normally be hashed)
    users = [
        ('Alice Smith', 'alice@example.com', 'password123'),
        ('Bob Jones', 'bob@example.com', 'securepass456')
    ]
    db.executemany("INSERT OR IGNORE INTO users (full_name, email, password) VALUES (?, ?, ?)", users)

    # Get user IDs for seeding expenses
    cursor = db.execute("SELECT id, email FROM users")
    user_map = {row[1]: row[0] for row in cursor.fetchall()}

    # Seed expenses
    expenses = [
        (user_map['alice@example.com'], 50.0, 'Food', '2023-10-01', 'Grocery shopping'),
        (user_map['bob@example.com'], 100.0, 'Utilities', '2023-10-01', 'Electricity bill'),
    ]
    db.executemany("INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)", expenses)

    db.commit()
    db.close()
    print("Database seeded successfully.")

if __name__ == "__main__":
    init_db()
    seed_db()
