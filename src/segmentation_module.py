# segmentation_module.py
"""
segmentation_module.py
Performs Vd pre-check and TFLite inference to produce label masks and confidence.
"""
import numpy as np
import cv2
import tflite_runtime.interpreter as tflite
from utils import compute_vd, mask_feature, create_roi_mask, compute_cloud_cover

MODEL_DAY_PATH = './model/model_day.tflite'
MODEL_NIGHT_PATH = './model/model_night.tflite'

CLOUD_COVER_THRESHOLD = 60.0   # percent
BRIGHTNESS_THRESHOLD = 160.0   # detects overcast brightness


def _load_interpreter(path: str):
    interp = tflite.Interpreter(model_path=path)
    interp.allocate_tensors()
    return interp, interp.get_input_details()[0], interp.get_output_details()[0]

_interp_day, inp_day, out_day = _load_interpreter(MODEL_DAY_PATH)
_interp_night, inp_night, out_night = _load_interpreter(MODEL_NIGHT_PATH)
_, D_H, D_W, _ = inp_day['shape']
_, N_H, N_W, _ = inp_night['shape']


def segment_image(image_path: str, mode: str = 'day') -> tuple:
    """
    Returns (label_mask, confidence).
    confidence: average max-softmax over ROI (%) or None if threshold branch.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    roi_mask = create_roi_mask(img.shape)

    if mode == 'day':
        # Pre-check
        vd = compute_vd(img)
        mask_vd = mask_feature(vd)
        mask_vd = cv2.bitwise_and(mask_vd, mask_vd, mask=roi_mask)
        cov = np.count_nonzero(mask_vd) / max(np.count_nonzero(roi_mask),1) *100
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mean_b = np.mean(gray[roi_mask==255])
        print(f"[pre-check] cover={cov:.1f}%, brightness={mean_b:.1f}")
        if cov <= CLOUD_COVER_THRESHOLD and mean_b < BRIGHTNESS_THRESHOLD:
            label = np.full(mask_vd.shape, 2, dtype=np.uint8)
            inside = roi_mask==255
            label[inside & (mask_vd==255)] = 0
            label[inside & (mask_vd==0)] = 1
            return label, None
        interp, inp_det, out_det, TW, TH = _interp_day, inp_day, out_day, D_W, D_H
    else:
        interp, inp_det, out_det, TW, TH = _interp_night, inp_night, out_night, N_W, N_H

    # Inference
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    inp = cv2.resize(rgb, (TW, TH)).astype(np.float32)/255.0
    inp = np.expand_dims(inp,0)
    interp.set_tensor(inp_det['index'], inp)
    interp.invoke()
    out = interp.get_tensor(out_det['index'])[0]
    label_mask = np.argmax(out, axis=-1).astype(np.uint8)

    # Confidence
    if label_mask.shape != roi_mask.shape:
        roi_small = cv2.resize(roi_mask,(label_mask.shape[1],label_mask.shape[0]),cv2.INTER_NEAREST)
    else:
        roi_small = roi_mask
    maxp = np.max(out,axis=-1)
    conf = np.mean(maxp[roi_small==255])*100
    return label_mask, conf