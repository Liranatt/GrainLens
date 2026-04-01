# Linoy – Project Missions

This document describes **everything you need to do** in this project as a materials‑engineering student.  
No coding is required. Your work is scientific: interpreting microstructures, using thermodynamics, choosing images, and writing engineering conclusions.

---

## Overview

The project goal:

> Given an SEM image of steel, identify the microstructure, explain how it formed (processing + thermodynamics), and say what this implies for properties and applications.

Your missions are grouped into phases:

- **Phase 0** – Understand the data and microstructures.
- **Phase 1** – Write detailed case studies and select images.
- **Phase 2** – Add thermodynamic calculations and engineering‑style reports.

You can do all of this with: a browser, a text editor, your Thermodynamics 1 notes, and a materials textbook (e.g. Callister).

---

## Phase 0 – Understand the Microstructures and Images

### Mission 0.A – Study the steel microstructure classes

**Goal:** Be able to look at an SEM image and confidently say which class it belongs to and why.

1. Read about the UHCS (Ultra‑High Carbon Steel) microstructure classes:  
   - Use the UHCS paper (or similar resource) and your materials textbook.  
   - Focus on: pearlite, spheroidite, martensite, and (if present) network/Widmanstätten structures.

2. Create the following table in your notes (or a shared doc):

| Class          | What it looks like in SEM                                   | How it forms (T, cooling rate, processing)                | Main mechanical properties                  | Typical uses                   |
|---------------|--------------------------------------------------------------|------------------------------------------------------------|---------------------------------------------|---------------------------------|
| Pearlite      |                                                              |                                                            |                                             |                                 |
| Spheroidite   |                                                              |                                                            |                                             |                                 |
| Martensite    |                                                              |                                                            |                                             |                                 |
| Network       |                                                              |                                                            |                                             |                                 |
| Widmanstätten |                                                              |                                                            |                                             |                                 |

3. Fill the table in your **own words**, not copy‑pasted:
   - SEM description: shape of features (lamellae, needles, spheres, networks), contrast (light/dark).
   - Formation: approximate temperature range, “slow cool / quench / long anneal”, and what phases transform.
   - Properties: hard/soft, tough/brittle, machinable/not, etc.
   - Uses: examples where this microstructure is suitable.

This table is your reference for all later missions.

---

### Mission 0.B – Scale‑bar calibration

**Goal:** Provide a reliable conversion from pixels to micrometers, so the measurements from images have real units.

1. Open 5–10 representative SEM images from the dataset (different classes if possible).
2. For each image:
   - Find the **scale bar** (e.g. “20 µm”) at the bottom.
   - Measure its length in pixels using any image viewer that shows pixel coordinates (even basic tools are fine).
3. Create a CSV file called e.g. `calibration.csv` with:

```text
filename,scale_bar_px,scale_bar_um,px_per_um,notes
img_001.png,135,20,6.75,clear bar
img_002.png,128,20,6.40,slightly cropped
...
```

4. Compute `px_per_um = scale_bar_px / scale_bar_um` for each image and also an average.  
5. Write a short note: which value do you think should be used as the default? Why?

This lets the code convert areas from pixels² to µm² using your real calibration.

---

### Mission 0.C – Image quality screening

**Goal:** Decide which images are “good enough” for analysis and which should be rejected.

1. Browse through ~50–80 images from the dataset.
2. For each image, decide if it’s **usable** or should be **rejected** because of:
   - Out of focus.
   - Strong charging artifacts (bright streaks, glows).
   - Obvious contamination (dust, debris).
   - Over‑ or under‑exposure (too white or too dark).
   - Scale bar covering important microstructure.

3. Create a text file such as `rejected_images.txt`:

```text
img_045.png | out_of_focus | edges completely blurry
img_112.png | charging_artifact | bright streak bottom-left
img_203.png | contamination | circular debris upper-right
```

Every rejected image should have a clear reason.

---

## Phase 1 – Case Studies and Image Selection

### Mission 1.A – Define 3 main case studies

**Goal:** Write 3 complete microstructure case studies that will appear in the website.

Recommended cases:

1. **Pearlite – slow cooling**
2. **Martensite – quench**
3. **Spheroidite – long anneal**

For each case, you need to specify:

#### 1) Processing condition

In 2–3 sentences:

- Starting state (e.g. austenite at some temperature).
- What heat treatment or cooling path is applied.
- Any approximate rates or hold times that are important.

Example for pearlite (you will refine this):

> “Hypoeutectoid steel austenitized at ~850–900 °C, then slowly cooled through the eutectoid temperature (~727 °C) at a rate of order 1–5 °C/min, allowing diffusion and formation of pearlite colonies.”

#### 2) Thermodynamic explanation (qualitative)

