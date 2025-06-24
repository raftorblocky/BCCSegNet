# test.py
"""
Batch test script for segmentation_module.py and utils.py
"""
import os
import cv2
from segmentation_module import segment_image
from utils import label_to_color, compute_cloud_cover, draw_roi_boundary

# Configuration
INPUT_DIR = './images/test'
OUTPUT_DIR = './images/test_segmented'
MODE = 'day'
ROI_RADIUS = 210


def process_folder(input_dir, output_dir, mode, roi_radius):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Mode: {mode}, ROI radius: {roi_radius or 'default'}")
    for fname in sorted(os.listdir(input_dir)):
        if not fname.lower().endswith(('.jpg','.png','.jpeg')):
            continue
        path = os.path.join(input_dir, fname)
        print(f"Processing {path}")
        label_mask, conf = segment_image(path, mode)
        color = label_to_color(label_mask)
        # save mask
        mpath = os.path.join(output_dir, f"{os.path.splitext(fname)[0]}_mask.png")
        cv2.imwrite(mpath, cv2.cvtColor(color,cv2.COLOR_RGB2BGR))
        # cover & conf
        cover = compute_cloud_cover(label_mask, radius=roi_radius)
        print(f" Cloud cover: {cover:.2f}%")
        print(f" Confidence : {conf:.2f}%" if conf is not None else " Confidence : n/a")
        # overlay
        viz = draw_roi_boundary(color, radius=roi_radius)
        vpath = os.path.join(output_dir, f"{os.path.splitext(fname)[0]}_roi.png")
        cv2.imwrite(vpath, cv2.cvtColor(viz,cv2.COLOR_RGB2BGR))
        print(f" Saved ROI overlay: {vpath}\n")

if __name__=='__main__':
    process_folder(INPUT_DIR, OUTPUT_DIR, MODE, ROI_RADIUS)
    print("Done.")