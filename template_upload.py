import requests
import random
from datetime import datetime

url = "https://cc.blockynet.site/insertdb.php"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
file_path = f"static/img/capture_{timestamp}.jpg"

data = {
    "file_path": file_path,
    "latitude": round(random.uniform(-7.150, -7.140), 6),
    "longitude": round(random.uniform(112.500, 112.520), 6),
    "altitude": random.randint(10, 50),
    "camera_model": random.choice(["Arducam B0425", "Raspberry Pi HQ Cam"]),
    "resolution": random.choice(["1080x1080", "1024x1024", "720x720"]),
    "aperture": random.choice(["f/1.8", "f/2.2", "f/2.8"]),
    "focal_length": round(random.uniform(1.0, 2.0), 2),
    "shutter_speed": random.choice(["1/500s", "1/1000s", "1/2000s"]),
    "iso": random.choice(["100", "200", "400"]),
    "cloud_cover": round(random.uniform(0, 100), 2),
    "cloud_okta": random.randint(0, 8),
    "sky_status": random.choice(["Clear", "Partly Cloudy", "Mostly Cloudy", "Overcast"]),
    "confidence_score": round(random.uniform(80, 100), 2)
}

response = requests.post(url, json=data)

print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("Status code:", response.status_code)
print("Response:", response.text)
