import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

cur.execute('''
CREATE TABLE observation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    okta INTEGER,
    status_langit TEXT,
    confidence REAL,
    timestamp TEXT,
    iso INTEGER,
    shutter_speed TEXT
)
''')

cur.execute('''
INSERT INTO observation (okta, status_langit, confidence, timestamp, iso, shutter_speed)
VALUES (3, 'Scattered (SCT)', 87.0, '2025-01-05 06:00:00', 1000, '1/2000')
''')

conn.commit()
conn.close()