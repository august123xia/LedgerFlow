
import sqlite3
from app_sqlite import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            amount REAL,
            status TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("LedgerFlow database initialized successfully!")


if __name__ == "__main__":
    init_db()
