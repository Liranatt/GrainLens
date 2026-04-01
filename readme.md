# GrainLens

GrainLens is a small materials‑engineering project that analyzes SEM images of steel microstructures, measures grain‑related features, and links them to processing history and expected properties.

The focus is on classical carbon steels (e.g. pearlite, spheroidite, martensite) and on the connection between **processing → microstructure → properties**, using basic thermodynamics and phase‑transformation concepts.

---

## What the project does

- Loads SEM micrographs of steel from an open dataset.
- Segments microstructural features (grains / colonies / laths) in each image.
- Measures grain‑related quantities (area, equivalent diameter, aspect ratio, basic statistics).
- Visualizes grain size distributions and overlays detected boundaries on the original images.
- Organizes a few **case studies**:
  - microstructure class and typical heat treatment,
  - qualitative thermodynamic explanation (ΔG, driving forces, metastability),
  - short engineering “conclusion” for each sample.

The end result is a static web page (GitHub Pages) that shows these images, measurements, and explanations in a way that is easy to browse.

---

## Main ideas (engineering side)

The project uses only basic ideas from Thermodynamics 1 and introductory physical metallurgy, for example:

- Gibbs free energy \( \Delta G = \Delta H - T\Delta S \) to discuss when phases are stable and when transformations are favorable.
- Simple grain‑growth relations to reason about why long anneals lead to coarser structures and how that affects properties.
- Qualitative structure–property links: fine vs. coarse grains, lamellar vs. spheroidal cementite, martensitic vs. equilibrated structures.

No advanced simulation or ML is used; the emphasis is on interpretation, not on heavy numerics.

---

## Project structure

```text
grainlens/
├── docs/           # Static site (for GitHub Pages)
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── data/       # JSON + images used by the site
├── pipeline/       # Local scripts to process images and generate docs/data/*
└── raw_data/       # SEM dataset (not tracked in git)
```

- The **pipeline** scripts run locally to process images and write JSON/PNG files into `docs/data/`.
- The **docs** folder is a static site that reads those JSON files in the browser and shows the results.

---

## How to run (when everything is implemented)

1. **Clone the repository**

```bash
git clone https://github.com/<username>/grainlens.git
cd grainlens
```

2. **Set up Python environment** (optional but recommended)

```bash
cd pipeline
pip install -r requirements.txt
```

3. **Download the SEM dataset**

Download the UHCS (or other) SEM images into `raw_data/` and adjust the paths in the pipeline config if needed.

4. **Generate analysis results**

```bash
cd pipeline
python process.py
# writes JSON + PNG overlays into ../docs/data/
```

5. **Open the site locally**

Open `docs/index.html` in a browser (double‑click or `open docs/index.html`).  
Once GitHub Pages is configured, the same site will be available at:

```text
https://<username>.github.io/grainlens
```

---

## Status

This repository is under active development.

Planned pieces include:

- better segmentation parameters per microstructure type,
- more case studies with literature references,
- and small improvements to the web visualization.