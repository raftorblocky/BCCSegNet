import os
import time
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from datetime import datetime
from picamera2 import Picamera2

# --- CONFIGURATION ---
IMAGE_DIR = './images/raw'
SEG_ROOT = './images/segmented'
MODEL_DAY_PATH = './model/model_day.tflite'
MODEL_NIGHT_PATH = './model/model_night.tflite'
CAPTURE_INTERVAL = 60  # seconds
CROP_SIZE = 1080  # crop square size
CROP_OFFSET_X = 60  # horizontal offset for crop

# --- INITIALIZE CAMERA ---
picam = Picamera2()
config = picam.create_still_configuration()
picam.configure(config)
picam.start()
time.sleep(1)  # warm-up

# --- LOAD TFLITE MODELS ---
interp_day = tflite.Interpreter(model_path=MODEL_DAY_PATH)
interp_day.allocate_tensors()
inp_day = interp_day.get_input_details()[0]
out_day = interp_day.get_output_details()[0]
_, D_H, D_W, D_C = inp_day['shape']

interp_night = tflite.Interpreter(model_path=MODEL_NIGHT_PATH)
interp_night.allocate_tensors()
inp_night = interp_night.get_input_details()[0]
out_night = interp_night.get_output_details()[0]
_, N_H, N_W, N_C = inp_night['shape']

# --- COLOR MAP (RGB) ---
COLOR_MAP = {
    0: (255, 255, 255),  # white
    1: (0, 0, 255),      # blue
    2: (0, 0, 0),        # black
}

# --- HELPER FUNCTIONS ---
def set_camera_mode(now):
    hour = now.hour
    if 6 <= hour < 18:
        picam.set_controls({'AnalogueGain': 1.0, 'ExposureTime': 10000})
        mode = 'day'
    else:
        picam.set_controls({'AnalogueGain': 4.0, 'ExposureTime': 1000000})
        mode = 'night'
    # allow controls to take effect
    time.sleep(0.5)
    return mode


def segment_image(raw_path, mode):
    if mode == 'day':
        interp = interp_day
        inp_det = inp_day
        out_det = out_day
        TW, TH = D_W, D_H
    else:
        interp = interp_night
        inp_det = inp_night
        out_det = out_night
        TW, TH = N_W, N_H

    img = cv2.imread(raw_path)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(rgb, (TW, TH), interpolation=cv2.INTER_LINEAR)
    inp = np.expand_dims(resized.astype(np.float32) / 255.0, axis=0)

    interp.set_tensor(inp_det['index'], inp)
    interp.invoke()
    out = interp.get_tensor(out_det['index'])

    mask = np.argmax(np.squeeze(out), axis=-1).astype(np.uint8)
    h_m, w_m = mask.shape
    color_mask = np.zeros((h_m, w_m, 3), dtype=np.uint8)
    for cls, rgb_val in COLOR_MAP.items():
        color_mask[mask == cls] = rgb_val
    return color_mask

# --- MAIN LOOP ---
print(f"Starting capture, crop, and segmentation every {CAPTURE_INTERVAL}s")
try:
    while True:
        now = datetime.now()
        mode = set_camera_mode(now)

        date_str = now.strftime('%Y%m%d')
        raw_dir = os.path.join(IMAGE_DIR, date_str)
        seg_dir = os.path.join(SEG_ROOT, date_str)
        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(seg_dir, exist_ok=True)

        ts = now.strftime('%Y%m%d_%H%M%S')

        # Capture to temp file
        tmp_path = os.path.join(raw_dir, f"tmp_{ts}.jpg")
        picam.capture_file(tmp_path)

        # Crop and save raw image
        img = cv2.imread(tmp_path)
        h, w = img.shape[:2]
        x0 = max(0, min((w - CROP_SIZE) // 2 + CROP_OFFSET_X, w - CROP_SIZE))
        y0 = max(0, h // 2 - CROP_SIZE // 2)
        crop = img[y0:y0 + CROP_SIZE, x0:x0 + CROP_SIZE]
        raw_path = os.path.join(raw_dir, f"raw_{ts}.jpg")
        cv2.imwrite(raw_path, crop)
        print(f"[{mode}] Raw saved: {raw_path}")

        # Remove temp file
        os.remove(tmp_path)

        # Segment and save
        seg_mask = segment_image(raw_path, mode)
        seg_path = os.path.join(seg_dir, f"seg_{ts}.png")
        cv2.imwrite(seg_path, cv2.cvtColor(seg_mask, cv2.COLOR_RGB2BGR))
        print(f"[{mode}] Seg saved: {seg_path}")

        time.sleep(CAPTURE_INTERVAL)
except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    picam.stop()
