"""
main.py
Coordinates capture, segmentation, ROI visualization, saving, and logging.
"""
import os
import time
from datetime import datetime
import cv2
from camera_module import set_camera_mode, capture_and_crop
from segmentation_module import segment_image
from utils import label_to_color, compute_cloud_cover, draw_roi_boundary

SEG_ROOT = './images/segmented'
CAP_INTERVAL = 60

print("Starting main loop with ROI boundary...")
try:
    while True:
        now = datetime.now()
        mode = set_camera_mode(now)
        raw_path = capture_and_crop(now)

        date_str = now.strftime('%Y%m%d')
        seg_dir = os.path.join(SEG_ROOT, date_str)
        os.makedirs(seg_dir, exist_ok=True)

        # Segmentation
        label_mask = segment_image(raw_path, mode)
        color_mask = label_to_color(label_mask)

        # Draw ROI boundary
        color_mask = draw_roi_boundary(color_mask)

        ts = now.strftime('%Y%m%d_%H%M%S')
        seg_path = os.path.join(seg_dir, f"seg_{ts}.png")
        # Save as BGR
        cv2.imwrite(seg_path, cv2.cvtColor(color_mask, cv2.COLOR_RGB2BGR))

        # Compute and log cloud cover
        cover = compute_cloud_cover(label_mask)
        print(f"[{mode}] {ts}: Seg saved with ROI, Cloud cover = {cover:.2f}%")

        time.sleep(CAP_INTERVAL)
except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    from picamera2 import Picamera2
    Picamera2().stop()
