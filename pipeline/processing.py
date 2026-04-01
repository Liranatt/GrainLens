from dataclasses import dataclass
from typing import List, Tuple
import os

import cv2
import numpy as np
from scipy import ndimage as ndi
from skimage import color, img_as_ubyte
from skimage.feature import peak_local_max
from skimage.filters import gaussian, threshold_otsu
from skimage.measure import regionprops
from skimage.morphology import closing, remove_small_objects, square
from skimage.segmentation import mark_boundaries, watershed

from .calibrate import px_to_um2


@dataclass
class GrainResult:
    filename: str
    grain_count: int
    areas_px: List[float]
    areas_um2: List[float]
    perimeters_px: List[float]
    aspect_ratios: List[float]
    centroids: List[Tuple[float, float]]
    mean_area_um2: float
    std_area_um2: float
    d10_um2: float
    d50_um2: float
    d90_um2: float
    overlay_image: np.ndarray
    labeled_image: np.ndarray
    detection_quality: str = "unknown"


def load_image(path: str) -> np.ndarray | None:
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    return img.astype(np.float32) / 255.0


def crop_scale_bar(img: np.ndarray, crop_bottom_px: int = 60) -> np.ndarray:
    if crop_bottom_px <= 0:
        return img
    if img.shape[0] <= crop_bottom_px:
        return img
    return img[:-crop_bottom_px, :]


def preprocess(img: np.ndarray, blur_sigma: float = 1.5) -> np.ndarray:
    return gaussian(img, sigma=blur_sigma)


def segment_grains(
    img: np.ndarray,
    min_size: int = 50,
    min_distance: int = 10,
) -> np.ndarray:
    thresh = threshold_otsu(img)
    binary = img > thresh

    binary = closing(binary, square(3))
    binary = remove_small_objects(binary, min_size=min_size)

    distance = ndi.distance_transform_edt(binary)
    coords = peak_local_max(distance, min_distance=min_distance, labels=binary)

    mask = np.zeros(distance.shape, dtype=bool)
    if coords.size > 0:
        mask[tuple(coords.T)] = True

    markers, _ = ndi.label(mask)
    labels_ws = watershed(-distance, markers, mask=binary)
    return labels_ws


def measure_grains(
    labeled: np.ndarray,
    px_per_um: float,
) -> tuple[list, list, list, list, list]:
    props = regionprops(labeled)
    areas_px: list[float] = []
    areas_um2: list[float] = []
    perims: list[float] = []
    aspects: list[float] = []
    centroids: list[tuple[float, float]] = []

    for p in props:
        if p.area < 30:
            continue
        areas_px.append(float(p.area))
        areas_um2.append(float(px_to_um2(float(p.area), px_per_um)))
        perims.append(float(p.perimeter))
        minor = p.minor_axis_length or 1.0
        aspects.append(float(p.major_axis_length / minor))
        centroids.append((float(p.centroid[0]), float(p.centroid[1])))

    return areas_px, areas_um2, perims, aspects, centroids


def create_overlay(original: np.ndarray, labeled: np.ndarray) -> np.ndarray:
    rgb = color.gray2rgb(original)
    overlay = mark_boundaries(rgb, labeled, color=(1, 0.2, 0.1), mode="thick")
    return img_as_ubyte(overlay)


def detect_grains(
    path: str,
    px_per_um: float,
    blur_sigma: float = 1.5,
    crop_bottom: int = 60,
) -> GrainResult | None:
    img = load_image(path)
    if img is None:
        print(f"[SKIP] cannot load {path}")
        return None

    img_c = crop_scale_bar(img, crop_bottom)
    img_p = preprocess(img_c, blur_sigma)
    labeled = segment_grains(img_p)

    areas_px, areas_um2, perims, aspects, centroids = measure_grains(labeled, px_per_um)
    if not areas_um2:
        print(f"[WARN] no grains in {path}")
        return None

    overlay = create_overlay(img_c, labeled)
    return GrainResult(
        filename=os.path.basename(path),
        grain_count=len(areas_px),
        areas_px=areas_px,
        areas_um2=areas_um2,
        perimeters_px=perims,
        aspect_ratios=aspects,
        centroids=centroids,
        mean_area_um2=float(np.mean(areas_um2)),
        std_area_um2=float(np.std(areas_um2)),
        d10_um2=float(np.percentile(areas_um2, 10)),
        d50_um2=float(np.percentile(areas_um2, 50)),
        d90_um2=float(np.percentile(areas_um2, 90)),
        overlay_image=overlay,
        labeled_image=labeled,
    )
