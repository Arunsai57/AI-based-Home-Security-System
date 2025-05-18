import sqlite3

DB_PATH = 'database/database.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    #  tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            image_path TEXT,
            face_encoding TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_name TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            image_path TEXT
        )
    ''')

    c.execute('''
            CREATE TABLE IF NOT EXISTS object_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                object_name TEXT,
                confidence REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_path TEXT,
                category TEXT
            )
        ''')

    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
