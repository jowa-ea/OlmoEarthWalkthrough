#!/usr/bin/env python
"""Script equivalent of prepare_ds3_ds4_for_olmo.ipynb: clones the two
source annotation repos, reclassifies them into DS4 (cropland status) and
DS3 (crop type), and exports both in OLMO-ready CSV/GeoJSON to
olmo_trainsets/. Run from this directory after installing the dependencies:

    pip install -r requirements.txt
    python main.py

The notebook covers the same pipeline plus data exploration (spatial and
yearly label distribution plots) and walks through the reclassification
rationale -- use it for the walkthrough, use this script for a quick
headless reproduction of the two datasets.
"""

from __future__ import annotations

from pathlib import Path

import pipeline_utils as pu

BASE_DIR = Path(__file__).parent
REPOS_DIR = BASE_DIR / "workshop_prep" / "repos"
OUTPUT_DIR = BASE_DIR / "olmo_trainsets"

DS4_COLUMNS = ["longitude", "latitude", "time", "year", "original_class",
               "class_cropland_full", "label_cropland_full"]
DS3_COLUMNS = ["longitude", "latitude", "time", "year", "fid", "original_class",
               "class_crop_type", "label_crop_type"]


def main() -> None:
    repos = pu.clone_data_repos(REPOS_DIR)
    cis_shp = repos["Ukraine_CIS_annotations_2021-2024"] / "CIS_annotations_2021-2024.shp"
    gpkg_dir = repos["Uk_sample_units_22-25"]

    print("\nReading CIS shapefile ...")
    cis_raw = pu.read_cis(cis_shp)
    print(f"  {len(cis_raw)} point-year records loaded")

    print("Reading Uk_sample_units GPKGs (2022-2025) ...")
    gpkg_raw = pu.load_gpkgs(gpkg_dir)
    print(f"  {len(gpkg_raw)} points loaded")

    print("\nBuilding DS4 (cropland status) ...")
    ds4 = pu.build_ds4(cis_raw)
    pu.validate_olmo_format(ds4)
    ds4_paths = pu.export_csv(ds4, OUTPUT_DIR, "ds4_cropland_full_21-24", DS4_COLUMNS)
    ds4_paths += pu.export_geojson(ds4, OUTPUT_DIR, "ds4_cropland_full_21-24", DS4_COLUMNS)

    print("\nBuilding DS3 (crop type) ...")
    ds3 = pu.build_ds3(gpkg_raw)
    pu.validate_olmo_format(ds3)
    ds3_paths = pu.export_csv(ds3, OUTPUT_DIR, "ds3_crop_types_22-25", DS3_COLUMNS)
    ds3_paths += pu.export_geojson(ds3, OUTPUT_DIR, "ds3_crop_types_22-25", DS3_COLUMNS)

    print("\nWritten:")
    for p in ds4_paths + ds3_paths:
        print(" ", p)


if __name__ == "__main__":
    main()
