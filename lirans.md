# Liran – Technical Plan

This file is your personal checklist for the technical side of the project.  
It assumes: Python + basic web (HTML/CSS/JS), no backend, deployed via GitHub Pages.

High‑level architecture:

- **Local Python pipeline** (`pipeline/`):  
  Load SEM images → segment → measure → write JSON + PNG overlays into `docs/data/`.
- **Static site** (`docs/`):  
  One HTML page + JS that reads those JSON files and shows images, charts, and case‑study text.

Linoy never has to touch any of this. She edits only content files (CSV/JSON/Markdown), mainly via GitHub’s web UI.

---

## 0. Repo & folders

Create a new public repo, e.g. `grainlens`, then locally:

```bash
git clone https://github.com/<username>/grainlens.git
cd grainlens

mkdir -p docs/css docs/js docs/data/results docs/data/images
mkdir -p pipeline raw_data
echo "raw_data/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
```

Later, in GitHub settings:

- Pages → Source: `Deploy from a branch`
- Branch: `main`, folder: `/docs`

The site will be at: `https://<username>.github.io/grainlens`.

---

## 1. Python environment & dataset

### 1.1 Requirements

Create `pipeline/requirements.txt`:

```text
opencv-python
scikit-image
numpy
pandas
scipy
Pillow
tqdm
```

Install in your venv:

```bash
cd pipeline
pip install -r requirements.txt
```

### 1.2 UHCS dataset (or another SEM set)

Manually download an SEM microstructure dataset into `raw_data/`. For UHCS:

- Clone or download the `micrographs/` and metadata into `raw_data/uhcs/`.
- Minimal assumption: there is a folder with image files you can glob.

Keep paths flexible so you can swap to a different dataset later.

---

## 2. Core processing pipeline

Goal: given an image path → return a `GrainResult` containing:

- labeled segmentation,
- per‑grain areas, aspect ratios, centroids,
- summary stats (mean, std, percentiles),
- overlay image (original + colored boundaries).

### 2.1 Data structures

In `pipeline/processing.py`:

```python
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

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
    overlay_image: np.ndarray        # uint8 RGB
    labeled_image: np.ndarray        # int labels
    detection_quality: str = "unknown"
```

### 2.2 Calibration utilities

In `pipeline/calibrate.py`:

```python
UHCS_PX_PER_UM_DEFAULT = 6.5  # placeholder; update from Linoy’s calibration

def px_to_um2(area_px: float, px_per_um: float = UHCS_PX_PER_UM_DEFAULT) -> float:
    return area_px / (px_per_um ** 2)

def px_to_um(length_px: float, px_per_um: float = UHCS_PX_PER_UM_DEFAULT) -> float:
    return length_px / px_per_um

def um_to_px(length_um: float, px_per_um: float = UHCS_PX_PER_UM_DEFAULT) -> float:
    return length_um * px_per_um
```

You’ll overwrite `UHCS_PX_PER_UM_DEFAULT` once she gives you the averaged value from Mission 0.B.

### 2.3 Basic image I/O and preprocessing

In `pipeline/processing.py`:

```python
import cv2
import numpy as np
from scipy import ndimage as ndi
from skimage.segmentation import watershed, mark_boundaries
from skimage.feature import peak_local_max
from skimage.measure import regionprops, label
from skimage.filters import threshold_otsu, gaussian
from skimage.morphology import closing, square, remove_small_objects
from skimage import color, img_as_ubyte
import os

from .calibrate import px_to_um2
```

Functions:

```python
def load_image(path: str) -> np.ndarray | None:
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    return img.astype(np.float32) / 255.0

def crop_scale_bar(img: np.ndarray, crop_bottom_px: int = 60) -> np.ndarray:
    # remove bottom strip where scale bar lives
    return img[:-crop_bottom_px, :]

def preprocess(img: np.ndarray, blur_sigma: float = 1.5) -> np.ndarray:
    return gaussian(img, sigma=blur_sigma)
```

### 2.4 Segmentation

