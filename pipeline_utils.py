"""Shared data-loading, reclassification, and export logic for the DS1/DS3
OLMO Earth workshop pipeline.

Used by both prepare_ds1_ds3_for_olmo.ipynb and main.py so the notebook
(exploration/teaching) and the script (headless local run) stay in sync.
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
from pathlib import Path

import geopandas as gpd
import pandas as pd

MAX_PER_FILE = 100_000

DATA_REPOS = {
    "Ukraine_CIS_annotations_2021-2024": "https://github.com/jowa-ea/Ukraine_CIS_annotations_2021-2024.git",
    "Uk_sample_units_22-25": "https://github.com/jowa-ea/Uk_sample_units_22-25.git",
}

# DS1 -- cropland status, reclassified from CIS_annotations_2021-2024
DS1_ENCODING = {"Cultivated": 1, "Non-crop": 2, "Abandoned": 3, "Fallow": 4}
DS1_LABELS = {1: "Cropland", 2: "Non-cropland", 3: "Abandoned", 4: "Fallow"}

# DS3 -- crop type on confirmed cropland, reclassified from Uk_sample_units_22-25
DS3_ENCODING = {"Winter_cer": 1, "Rapeseed": 2, "Summer_cro": 3}
DS3_LABELS = {1: "Winter cereals", 2: "Rapeseed", 3: "Summer crop"}

CIS_YEAR_COLUMNS = [
    (2021, "Label_21"), (2022, "Label_22"),
    (2023, "Label_23"), (2024, "Label_24"),
]
GPKG_YEARS = [2022, 2023, 2024, 2025]


def clone_if_missing(url: str, dest: Path) -> Path:
    """Shallow-clone a repo into dest unless it's already present."""
    if dest.exists():
        print(f"{dest.name}: already present, skipping clone")
    else:
        print(f"Cloning {dest.name} ...")
        subprocess.run(["git", "clone", "--depth", "1", url, str(dest)], check=True)
    return dest


def clone_data_repos(repos_dir: Path) -> dict[str, Path]:
    """Clone both source annotation repos into repos_dir, return their paths."""
    repos_dir.mkdir(parents=True, exist_ok=True)
    return {name: clone_if_missing(url, repos_dir / name) for name, url in DATA_REPOS.items()}


def read_cis(shp_path: Path) -> pd.DataFrame:
    """One row per (point, year) from the CIS wide-format shapefile, raw labels only."""
    gdf = gpd.read_file(shp_path)
    records = []
    for _, row in gdf.iterrows():
        lat, lon = float(row["lat"]), float(row["lon"])
        for year, label_col in CIS_YEAR_COLUMNS:
            label = str(row[label_col]).strip() if row[label_col] is not None else ""
            if not label:
                continue
            records.append({"longitude": lon, "latitude": lat, "year": year, "original_class": label})
    return pd.DataFrame.from_records(records)


def read_gpkg(gpkg_dir: Path, year: int) -> pd.DataFrame:
    """Raw points from one Uk_sample_units_22-25 yearly GeoPackage."""
    gpkg = gpkg_dir / f"{year}_annotated_data.gpkg"
    table = f"{year}_annotated_data"
    with sqlite3.connect(gpkg) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(f'SELECT "lat", "lon", "fid", "Year", "Class_st" FROM "{table}"').fetchall()
    records = []
    for r in rows:
        if r["lat"] is None or r["lon"] is None:
            continue
        records.append({
            "longitude": float(r["lon"]),
            "latitude": float(r["lat"]),
            "year": int(r["Year"] or year),
            "fid": r["fid"],
            "original_class": r["Class_st"],
        })
    return pd.DataFrame.from_records(records)


def load_gpkgs(gpkg_dir: Path, years: list[int] = GPKG_YEARS) -> pd.DataFrame:
    """Concatenate all yearly GeoPackages into one raw points DataFrame."""
    return pd.concat([read_gpkg(gpkg_dir, year) for year in years], ignore_index=True)


def build_ds1(cis_raw: pd.DataFrame) -> pd.DataFrame:
    """Reclassify raw CIS labels into the DS1 cropland-status scheme."""
    unknown = set(cis_raw["original_class"]) - set(DS1_ENCODING)
    if unknown:
        raise ValueError(f"Unknown CIS labels encountered: {unknown}")
    ds1 = cis_raw.copy()
    ds1["class_cropland_full"] = ds1["original_class"].map(DS1_ENCODING)
    ds1["label_cropland_full"] = ds1["class_cropland_full"].map(DS1_LABELS)
    ds1["time"] = ds1["year"].astype(str) + "-04-15"
    return ds1


def build_ds3(gpkg_raw: pd.DataFrame) -> pd.DataFrame:
    """Filter to confirmed cropland-with-known-type and reclassify into DS3 crop types."""
    ds3 = gpkg_raw.loc[gpkg_raw["original_class"].isin(DS3_ENCODING)].copy()
    ds3["class_crop_type"] = ds3["original_class"].map(DS3_ENCODING)
    ds3["label_crop_type"] = ds3["class_crop_type"].map(DS3_LABELS)
    ds3["time"] = ds3["year"].astype(str) + "-04-15"
    return ds3


def _chunks(df: pd.DataFrame, n: int):
    for i in range(0, len(df), n):
        yield df.iloc[i:i + n]


def _json_default(obj):
    """Coerce numpy scalars (int64/float64) to native Python types for json.dumps."""
    if hasattr(obj, "item"):
        return obj.item()
    return str(obj)


def export_csv(df: pd.DataFrame, out_dir: Path, stem: str, columns: list[str]) -> list[Path]:
    """Write df to one or more OLMO-compliant CSV files, chunked to MAX_PER_FILE rows."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for idx, chunk in enumerate(_chunks(df, MAX_PER_FILE), start=1):
        out = out_dir / f"{stem}_part{idx:03d}.csv"
        chunk[columns].to_csv(out, index=False)
        paths.append(out)
    return paths


def export_geojson(df: pd.DataFrame, out_dir: Path, stem: str, columns: list[str]) -> list[Path]:
    """Write df to one or more OLMO-compliant GeoJSON FeatureCollections, chunked to MAX_PER_FILE features."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for idx, chunk in enumerate(_chunks(df, MAX_PER_FILE), start=1):
        features = []
        for _, row in chunk.iterrows():
            props = {c: row[c] for c in columns if c not in ("longitude", "latitude")}
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row["longitude"], row["latitude"]]},
                "properties": props,
            })
        fc = {"type": "FeatureCollection", "features": features}
        out = out_dir / f"{stem}_part{idx:03d}.geojson"
        out.write_text(json.dumps(fc, default=_json_default), encoding="utf-8")
        paths.append(out)
    return paths


def validate_olmo_format(df: pd.DataFrame) -> None:
    """Check the required OLMO columns and ISO-8601 'time' format are present."""
    required = {"longitude", "latitude", "time"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required OLMO columns: {missing}")
    bad_dates = df.loc[~df["time"].astype(str).str.match(r"^\d{4}-\d{2}-\d{2}"), "time"]
    if len(bad_dates):
        raise ValueError(f"Found {len(bad_dates)} rows with non ISO-8601 'time' values")
    print(f"OK - {len(df)} rows, required columns present, time format valid")
