"""Download SEM images into raw_data/uhcs/micrographs from a simple URL list.

Usage:
  python -m pipeline.download_images
  python -m pipeline.download_images --sources raw_data/image_sources.txt --limit 20
"""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCES = PROJECT_ROOT / "raw_data" / "image_sources.txt"
DEFAULT_OUT_DIR = PROJECT_ROOT / "raw_data" / "uhcs" / "micrographs"
VALID_EXT = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


def parse_sources(path: Path) -> list[tuple[str, str | None]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing sources file: {path}")

    out: list[tuple[str, str | None]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" in line:
            url, name = [x.strip() for x in line.split("|", 1)]
            out.append((url, name or None))
        else:
            out.append((line, None))
    return out


def infer_name(url: str, preferred: str | None, index: int) -> str:
    if preferred:
        name = preferred
    else:
        parsed = urlparse(url)
        name = Path(parsed.path).name or f"img_{index:04d}.jpg"

    suffix = Path(name).suffix.lower()
    if suffix not in VALID_EXT:
        name = f"{Path(name).stem}.jpg"
    return name


def download(url: str, dst: Path, timeout_sec: int = 40) -> None:
    req = Request(url, headers={"User-Agent": "GrainLensDownloader/1.0"})
    with urlopen(req, timeout=timeout_sec) as resp:
        data = resp.read()
    dst.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--limit", type=int, default=0, help="0 = all")
    args = parser.parse_args()

    sources = parse_sources(args.sources)
    if args.limit > 0:
        sources = sources[: args.limit]

    args.out.mkdir(parents=True, exist_ok=True)
    ok, fail = 0, 0

    for i, (url, preferred_name) in enumerate(sources, start=1):
        name = infer_name(url, preferred_name, i)
        target = args.out / name
        try:
            download(url, target)
            print(f"[OK] {name}")
            ok += 1
        except Exception as exc:  # pragma: no cover
            print(f"[FAIL] {url} -> {exc}")
            fail += 1

    print("---")
    print(f"Downloaded: {ok}")
    print(f"Failed: {fail}")
    print(f"Folder: {args.out}")


if __name__ == "__main__":
    main()