In 4–5 sentences, connect the microstructure to Thermodynamics 1:

- Use \( \Delta G = \Delta H - T\Delta S \) at least qualitatively.
- Explain at what temperatures the transformation is favorable (ΔG < 0).
- For martensite: emphasize **metastability** and kinetics (diffusionless, fast quench).
- For spheroidite: discuss **interfacial energy** and why spherical particles reduce total energy.
- For pearlite: discuss why slow cooling allows equilibrium phases to form.

This is the “physics brain” of each case.

#### 3) Key features in the SEM image

List 3–5 things to look for:

- Examples:
  - Pearlite: alternating ferrite/cementite lamellae, colony boundaries.
  - Martensite: needle‑like or lath‑like features, high aspect ratio, low contrast between laths.
  - Spheroidite: round dark particles in a lighter matrix, coarsening compared to pearlite.

These will guide interpretation and help validate the segmentation.

#### 4) Expected properties and applications

In 2–3 sentences per case:

- Short description of expected hardness / toughness / ductility profile.
- One or two plausible applications (rails, machinable bars, hardened tools, etc.).
- Why that microstructure is suitable there.

You can keep all this initially in your own notes; later it will be moved into the project’s JSON/content files.

---

### Mission 1.B – Select representative images for each case

**Goal:** Choose the best examples of each microstructure for display and analysis.

1. For each of your 3 cases (pearlite, martensite, spheroidite):
   - Browse the SEM images and find **5 good images**.
2. Criteria:
   - The defining feature of the microstructure is clearly visible (lamellae, needles, spheres).
   - Image is in focus.
   - Scale bar is visible.
   - No major artifacts.

3. Create a CSV like `selected_images.csv`:

```text
case_id,filename,why_selected,quality_rating
pearlite_slow,img_001.png,clear lamellae with good contrast,3
pearlite_slow,img_007.png,large pearlite colonies visible,3
martensite_quench,img_089.png,fine lath martensite structure,3
spheroidite_anneal,img_150.png,uniform spheroidized carbides,3
...
```

- `case_id` – a short id for the case (e.g. `pearlite_slow`, `martensite_quench`, `spheroidite_anneal`).
- `quality_rating` – 1 (OK), 2 (good), 3 (excellent).

These “selected” images are the ones the site will highlight.

---

### Mission 1.C – Define “fine” vs “coarse” grain thresholds

**Goal:** Decide numerically what you call “fine” and “coarse” in terms of measured area.

After the first version of the pipeline has run, you’ll see grain size histograms for your images. For each case:

1. Look at the histogram of grain (or feature) areas in µm².
2. Decide:
   - `fine_max`: up to what area do you consider grains/features to be “fine”.
   - `coarse_min`: from what area do you consider them “coarse”.

There is no single correct answer; you use your engineering judgment:

- Finer structure often means faster cooling or more undercooling.
- Coarser grains/colonies mean slower cooling or longer anneal.

Write down, for each case:

```text
Case: Pearlite
fine_max ≈ ___ µm²  (reason: ...)
coarse_min ≈ ___ µm²  (reason: ...)

Case: Martensite
...

Case: Spheroidite
...
```

These thresholds will be used to color zones on the histograms (“fine / medium / coarse”).

---

### Mission 1.D – Validate the tool’s output

**Goal:** Check if the automatic detection is physically reasonable and describe any mistakes it makes.

Once Liran shows you the site or intermediate plots, do the following:

1. For each of your 3 case studies, pick 3–5 of the selected images.
2. For each image:
   - Look at the **original image** and make a rough estimate of how many grains/colonies you see in a central region.
   - Look at the **overlay image** with detected boundaries.
   - Compare your rough estimate with the tool’s “grain_count” and how the boundaries are drawn.

3. Create a validation file (e.g. `validation.csv`):

```text
case_id,filename,estimate_tool_match,notes
pearlite_slow,img_001.png,yes,overlay matches lamellae colonies reasonably
pearlite_slow,img_007.png,partial,tool sometimes splits one colony into two
martensite_quench,img_089.png,uncertain,features too fine to count by eye, segmentation noisy
spheroidite_anneal,img_150.png,no,small carbides are being merged into large blobs
```

Where `estimate_tool_match` can be: `yes`, `partial`, `no`, or `uncertain`.

4. The **notes** are the most important part. Describe in materials terms what is wrong when it’s wrong:
   - “Counting cementite lamellae as separate grains instead of whole pearlite colonies.”
   - “Missing grain boundaries where etching contrast is low.”
   - “Merging neighboring spheroidized carbides into bigger particles.”

This guidance will drive tuning of the algorithm.

---

## Phase 2 – Thermodynamics and Engineering Reports

