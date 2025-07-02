import numpy as np
import cv2
import tflite_runtime.interpreter as tflite
from utils import compute_vd, mask_feature, create_roi_mask

MODEL_DAY_PATH = './model/model_day.tflite'
MODEL_NIGHT_PATH = './model/model_night.tflite'

ROI_BIG_RADIUS = 480
ROI_SMALL_RADIUS = 300
FALLBACK_UNDEF_MIN_COUNT = 100
KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

def _load_interpreter(path: str):
    interp = tflite.Interpreter(model_path=path)
    interp.allocate_tensors()
    return interp, interp.get_input_details()[0], interp.get_output_details()[0]

_interp_day, inp_day, out_day = _load_interpreter(MODEL_DAY_PATH)
_interp_night, inp_night, out_night = _load_interpreter(MODEL_NIGHT_PATH)
_, D_H, D_W, _ = inp_day['shape']
_, N_H, N_W, _ = inp_night['shape']

def segment_image(image_path: str, mode: str = 'day') -> np.ndarray:
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    h_full, w_full = img.shape[:2]
    roi_big_full = create_roi_mask(img.shape, ROI_BIG_RADIUS)
    roi_small_full = create_roi_mask(img.shape, ROI_SMALL_RADIUS)

    if mode == 'day':
        interp, inp_i, out_i, TW, TH = _interp_day, inp_day, out_day, D_W, D_H
    else:
        interp, inp_i, out_i, TW, TH = _interp_night, inp_night, out_night, N_W, N_H

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    inp_buf = cv2.resize(rgb, (TW, TH)).astype(np.float32) / 255.0
    inp_buf = np.expand_dims(inp_buf, 0)
    interp.set_tensor(inp_i['index'], inp_buf)
    interp.invoke()
    out = interp.get_tensor(out_i['index'])[0]
    label_model = np.argmax(out, axis=-1).astype(np.uint8)
    Hm, Wm = label_model.shape

    roi_big = cv2.resize(roi_big_full, (Wm, Hm), interpolation=cv2.INTER_NEAREST)
    roi_small = cv2.resize(roi_small_full, (Wm, Hm), interpolation=cv2.INTER_NEAREST)

    if mode != 'day':
        label_full = cv2.resize(label_model, (w_full, h_full), interpolation=cv2.INTER_NEAREST)
        return label_full

    undef_mask = (label_model == 2).astype(np.uint8) * 255
    undef_mask = cv2.morphologyEx(undef_mask, cv2.MORPH_OPEN, KERNEL)
    undef_mask = cv2.morphologyEx(undef_mask, cv2.MORPH_CLOSE, KERNEL)
    num_undef = int(np.count_nonzero((undef_mask == 255) & (roi_small == 255)))

    if num_undef >= FALLBACK_UNDEF_MIN_COUNT:
        vd = compute_vd(img)
        mask_vd = mask_feature(vd)
        mask_vd = cv2.morphologyEx(mask_vd, cv2.MORPH_OPEN, KERNEL)
        mask_vd = cv2.morphologyEx(mask_vd, cv2.MORPH_CLOSE, KERNEL)
        valid_mask = (cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) > 10)
        label_thresh_full = np.full((h_full, w_full), 2, dtype=np.uint8)
        label_thresh_full[(valid_mask) & (mask_vd == 255)] = 0
        label_thresh_full[(valid_mask) & (mask_vd == 0)] = 1
        return label_thresh_full

    label_full = cv2.resize(label_model, (w_full, h_full), interpolation=cv2.INTER_NEAREST)
    return label_full