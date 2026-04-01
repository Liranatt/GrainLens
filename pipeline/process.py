import json
from pathlib import Path

from tqdm import tqdm

from .calibrate import UHCS_PX_PER_UM_DEFAULT
from .processing import detect_grains
from .report import save_result

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = PROJECT_ROOT / "raw_data" / "uhcs" / "micrographs"
SELECTED_CSV = PROJECT_ROOT / "raw_data" / "selected_images.csv"
REJECTED_TXT = PROJECT_ROOT / "raw_data" / "rejected_images.txt"
INDEX_PATH = PROJECT_ROOT / "docs" / "data" / "results" / "index.json"
VALID_SUFFIXES = {".png", ".tif", ".tiff", ".jpg", ".jpeg", ".bmp"}


def load_rejected() -> set[str]:
    if not REJECTED_TXT.exists():
        return set()

    rejected: set[str] = set()
    for raw in REJECTED_TXT.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if parts and parts[0]:
            rejected.add(parts[0])
    return rejected


def discover_images() -> list[Path]:
    rejected = load_rejected()

    if SELECTED_CSV.exists():
        import pandas as pd

        df = pd.read_csv(SELECTED_CSV)
        if "filename" in df.columns:
            candidates = [IMG_DIR / str(fn) for fn in df["filename"].dropna().tolist()]
            return [p for p in candidates if p.name not in rejected and p.exists()]

    if not IMG_DIR.exists():
        return []

    return sorted(
        [
            p
            for p in IMG_DIR.iterdir()
            if p.is_file() and p.suffix.lower() in VALID_SUFFIXES and p.name not in rejected
        ]
    )


def main() -> None:
    imgs = discover_images()
    summary: list[dict] = []

    for path in tqdm(imgs, desc="Processing"):
        res = detect_grains(str(path), px_per_um=UHCS_PX_PER_UM_DEFAULT)
        if res is None:
            continue
        meta = save_result(res)
        summary.append(meta)

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with INDEX_PATH.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Wrote {len(summary)} result entries to {INDEX_PATH}")


if __name__ == "__main__":
    main()
