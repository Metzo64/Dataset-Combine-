# Google Earth Engine Scripts

This directory contains JavaScript files for extracting satellite environmental data using Google Earth Engine.

## Files

### 1. `satellite_generator.js`
Main script for extracting SST and chlorophyll-a data for all 25,000 fisheries observations (2015-2024).

### 2. `test_single_month.js`
Test script for validating extraction methodology on a single month before full-scale processing.

## Prerequisites

1. **Google Earth Engine Account**
   - Sign up at: https://earthengine.google.com/
   - Request access (usually approved within 1-2 days)

2. **GEE Code Editor Access**
   - Access at: https://code.earthengine.google.com/

3. **Fisheries Dataset Upload**
   - Upload `fisheries_25000.csv` as a Table Asset in GEE
   - Note the Asset ID (e.g., `users/YOUR_USERNAME/fisheries_25000`)

## Usage Instructions

### Step 1: Upload Fisheries CSV to GEE

1. Open Google Earth Engine Code Editor: https://code.earthengine.google.com/
2. Click on "Assets" tab (left panel)
3. Click "NEW" → "CSV file"
4. Upload `fisheries_25000.csv` from the project root
5. Name the asset: `fisheries_25000`
6. Wait for upload to complete (may take a few minutes)
7. Note the full Asset ID (shown as `users/YOUR_USERNAME/fisheries_25000`)

### Step 2: Configure Asset ID

Open `satellite_generator.js` or `test_single_month.js` and update the asset ID:

```javascript
// UPDATE THIS LINE with your actual asset ID
var FISHERIES_ASSET = 'users/YOUR_USERNAME/fisheries_25000';
```

### Step 3: Test Extraction (Single Month)

1. Open `test_single_month.js` in GEE Code Editor
2. Update the asset ID (see Step 2)
3. Click "Run"
4. Check Console for progress and statistics
5. Review extracted values on the map
6. Export test data to Google Drive:
   - Click "Tasks" tab
   - Click "Run" next to the export task
   - Wait for completion (1-2 minutes)

### Step 4: Full Extraction (All Years)

1. Open `satellite_generator.js` in GEE Code Editor
2. Update the asset ID (see Step 2)
3. Click "Run"
4. Check Console for statistics
5. Export all annual batches:
   - Click "Tasks" tab
   - You'll see 10 tasks (one per year: 2015-2024)
   - Click "Run" for each task
   - Monitor progress in Tasks tab
   - Each task takes 10-30 minutes

### Step 5: Download Exports

1. Go to Google Drive
2. Find folder: `GEE_Satellite_Exports`
3. Download all CSV files:
   - `satellite_2015.csv`
   - `satellite_2016.csv`
   - ...
   - `satellite_2024.csv`
4. Place downloaded files in: `output/satellite_exports/`

### Step 6: Consolidate Exports

```bash
python src/merge_satellite_exports.py
```

This creates: `output/final/satellite_25000_rebuilt.csv`

### Step 7: Validate Final Dataset

```bash
python src/validate_satellite.py
```

This generates: `output/reports/satellite_validation_report.txt`

## Troubleshooting

### Issue: "Asset not found"
**Solution:** Check that the asset ID is correct and the CSV upload completed successfully.

### Issue: "Computation timed out"
**Solution:** This is rare. Try reducing the batch size or re-running the failed export.

### Issue: "Too many concurrent operations"
**Solution:** GEE limits concurrent export tasks. Wait for some tasks to complete before starting more.

### Issue: "Missing satellite_exports folder"
**Solution:** Create the directory:
```bash
mkdir -p output/satellite_exports
```

### Issue: Chlorophyll values mostly null
**Explanation:** Chlorophyll satellite imagery often has gaps due to clouds. This is normal and expected.

## Expected Results

**SST (Sea Surface Temperature):**
- Expected completeness: ~99% (very few missing values)
- Typical range: 22-32°C for study area
- Source: NOAA OISST v2.1 (daily, 0.25° resolution)

**Chlorophyll-a:**
- Expected completeness: 30-70% (many gaps due to clouds)
- Typical range: 0.05-5 mg/m³ (open ocean), up to 20 mg/m³ (coastal)
- Source: MODIS Aqua L3SMI (daily, 4 km resolution)

## Data Sources

### NOAA OISST v2.1
- **GEE ID:** `NOAA/CDR/OISST/V2_1`
- **Band:** `sst`
- **Units:** Degrees Celsius
- **Resolution:** 0.25° (~25 km)
- **Coverage:** 1981-present

### MODIS Aqua Ocean Color
- **GEE ID:** `NASA/OCEANDATA/MODIS-Aqua/L3SMI`
- **Band:** `chlor_a`
- **Units:** mg/m³
- **Resolution:** 4 km
- **Coverage:** July 2002-present

## Notes

- Export tasks run asynchronously (you can close the browser)
- Check task status at: https://code.earthengine.google.com/ (Tasks tab)
- Failed tasks can be re-run without affecting completed ones
- Each annual export is ~1-2 MB

## Support

For GEE-specific issues:
- Documentation: https://developers.google.com/earth-engine/
- Forum: https://groups.google.com/g/google-earth-engine-developers
