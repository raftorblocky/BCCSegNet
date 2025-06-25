"""
camera_module.py
Handles Picamera2 initialization, capture, cropping, and mode settings.
"""
import time
import os
import numpy as np
import cv2
from datetime import datetime
from picamera2 import Picamera2

# Configuration constants
IMAGE_DIR = './images/raw'
CROP_SIZE = 1080
CROP_OFFSET_X = 60

# Initialize camera
picam = Picamera2()
config = picam.create_still_configuration()
picam.configure(config)
picam.start()
time.sleep(1)  # warm-up


def set_camera_mode(now: datetime) -> str:
    if 6 <= now.hour < 18:
        picam.set_controls({'AnalogueGain': 1.0, 'ExposureTime': 100})
        mode = 'day'
    else:
        picam.set_controls({'AnalogueGain': 2.0, 'ExposureTime': 1000000})
        mode = 'night'
    time.sleep(1)
    return mode


def capture_and_crop(now: datetime) -> str:
    date_folder = now.strftime('%Y%m%d')
    raw_dir = os.path.join(IMAGE_DIR, date_folder)
    os.makedirs(raw_dir, exist_ok=True)

    ts = now.strftime('%Y%m%d_%H%M%S')
    tmp_path = os.path.join(raw_dir, f"tmp_{ts}.jpg")
    picam.capture_file(tmp_path)

    img = cv2.imread(tmp_path)
    h, w = img.shape[:2]
    x0 = max(0, min((w - CROP_SIZE)//2 + CROP_OFFSET_X, w - CROP_SIZE))
    y0 = max(0, h//2 - CROP_SIZE//2)
    crop = img[y0:y0 + CROP_SIZE, x0:x0 + CROP_SIZE]

    # ===== Tambahkan circular mask =====
    mask = np.zeros((CROP_SIZE, CROP_SIZE), dtype=np.uint8)
    cv2.circle(mask, (CROP_SIZE // 2, CROP_SIZE // 2), CROP_SIZE // 2, 255, thickness=-1)
    crop = cv2.bitwise_and(crop, crop, mask=mask)
    # ===================================

    raw_path = os.path.join(raw_dir, f"raw_{ts}.jpg")
    cv2.imwrite(raw_path, crop)
    os.remove(tmp_path)
    return raw_path, ts