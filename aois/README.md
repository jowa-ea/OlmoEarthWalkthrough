# AOIs — oblast boundaries for OLMO Earth inference

Oblast-level areas of interest, used to define where OLMO Earth
inference/evaluation runs, separate from the point-based training sets
in `olmo_trainsets/`.

Source: `OLMO_training/data/admin1/oblasts_geojson/` (admin1 boundary
layer from the broader Ukraine winter-crop mapping pipeline, not part of
this repo; 25 oblast-level units total).

Format (both files): GeoJSON, EPSG:4326 (CRS84), one
`Polygon`/`MultiPolygon` feature per oblast, single property `oblast`
(name). No `time` property — these are spatial AOI definitions, not
training/reference datasets.

## Files

- **`test_oblasts.geojson`** — the four held-out test oblasts merged
  into one FeatureCollection: Donetska, Sumska, Ternopilska, Mykolaivska.
- **`other_oblasts.geojson`** — the remaining 21 oblasts (everything
  except the four test oblasts above), merged into one FeatureCollection.
