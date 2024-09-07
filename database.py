# database.py

import sqlite3

def create_table():
    """Creates the uscis_info table if it doesn't exist."""

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uscis_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            source_url TEXT, 
            last_updated DATE
        );
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    """Establishes a connection to the SQLite database."""

    conn = sqlite3.connect('immigration.db')
    conn.row_factory = sqlite3.Row  
    return conn

if __name__ == "__main__":
    create_table()