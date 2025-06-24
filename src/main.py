import os
import time
import json
import threading
from datetime import datetime, timezone
import cv2
import requests
from camera_module import set_camera_mode, capture_and_crop
from segmentation_module import segment_image
from utils import (
    label_to_color, compute_cloud_cover, draw_roi_boundary,
    percent_to_okta, okta_to_sky_status
)

SEG_ROOT = './images/segmented'
RAW_ROOT = './images/raw'
CAPTURE_INTERVAL_MIN = 10  # 10 minutes
LOG_PATH = "unsent_logs.jsonl"
API_URL = "https://cc.blockynet.site/insertdb.php"

# === LOGGING FUNCTIONS ===
def save_log_locally(data, path=LOG_PATH):
    with open(path, "a") as f:
        f.write(json.dumps(data) + "\n")

def send_to_db(data, url=API_URL, log_path=LOG_PATH):
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print("Data sent successfully")
            return True
        else:
            print(f"Failed to send data, status: {response.status_code}")
            if log_path: save_log_locally(data, log_path)
            return False
    except Exception as e:
        print(f"Error sending data: {e}")
        if log_path: save_log_locally(data, log_path)
        return False

def resend_unsent_logs(url=API_URL, log_path=LOG_PATH):
    while True:
        if not os.path.exists(log_path):
            time.sleep(120)
            continue
        new_lines = []
        with open(log_path, "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if send_to_db(data, url, log_path=None):
                        continue  # Sent successfully, skip writing back
                    else:
                        new_lines.append(line)
                except Exception as e:
                    print(f"Malformed log line: {e}")
        with open(log_path, "w") as f:
            f.writelines(new_lines)
        time.sleep(120)  # Sleep 2 menit sebelum cek lagi

def upload_raw_image(raw_path, upload_url="https://cc.blockynet.site/uploadimg.php"):
    try:
        # Pakai nama file fixed 'latest_capture.jpg'
        with open(raw_path, "rb") as imgf:
            files = {"image": ("latest_capture.jpg", imgf, "image/jpeg")}
            response = requests.post(upload_url, files=files, timeout=10)
        if response.status_code == 200 and "Upload berhasil" in response.text:
            print(f"Raw image uploaded as latest_capture.jpg")
            return True
        else:
            print(f"Failed to upload image: {response.text}")
            return False
    except Exception as e:
        print(f"Exception during upload: {e}")
        return False

def main():
    now_local_init = datetime.now().astimezone()
    mode_init = set_camera_mode(now_local_init)
    print(f"Camera controls set for initial mode: {mode_init}")

    os.makedirs(SEG_ROOT, exist_ok=True)
    print("Scheduled capture every UTC 10-minute mark; segmentation every UTC 30-minute mark.")

    last_capture_min = None
    last_seg_hour = None
    last_raw_path = None
    last_ts = None
    
    threading.Thread(target=resend_unsent_logs, daemon=True).start()

    try:
        while True:

            now_utc = datetime.now(timezone.utc)
            minute = now_utc.minute
            now_local = now_utc.astimezone()

            # Capture pada setiap menit kelipatan 10 
            if minute % 10 == 0 and minute != last_capture_min:
                last_capture_min = minute

                raw_path, ts = capture_and_crop(now_local)
                last_raw_path = raw_path
                last_ts = ts
                print(f"Captured image at {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')} local ({now_utc.strftime('%H:%M UTC')})")

                # Segmentasi pada menit 0 dan 30 UTC
                if minute in (0, 30) and (last_seg_hour != (now_utc.hour, minute)):
                    last_seg_hour = (now_utc.hour, minute)
                    mode = set_camera_mode(now_local)
                    date_str = now_local.strftime('%Y%m%d')
                    seg_dir = os.path.join(SEG_ROOT, date_str)
                    os.makedirs(seg_dir, exist_ok=True)

                    # Segmentasi (tanpa confidence)
                    label_mask = segment_image(last_raw_path, mode)
                    color_mask = label_to_color(label_mask)
                    overlay = draw_roi_boundary(color_mask)
                    seg_path = os.path.join(seg_dir, f"seg_{last_ts}.png")
                    cv2.imwrite(seg_path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))

                    cover = compute_cloud_cover(label_mask)
                    okta = percent_to_okta(cover)
                    sky_status = okta_to_sky_status(okta)
                    msg = f"[{mode.upper()}][{now_local.strftime('%H:%M %Z')}]: Cloud cover={cover:.2f}%"
                    print(msg)

                    # === Data ready for DB/API ===
                    if mode == 'day':
                        shutter_speed = "1/1000s" #configurable
                        iso = "100" #configurable
                    else:
                        shutter_speed = "1/10s" #configurable
                        iso = "400" #configurable
                    # Compose data payload
                    db_data = {
                        "file_path": raw_path,
                        "latitude": -7.145,    #configurable
                        "longitude": 112.510,  #configurable
                        "altitude": 30,        #configurable
                        "camera_model": "Arducam B0425 Lens Moded",
                        "resolution": "1080x1080",
                        "aperture": "f/2.2",
                        "focal_length": 1.1,
                        "shutter_speed": shutter_speed,
                        "iso": iso,
                        "cloud_cover": round(cover, 2),
                        "cloud_okta": okta,
                        "sky_status": sky_status
                    }
                    # Attempt to send, log if fail
                    send_to_db(db_data)
                    upload_raw_image(last_raw_path)
            time.sleep(30)
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting.")
    finally:
        from picamera2 import Picamera2
        Picamera2().stop()

if __name__ == '__main__':
    main()