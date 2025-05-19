import sqlite3

conn = sqlite3.connect("cloud_cover.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cloud_cover TEXT,
    sky_condition TEXT,
    confidence_score INTEGER,
    image_path TEXT,
    shutter_speed TEXT,
    iso TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
