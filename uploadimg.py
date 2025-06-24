import requests

url = "https://cc.blockynet.site/uploadimg.php"
file_path = "latest_capture.jpg"

with open(file_path, "rb") as f:
    files = {"image": f}
    response = requests.post(url, files=files)

print(response.text)