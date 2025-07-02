# utils.py
"""
utils.py
Color mapping, ROI generation, threshold features, and cloud cover computation.
"""
import numpy as np
import cv2

# Default ROI radius in pixels
default_ROI_RADIUS = 480

# RGB color map for labels
COLOR_MAP = {
    0: (255, 255, 255),  # cloud (white)
    1: (0, 0, 255),      # sky (blue)
    2: (0, 0, 0),        # undefined (black)
}

def label_to_color(mask: np.ndarray) -> np.ndarray:
    """Convert integer label mask to RGB image using COLOR_MAP."""
    h, w = mask.shape
    color = np.zeros((h, w, 3), dtype=np.uint8)
    for cls, col in COLOR_MAP.items():
        color[mask == cls] = col
    return color

def compute_cloud_cover(mask: np.ndarray, radius: int = None) -> float:
    """Calculate percentage of cloud (label 0) within a circular ROI."""
    h, w = mask.shape
    cx, cy = w // 2, h // 2
    if radius is None:
        radius = default_ROI_RADIUS if default_ROI_RADIUS is not None else min(cx, cy)
    Y, X = np.ogrid[:h, :w]
    roi = (X - cx) ** 2 + (Y - cy) ** 2 <= radius ** 2
    cloud = np.sum((mask == 0) & roi)
    total = np.sum(roi)
    return float(cloud) / total * 100

def draw_roi_boundary(image: np.ndarray,
                      color: tuple = (0, 255, 0),
                      thickness: int = 2,
                      radius: int = None) -> np.ndarray:
    """Draw a circular ROI boundary on an RGB image."""
    h, w = image.shape[:2]
    cx, cy = w // 2, h // 2
    if radius is None:
        radius = default_ROI_RADIUS if default_ROI_RADIUS is not None else min(cx, cy)
    img_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.circle(img_bgr, (cx, cy), radius, color, thickness)
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

def create_roi_mask(shape: tuple, radius: int = None) -> np.ndarray:
    """Generate a binary mask of a filled circle centered in an image."""
    h, w = shape[:2]
    cx, cy = w // 2, h // 2
    if radius is None:
        radius = default_ROI_RADIUS if default_ROI_RADIUS is not None else min(cx, cy)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, (cx, cy), radius, 255, thickness=-1)
    return mask

def compute_vd(img_bgr: np.ndarray) -> np.ndarray:
    """Feature array Vd = R - B for pre-check threshold."""
    B = img_bgr[:, :, 0].astype(np.float32)
    R = img_bgr[:, :, 2].astype(np.float32)
    return R - B

def mask_feature(arr: np.ndarray,
                 use_otsu: bool = True,
                 fixed_thr: float = 20) -> np.ndarray:
    """Create binary mask from feature array using Otsu or fixed threshold."""
    norm = cv2.normalize(arr, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    if use_otsu:
        _, m = cv2.threshold(norm, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        m = np.zeros_like(norm)
        m[norm > fixed_thr] = 255
    return m

def percent_to_okta(cloud_cover):
    """
    Konversi persentase cloud cover ke skala okta (0-8) sesuai tabel WMO.
    """
    if cloud_cover == 0:
        return 0
    elif 0 < cloud_cover < 18.75:
        return 1
    elif 18.75 <= cloud_cover < 31.25:
        return 2
    elif 31.25 <= cloud_cover < 43.75:
        return 3
    elif 43.75 <= cloud_cover < 56.25:
        return 4
    elif 56.25 <= cloud_cover < 68.75:
        return 5
    elif 68.75 <= cloud_cover < 81.25:
        return 6
    elif 81.25 <= cloud_cover < 100:
        return 7
    elif cloud_cover == 100:
        return 8
    else:
        return None  # untuk kasus tidak valid

def okta_to_sky_status(okta):
    """
    Konversi okta ke sky status string.
    """
    if okta == 0:
        return "Clear"
    elif 1 <= okta <= 2:
        return "Few"
    elif 3 <= okta <= 4:
        return "Scattered"
    elif 5 <= okta <= 7:
        return "Broken"
    elif okta == 8:
        return "Overcast"
    else:
        return "Unknown"