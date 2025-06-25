import os
from datetime import datetime
from picamera2 import Picamera2

# Inisialisasi kamera
picam = Picamera2()
config = picam.create_still_configuration()
picam.configure(config)

# ======== ATUR PARAMETER DI SINI ========
ISO_VALUE = 1.0                   # Contoh: 1.0 = ISO 100, 2.0 = ISO 200, 4.0 = ISO 400
EXPOSURE_MICROSECONDS = 100   # Contoh: 1.000.000 �s = 1 detik exposure
# =========================================

# Set pengaturan manual
picam.set_controls({
    "AnalogueGain": ISO_VALUE,
    "ExposureTime": EXPOSURE_MICROSECONDS
})

# Start kamera
picam.start()

# Buat folder output
now = datetime.now()
output_dir = "images/test"
os.makedirs(output_dir, exist_ok=True)

# Buat nama file
filename = now.strftime(f"test_{ISO_VALUE:.1f}ISO_{EXPOSURE_MICROSECONDS}us_%Y%m%d_%H%M%S.jpg")
filepath = os.path.join(output_dir, filename)

# Capture gambar
picam.capture_file(filepath)
print(f"Gambar disimpan di: {filepath}")

# Stop kamera
picam.stop()
