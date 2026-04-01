import json
from pathlib import Path

import numpy as np
from PIL import Image

from .processing import GrainResult

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = PROJECT_ROOT / "docs" / "data" / "results"
IMAGE_DIR = PROJECT_ROOT / "docs" / "data" / "images"


def save_result(result: GrainResult) -> dict:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    stem = Path(result.filename).stem
    overlay_rel = f"data/images/{stem}_overlay.png"
    overlay_path = IMAGE_DIR / f"{stem}_overlay.png"
    Image.fromarray(result.overlay_image).save(overlay_path)

    data = {
        "filename": result.filename,
        "grain_count": result.grain_count,
        "mean_area_um2": round(result.mean_area_um2, 2),
        "std_area_um2": round(result.std_area_um2, 2),
        "d10_um2": round(result.d10_um2, 2),
        "d50_um2": round(result.d50_um2, 2),
        "d90_um2": round(result.d90_um2, 2),
        "aspect_ratio_mean": round(float(np.mean(result.aspect_ratios)), 3),
        "areas_um2": [round(a, 2) for a in result.areas_um2],
        "overlay_path": overlay_rel,
        "detection_quality": result.detection_quality,
    }

    json_path = RESULT_DIR / f"{stem}.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data
