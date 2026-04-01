# Raw Data Placement

Put SEM images and related metadata under this folder.

Expected layout for the current pipeline:

- `raw_data/uhcs/micrographs/` contains source images (`.png`, `.jpg`, `.tif`, etc.)
- `raw_data/selected_images.csv` lists selected filenames for case studies
- `raw_data/rejected_images.txt` lists files to skip during processing
- `raw_data/calibration.csv` stores scale-bar measurements

Only metadata templates are tracked in git. Large image files are ignored by `.gitignore`.
