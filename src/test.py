"""
Batch test script for segmentation_module.py and utils.py
Resizes mask output back to original image size, draws ROI circle on mask
"""
import os
import cv2
from segmentation_module import segment_image
from utils import label_to_color, compute_cloud_cover, draw_roi_boundary

# Configuration
INPUT_DIR = './images/test'
OUTPUT_DIR = './images/test_segmented'
MODE = 'day'


def process_folder(input_dir: str, output_dir: str, mode: str):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Mode: {mode}, using default ROI radius")

    for fname in sorted(os.listdir(input_dir)):
        if not fname.lower().endswith(('.jpg', '.png', '.jpeg')):
            continue

        img_path = os.path.join(input_dir, fname)
        print(f"Processing {img_path}")

        # Read original image for resizing
        orig = cv2.imread(img_path)
        h, w = orig.shape[:2]

        # Perform segmentation
        label_mask, confidence = segment_image(img_path, mode)

        # Colorize mask
        color_mask = label_to_color(label_mask)
        # Resize mask back to original resolution
        color_resized = cv2.resize(color_mask, (w, h), interpolation=cv2.INTER_NEAREST)

        # Draw ROI boundary on resized mask
        overlay = draw_roi_boundary(color_resized)

        # Save mask and overlay
        base, _ = os.path.splitext(fname)
        mask_path = os.path.join(output_dir, f"{base}_mask.png")
        overlay_path = os.path.join(output_dir, f"{base}_mask_roi.png")
        cv2.imwrite(mask_path, cv2.cvtColor(color_resized, cv2.COLOR_RGB2BGR))
        cv2.imwrite(overlay_path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))

        # Compute and print cloud cover
        cover = compute_cloud_cover(label_mask)
        print(f" Cloud cover: {cover:.2f}%")

        # Print confidence
        if confidence is not None:
            print(f" Confidence: {confidence:.2f}%")
        else:
            print(" Confidence: n/a (threshold)")

        print(f" Saved mask: {mask_path}")
        print(f" Saved ROI overlay: {overlay_path}\n")

if __name__ == '__main__':
    process_folder(INPUT_DIR, OUTPUT_DIR, MODE)
    print("Done.")