```python
def segment_grains(img: np.ndarray,
                   min_size: int = 50,
                   min_distance: int = 10) -> np.ndarray:
    # Threshold
    thresh = threshold_otsu(img)
    binary = img > thresh

    # Morphology
    binary = closing(binary, square(3))
    binary = remove_small_objects(binary, min_size=min_size)

    # Distance transform
    distance = ndi.distance_transform_edt(binary)

    # Seeds
    coords = peak_local_max(distance, min_distance=min_distance, labels=binary)
    mask = np.zeros(distance.shape, dtype=bool)
    if coords.size > 0:
        mask[tuple(coords.T)] = True
    markers, _ = ndi.label(mask)

    # Watershed
    labels_ws = watershed(-distance, markers, mask=binary)
    return labels_ws
```

### 2.5 Measurement and overlay

```python
def measure_grains(labeled: np.ndarray,
                   px_per_um: float) -> tuple[list, list, list, list, list]:
    props = regionprops(labeled)
    areas_px, areas_um2, perims, aspects, centroids = [], [], [], [], []

    for p in props:
        if p.area < 30:
            continue
        areas_px.append(p.area)
        areas_um2.append(px_to_um2(p.area, px_per_um))
        perims.append(p.perimeter)
        minor = p.minor_axis_length or 1.0
        aspects.append(p.major_axis_length / minor)
        centroids.append(p.centroid)

    return areas_px, areas_um2, perims, aspects, centroids

def create_overlay(original: np.ndarray,
                   labeled: np.ndarray) -> np.ndarray:
    rgb = color.gray2rgb(original)
    overlay = mark_boundaries(rgb, labeled, color=(1, 0.2, 0.1), mode="thick")
    return img_as_ubyte(overlay)
```

### 2.6 High‑level entry point

```python
def detect_grains(path: str,
                  px_per_um: float,
                  blur_sigma: float = 1.5,
                  crop_bottom: int = 60) -> GrainResult | None:
    import numpy as np

    img = load_image(path)
    if img is None:
        print(f"[SKIP] cannot load {path}")
        return None

    img_c = crop_scale_bar(img, crop_bottom)
    img_p = preprocess(img_c, blur_sigma)
    labeled = segment_grains(img_p)

    areas_px, areas_um2, perims, aspects, centroids = measure_grains(
        labeled, px_per_um
    )
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
```

---

## 3. Serialization to JSON / PNG

In `pipeline/report.py`:

```python
import os
import json
from pathlib import Path
import numpy as np
from PIL import Image
from .processing import GrainResult

RESULT_DIR = Path("docs/data/results")
IMAGE_DIR = Path("docs/data/images")

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
    with json_path.open("w") as f:
        json.dump(data, f, indent=2)

    return data
```

Main runner in `pipeline/process.py`:

```python
import os
import json
from pathlib import Path
from tqdm import tqdm
from .processing import detect_grains
from .calibrate import UHCS_PX_PER_UM_DEFAULT
from .report import save_result

IMG_DIR = Path("raw_data/uhcs/micrographs")
SELECTED_CSV = Path("raw_data/selected_images.csv")   # from Linoy
REJECTED_TXT = Path("raw_data/rejected_images.txt")   # from Linoy
INDEX_PATH = Path("docs/data/results/index.json")

def load_rejected() -> set[str]:
    if not REJECTED_TXT.exists():
        return set()
    return {
        line.split("|").strip()
        for line in REJECTED_TXT.read_text().splitlines()
        if line.strip()
    }

def discover_images() -> list[Path]:
    rejected = load_rejected()
    if SELECTED_CSV.exists():
        # process only selected ones
        import pandas as pd
        df = pd.read_csv(SELECTED_CSV)
        return [IMG_DIR / fn for fn in df["filename"].tolist() if fn not in rejected]
    # fallback: all images
    return [
        p for p in IMG_DIR.iterdir()
        if p.suffix.lower() in {".png", ".tif", ".tiff", ".jpg", ".jpeg"}
        and p.name not in rejected
    ]

def main():
    imgs = discover_images()
    summary: list[dict] = []

    for path in tqdm(imgs, desc="Processing"):
        res = detect_grains(str(path), px_per_um=UHCS_PX_PER_UM_DEFAULT)
        if res is None:
            continue
        meta = save_result(res)
        summary.append(meta)

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with INDEX_PATH.open("w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()
```

Call once after new data / parameters: `python -m pipeline.process`.

---

## 4. Static site (GitHub Pages)

### 4.1 `docs/index.html`

