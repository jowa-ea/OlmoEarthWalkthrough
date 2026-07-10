# OLMO Earth walkthrough — preparing reference training data

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jowa-ea/OlmoEarthWalkthrough/blob/main/prepare_ds1_ds3_for_olmo.ipynb)

Workshop material for the OLMO Earth data-prep session. The notebook
`prepare_ds1_ds3_for_olmo.ipynb` clones two public annotation repositories,
explores the raw label data, reclassifies it into the class schemes used
to train Ukraine winter-crop models, and exports the result in the two
file formats [OLMO Earth](https://olmoearth.allenai.org/) accepts for
reference/training data (CSV, GeoJSON).

## Run it

- **Locally**: create a Python environment, install the dependencies
  (`pip install -r requirements.txt`), open `prepare_ds1_ds3_for_olmo.ipynb`
  in Jupyter with that environment as the kernel, and run all cells from
  this folder.
- **Google Colab**: open the notebook in Colab and run all cells — the
  first cells detect the Colab environment, install the missing
  geospatial packages, and clone this repo to pick up the bundled files
  under `data/`.

## What it produces

Two point-based reference datasets, written to `olmo_trainsets/` (see the
README there for column/class documentation):

- **DS1** — cropland status (Cropland / Non-cropland / Abandoned /
  Fallow), from `Ukraine_CIS_annotations_2021-2024` (2021–2024).
- **DS3** — crop type on confirmed cropland (Winter cereals / Rapeseed /
  Summer crop), from `Uk_sample_units_22-25` (2022–2025).

Both are reproduced from public GitHub repos only.

## Folder contents

```
AI2_workshop_olmo_walkthrough/
├── prepare_ds1_ds3_for_olmo.ipynb   notebook (this is the deliverable)
├── data/
│   └── oblasts_simplified.geojson   Ukraine oblast boundaries (simplified,
│                                     ~488 KB), used as basemap context for
│                                     the spatial-distribution plots
├── olmo_trainsets/                  DS1 & DS3 outputs + README (tracked)
├── aois/                            oblast AOIs for OLMO inference: the 4
│                                     test oblasts (merged + individual) and
│                                     other_oblasts.geojson (remaining 21)
└── workshop_prep/                   gitignored; repo clones land here at
                                      runtime, regenerated on every run
```

## Source repos

- CIS annotations 2021–2024: https://github.com/jowa-ea/Ukraine_CIS_annotations_2021-2024
  — Wagner, J. et al., *Monitoring cropland cultivation, abandonment,
  fallowing and recultivation dynamics with regard to conflict intensity
  in war-affected Ukraine*, Science of Remote Sensing, 12 (2025).
  https://doi.org/10.1016/j.srs.2025.100326
- Annotated sample units 2022–2025: https://github.com/jowa-ea/Uk_sample_units_22-25
  — Wagner, J., Skakun, S., Nair, S.S. et al., *Monitoring winter crop
  areas during wartime: remote sensing support for Ukraine's
  agricultural statistics*, npj Sustainable Agriculture, 4, 1 (2026).
  https://doi.org/10.1038/s44264-025-00119-4
