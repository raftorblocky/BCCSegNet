import requests

url = "https://cc.blockynet.site/insertdb.php"

db_data = {
    "file_path": "/images/raw/20240701/raw_20240701_130000.jpg",
    "latitude": -7.145,
    "longitude": 112.510,
    "altitude": 30,
    "camera_model": "Arducam B0425 Lens Moded",
    "resolution": "1080x1080",
    "aperture": "f/2.2",
    "focal_length": 1.1,
    "shutter_speed": "1/1000s",  # contoh, sesuaikan kebutuhan
    "iso": "100",                # contoh, sesuaikan kebutuhan
    "cloud_cover": 62.37,        # contoh hasil dari utils
    "cloud_okta": 5,             # hasil dari percent_to_okta
    "sky_status": "Mostly Cloudy" # hasil dari okta_to_sky_status
}

response = requests.post(url, json=db_data)
print("Status code:", response.status_code)
print("Response:", response.text)
