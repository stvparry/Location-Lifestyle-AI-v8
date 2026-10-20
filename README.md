# Location Lifestyle AI V8

A fully self-contained Streamlit release. No separate geographic download, reconciliation script or batch file is required.

## Deploy
1. Unzip.
2. Upload all files to a new GitHub repository.
3. Deploy `app.py` in Streamlit Community Cloud.

## Included
- 200 uniquely named real GB places
- complete coordinates with per-row source/status
- Recommendations first
- household profile presets and JSON import/export
- removable Life Network rows
- Road and Public Transport Journey Maps
- miles, estimated minutes and monthly travel burden
- recommendation network threshold
- compact dials
- comparison and narrative views
- QA report

## Travel assumptions
Road: 35 mph effective average plus 10 minutes.
Public transport: 45 mph effective average plus 30 minutes.
These are explanatory proxies, not live routing or timetables.

## Data honesty
Coordinates are complete. 159 rows use the bundled GeoNamesCache dataset; 41 smaller/core lifestyle places use explicit curated town-centre points. County/area is specific for curated core locations; GeoNames-derived expansion records use nation-level administrative labels because the bundled dataset does not provide ceremonial county.
Lifestyle scores remain deterministic seed assessments for product testing, not official statistics.