### Mission 2.A – Simple ΔG(T) calculation for at least one transformation

**Goal:** Use Thermodynamics 1 formulas to compute ΔG as a function of temperature for one transformation, and interpret it.

A good starting point is the austenite → pearlite eutectoid reaction.

1. Use the relation:

\[
\Delta G = \Delta H - T\Delta S
\]

2. From a textbook or notes, get approximate values:
   - ΔH (J/mol) for austenite → pearlite decomposition (a typical number is around −4,200 J/mol for illustration).
   - T_eutectoid ≈ 727 °C ≈ 1000 K.

3. At the eutectoid point, ΔG ≈ 0, so:

\[
\Delta S \approx \frac{\Delta H}{T_{\text{eutectoid}}}
\]

4. For a few temperatures (e.g. 800, 900, 1000, 1100 K), compute:

\[
\Delta G(T) = \Delta H - T\Delta S
\]

5. Make a small table in your notes:

| T (K) | ΔG (J/mol) | Sign | Interpretation |
|-------|------------|------|----------------|
| 800   |            |      |                |
| 900   |            |      |                |
| 1000  |            |      |                |
| 1100  |            |      |                |

Check that:
- At ≈1000 K, ΔG ≈ 0.
- Below that, ΔG < 0 (product phases favorable).
- Above, ΔG > 0 (parent phase stable).

6. Write 3–4 sentences in plain language describing what that means for the transformation (when does pearlite form spontaneously, when is austenite stable).

This content feeds into the “thermodynamic explanation” of your pearlite case study.

---

### Mission 2.B – Activation energy lookup for grain growth / spheroidization

**Goal:** Provide realistic values of activation energy Q for relevant processes.

1. Use a materials text (Callister, physical metallurgy, or similar) to find Q values for:
   - Self‑diffusion in iron (for grain growth – approximate).
   - Carbon diffusion in α‑iron (for spheroidization).
2. Make a small table:

| Process                          | Q (kJ/mol) | Source (book, page)            |
|----------------------------------|-----------:|---------------------------------|
| Grain growth in Fe (approx.)     |            |                                 |
| Carbon diffusion in α‑Fe         |            |                                 |

3. Add a short note for each: what process this Q is meant to approximate in your case studies (e.g. “spheroidization of pearlite at ~700 °C”).

These Q values will be used to draw simple “predicted grain size vs time and temperature” curves.

---

### Mission 2.C – Write engineering‑style summaries for each case

**Goal:** For each case study, write a short “mini‑report” like you would send to an engineering team.

For each of your 3 main cases (pearlite, martensite, spheroidite), write a paragraph (~4–6 sentences) covering:

1. What microstructure is observed and how you know (reference features you see in SEM).
2. What processing history it suggests (slow cool / quench / anneal, approximate conditions).
3. How the measured grain/feature sizes fit with that history (fine vs coarse, consistent or not).
4. What this implies for mechanical behavior (hard/soft, ductile/brittle, machinable?).
5. Whether that structure is appropriate for a chosen application and why.

Example skeleton (you will fill it with real values and reasoning):

> “The examined sample shows a predominantly pearlitic microstructure with well‑defined lamellae and large colonies, consistent with slow cooling from the austenite region through the eutectoid temperature. Measured colony sizes are in the ___ µm² range, which corresponds to a relatively coarse pearlite, as expected for furnace cooling. This structure provides moderate hardness with reasonable ductility, making it suitable for applications such as ___ where a balance between strength and toughness is required. There is no evidence of martensite or significant spheroidization, indicating that no rapid quench or long sub‑eutectoid anneal was applied.”

Once the measurements are available, you can insert the actual average grain/feature sizes instead of blanks.

These paragraphs are what future reviewers/interviewers will actually read to understand your engineering thinking.

---

## Summary of your deliverables

Over the project, you will create and maintain:

- A **microstructure overview table** (Phase 0.A).
- `calibration.csv` – scale bar measurements and recommended px/µm (Phase 0.B).
- `rejected_images.txt` – list of unusable images with reasons (Phase 0.C).
- `selected_images.csv` – mapping from case studies to chosen images with brief justification (Phase 1.B).
- Notes for each **case study**: processing, thermodynamic explanation, key features, properties, applications (Phase 1.A).
- A **validation sheet** recording where the tool matches or disagrees with your physical expectation (Phase 1.D).
- Simple **ΔG(T)** calculations for at least one transformation and activation energy notes (Phase 2.A, 2.B).
- Three **engineering‑style summary paragraphs** (Phase 2.C).

If you work through these missions one by one, you’ll end up with a complete, coherent materials‑engineering project that shows real understanding of microstructures, thermodynamics, and structure–property relationships.