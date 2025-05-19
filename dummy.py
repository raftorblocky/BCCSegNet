import sqlite3
import random
import time
from datetime import datetime

def insert_dummy_data():
    conn = sqlite3.connect("cloud_cover.db")
    c = conn.cursor()

    cloud_cover = random.choice(["1 oktas", "3 oktas", "6 oktas", "8 oktas"])
    sky_condition = random.choice(["Clear (CLR)", "Few (FEW)", "Scattered (SCT)", "Broken (BKN)", "Overcast (OVC)"])
    confidence_score = random.randint(60, 99)
    image_path = "static/img/latest_capture.jpg"
    shutter_speed = random.choice(["1/100", "1/250", "1/500"])
    iso = random.choice(["100", "200", "400"])

    c.execute("""
    INSERT INTO observations (cloud_cover, sky_condition, confidence_score, image_path, shutter_speed, iso)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (cloud_cover, sky_condition, confidence_score, image_path, shutter_speed, iso))

    conn.commit()
    conn.close()
    print(f"Inserted at {datetime.now()}")

# Loop setiap 5 detik
if __name__ == "__main__":
    while True:
        insert_dummy_data()
        time.sleep(5)