Minimal skeleton:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>GrainLens – Steel Microstructures</title>
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <link rel="stylesheet" href="css/style.css">
  <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
</head>
<body>
  <header>
    <h1>GrainLens</h1>
    <nav>
      <button data-tab="analyze" class="tab active">Analyze</button>
      <button data-tab="cases" class="tab">Case studies</button>
      <button data-tab="compare" class="tab">Compare</button>
    </nav>
  </header>

  <main>
    <section id="tab-analyze" class="tab-pane active">
      <div id="analyze-controls"></div>
      <div id="analyze-image"></div>
      <div id="analyze-stats"></div>
      <div id="analyze-chart"></div>
    </section>

    <section id="tab-cases" class="tab-pane">
      <div id="cases-container"></div>
    </section>

    <section id="tab-compare" class="tab-pane">
      <div id="compare-controls"></div>
      <div id="compare-chart"></div>
    </section>
  </main>

  <script src="js/app.js"></script>
  <script src="js/charts.js"></script>
</body>
</html>
```

### 4.2 Basic CSS (`docs/css/style.css`)

Keep it simple: flex header, tabs, responsive layout. You can iterate later.

### 4.3 JS data loader (`docs/js/app.js`)

Responsibilities:

- Handle tab switching.
- Fetch `data/results/index.json`.
- Populate dropdowns / lists with available images.
- On selection, fetch individual `<stem>.json` and render:
  - overlay image (using `overlay_path`),
  - stats table,
  - histogram chart via `charts.js`.

Skeleton:

```javascript
async function loadIndex() {
  const res = await fetch('data/results/index.json');
  return res.json();
}

function initTabs() {
  const tabs = document.querySelectorAll('button.tab');
  const panes = document.querySelectorAll('.tab-pane');
  tabs.forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.tab;
      tabs.forEach(b => b.classList.toggle('active', b === btn));
      panes.forEach(p => p.classList.toggle('active', p.id === `tab-${id}`));
    });
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  initTabs();
  const index = await loadIndex();
  initAnalyzeTab(index);
  initCasesTab();     // later, reading Linoy's case content
  initCompareTab(index);
});
```

### 4.4 Charts (`docs/js/charts.js`)

At minimum, implement:

- histogram of `areas_um2` with vertical lines at d10/d50/d90,
- multi‑histogram for comparison.

Example histogram:

```javascript
function plotGrainHistogram(containerId, areasUm2, stats, thresholds) {
  const trace = {
    x: areasUm2,
    type: 'histogram',
    marker: { color: '#01696f' },
    opacity: 0.75,
  };

  const shapes = [];
  ['d10_um2','d50_um2','d90_um2'].forEach(key => {
    const x = stats[key];
    shapes.push({
      type: 'line',
      x0: x, x1: x,
      y0: 0, y1: 1,
      xref: 'x',
      yref: 'paper',
      line: { color: '#964219', dash: 'dash' }
    });
  });

  const layout = {
    margin: { t: 20, r: 10, b: 40, l: 50 },
    xaxis: { title: 'Grain / feature area (µm²)' },
    yaxis: { title: 'Count' },
    shapes
  };

  Plotly.newPlot(containerId, [trace], layout, {displayModeBar: false});
}
```

Wire from `initAnalyzeTab` by reading the JSON.

---

## 5. Interaction with Linoy’s work

You need to **stop and wait for her** at specific points:

- After she provides `calibration.csv`: update `UHCS_PX_PER_UM_DEFAULT`.
- After she provides `rejected_images.txt`: re‑run `process.py` so bad images are excluded.
- After she creates `selected_images.csv`: process only those for the main case studies.
- Once she defines thresholds and case texts (in whatever content format you agree on): feed them into the site (e.g. via a `docs/data/case_studies.json` that you design).

You can keep the JSON schema minimal at first:
- `case_id`, `title`, `sample_images`, `processing_text`, `thermo_text`, `summary_text`, `grain_thresholds`.

---

## 6. Minimal dev workflow

1. Implement processing + report + index.
2. Run on a small subset of images.
3. Manually open `docs/index.html` → check JS works.
4. Iterate with Linoy:
   - she refines selection, thresholds, and explanations,
   - you adjust parameters and update pipeline / JS.

When things are stable, push `main`, GitHub Pages updates, and she can share the link as her project.