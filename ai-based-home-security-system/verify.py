import sqlite3

conn = sqlite3.connect('database/database.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
