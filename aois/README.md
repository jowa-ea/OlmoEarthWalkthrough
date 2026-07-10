# AOIs — test oblasts (`test_oblasts.geojson`)

Held-out oblast boundaries used as areas of interest for OLMO Earth
inference/evaluation, separate from the point-based training sets in
`olmo_trainsets/`.

Source: `OLMO_training/data/admin1/oblasts_geojson/` (admin1 boundary
layer from the broader Ukraine winter-crop mapping pipeline, not part of
this repo). Four oblasts merged into a single FeatureCollection:

- Donetska
- Sumska
- Ternopilska
- Mykolaivska

Format: GeoJSON, EPSG:4326 (CRS84), one `Polygon`/`MultiPolygon` feature
per oblast, single property `oblast` (name). No `time` property — this
is a spatial AOI definition, not a training/reference dataset.
