# GrainLens

GrainLens analyzes SEM images of steel microstructures and publishes interactive results as a static GitHub Pages site.

## Repository layout

```text
GrainLens/
├── docs/                     # GitHub Pages site (main branch, /docs folder)
│   ├── index.html
│   ├── .nojekyll
│   ├── css/style.css
│   ├── js/
│   │   ├── app.js
│   │   ├── charts.js
│   │   └── viewer.js
│   └── data/
│       ├── results/index.json
│       ├── images/
│       └── case_studies.json
├── pipeline/                 # Local Python processing pipeline
│   ├── calibrate.py
│   ├── processing.py
│   ├── report.py
│   └── process.py
└── raw_data/                 # Local dataset + metadata templates
```

## Quick start

1. Install dependencies:

```bash
pip install -r pipeline/requirements.txt
```

2. Place SEM images in `raw_data/uhcs/micrographs/`.

If you have direct image links, you can auto-download them:

```bash
python -m pipeline.download_images
```

Edit `raw_data/image_sources.txt` first and paste one URL per line.

3. Run processing from repository root:

```bash
python -m pipeline.process
```

4. Open `docs/index.html` to inspect results locally.

## GitHub Pages

Configure Pages to deploy from `main` branch, folder `/docs`.

The frontend is static and uses only relative paths (for example `data/results/index.json`), so it works on GitHub Pages without backend services.