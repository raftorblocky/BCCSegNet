import time
import os
from datetime import datetime
from picamera2 import Picamera2
import cv2
import numpy as np

# Inisialisasi kamera
picam = Picamera2()
config = picam.create_still_configuration()
picam.configure(config)
picam.start()
time.sleep(1.0)  # Biarkan kamera warm-up

# Path folder penyimpanan utama
IMAGE_DIR = "images/raw"
os.makedirs(IMAGE_DIR, exist_ok=True)

# Pengaturan manual untuk preprocessing
CROP_SIZE = 1080               # Ukuran square crop
CROP_OFFSET_X = 60              # Offset horizontal crop (positif ke kanan, negatif ke kiri)

print("Capture berjalan setiap 1 menit. Tekan Ctrl+C untuk berhenti.")

def set_camera_mode(now):
    hour = now.hour
    if hour >= 18 or hour < 6:
        # Mode malam
        print("Mode: Malam - ISO tinggi dan exposure lambat")
        picam.set_controls({
            "AnalogueGain": 4.0,
            "ExposureTime": 1_000_000
        })
    else:
        # Mode siang
        print("Mode: Siang - ISO rendah dan exposure cepat")
        picam.set_controls({
            "AnalogueGain": 1.0,
            "ExposureTime": 10_000
        })
    time.sleep(0.5)  # Biarkan kontrol manual aktif

try:
    while True:
        now = datetime.now()
        set_camera_mode(now)

        # Buat folder per tanggal
        date_folder = now.strftime("%Y%m%d")
        folder_path = os.path.join(IMAGE_DIR, date_folder)
        os.makedirs(folder_path, exist_ok=True)

        # Ambil gambar dan simpan file sementara
        temp_filename = now.strftime("tmp_%Y%m%d_%H%M%S.jpg")
        temp_path = os.path.join(folder_path, temp_filename)
        picam.capture_file(temp_path)
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Gambar asli disimpan: {temp_path}")

        # Preprocessing: crop dengan offset, lalu circular mask
        img = cv2.imread(temp_path)
        h, w = img.shape[:2]
        # Hitung titik awal crop dengan offset
        x0 = (w - CROP_SIZE) // 2 + CROP_OFFSET_X
        y0 = (h - CROP_SIZE) // 2
        # Boundary check
        x0 = max(0, min(x0, w - CROP_SIZE))
        y0 = max(0, min(y0, h - CROP_SIZE))
        crop = img[y0:y0 + CROP_SIZE, x0:x0 + CROP_SIZE]

        # Masking circular pada crop
        ch, cw = crop.shape[:2]
        center = (cw // 2, ch // 2)
        radius = min(cw, ch) // 2
        mask = np.zeros((ch, cw), dtype=np.uint8)
        cv2.circle(mask, center, radius, 255, thickness=-1)
        masked = cv2.bitwise_and(crop, crop, mask=mask)

        # Simpan hasil akhir dengan nama asli
        final_filename = now.strftime("raw_%Y%m%d_%H%M%S.jpg")
        final_path = os.path.join(folder_path, final_filename)
        cv2.imwrite(final_path, masked)
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Gambar diproses dan disimpan: {final_path}")

        # Hapus file sementara
        os.remove(temp_path)

        # Tunggu 1 menit
        time.sleep(10)

except KeyboardInterrupt:
    print("\nDihentikan oleh pengguna.")
finally:
    picam.stop()
