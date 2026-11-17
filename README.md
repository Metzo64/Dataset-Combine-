# Satellite Dataset Generation using Google Earth Engine

**Version:** 1.0  
**Study Period:** 2015-2024 (10 years, 120 months)  
**Study Area:** 0°-30°N, 50°-100°E (Northern Indian Ocean)  
**Target Records:** 25,000 satellite observations aligned with fisheries data

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Study Requirements](#study-requirements)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Google Earth Engine Setup](#google-earth-engine-setup)
6. [Usage Instructions](#usage-instructions)
7. [Output Dataset](#output-dataset)
8. [Validation](#validation)
9. [Troubleshooting](#troubleshooting)
10. [Scientific Methodology](#scientific-methodology)

---

## Project Overview

This project regenerates a satellite environmental dataset using genuine satellite observations from Google Earth Engine (GEE). The dataset provides Sea Surface Temperature (SST) and Chlorophyll-a measurements that are spatially and temporally aligned with 25,000 fisheries observations across the Northern Indian Ocean from 2015-2024.

### Key Features

- **Scientifically rigorous**: Uses NOAA and NASA satellite data sources
- **Spatially aligned**: Extracts measurements at exact fisheries coordinates
- **Temporally aligned**: Preserves original observation dates
- **Quality controlled**: Transparent handling of missing values
- **Reproducible**: Fully documented methodology and code
- **Validated**: Comprehensive automated validation checks

### Satellite Data Sources

1. **Sea Surface Temperature**: NOAA OISST v2.1 (daily, 0.25° resolution)
2. **Chlorophyll-a**: MODIS Aqua Ocean Color L3SMI (daily, 4 km resolution)

---

## Study Requirements

### Geographical Coverage

- **Latitude**: 0° to 30° North
- **Longitude**: 50° to 100° East
- **Region**: Northern Indian Ocean (Arabian Sea and Bay of Bengal)

### Temporal Coverage

- **Start Date**: January 1, 2015
- **End Date**: December 31, 2024
- **Duration**: 10 years, 120 months
- **Target Distribution**: 2,500 records per year, all 12 months represented

### Reference Dataset

The `fisheries_25000.csv` file is the PRIMARY reference for:
- Observation coordinates (latitude, longitude)
- Observation dates
- Unique fisheries record IDs
- Expected record count (25,000)

**The satellite dataset must have exactly one record per fisheries observation.**

---

## Project Structure

```
maj maj/
│
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── .gitignore                          # Git ignore rules
│
├── fisheries_25000.csv                 # Reference fisheries dataset (DO NOT MODIFY)
├── satellite_25000.csv                 # Old satellite dataset (for schema reference only)
│
├── config/
│   └── config.py                       # Project configuration
│
├── gee/                                # Google Earth Engine scripts
│   ├── README.md                       # GEE-specific instructions
│   ├── satellite_generator.js          # Main extraction script (all years)
│   └── test_single_month.js            # Test script (single month)
│
├── src/                                # Python source code
│   ├── __init__.py
│   ├── inspect_fisheries.py            # Phase 1: Inspect fisheries dataset
│   ├── merge_satellite_exports.py      # Phase 6: Consolidate GEE exports
│   └── validate_satellite.py           # Phase 7: Validate final dataset
│
├── output/
│   ├── satellite_exports/              # GEE export files (download here)
│   ├── final/                          # Final consolidated dataset
│   │   └── satellite_25000_rebuilt.csv
│   └── reports/                        # Inspection and validation reports
│       ├── fisheries_inspection_report.txt
│       ├── satellite_source_report.md
│       ├── extraction_methodology.md
│       └── satellite_validation_report.txt
│
└── logs/                               # Log files
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Earth Engine account (free, registration required)
- Google Drive account (for GEE exports)

### Python Environment Setup

1. **Clone or navigate to the project directory**:
   ```powershell
   cd "D:\Projects\Projects\maj maj"
   ```

2. **Install Python dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```powershell
   python -c "import pandas, numpy; print('Dependencies installed successfully')"
   ```

---

## Google Earth Engine Setup

### Step 1: Create GEE Account

1. Go to: https://earthengine.google.com/
2. Click "Sign Up"
3. Use your Google account to register
4. Wait for approval (usually 1-2 days, sometimes instant)
5. Verify access at: https://code.earthengine.google.com/

### Step 2: Upload Fisheries Dataset

1. Open GEE Code Editor: https://code.earthengine.google.com/
2. Click "Assets" tab (left panel)
3. Click "NEW" → "CSV file"
4. Select `fisheries_25000.csv` from project root
5. Set asset name: `fisheries_25000`
6. Click "Upload"
7. Wait for processing (2-5 minutes)
8. Note your asset ID: `users/YOUR_USERNAME/fisheries_25000`

### Step 3: Configure GEE Scripts

Open `gee/satellite_generator.js` and `gee/test_single_month.js` and update:

```javascript
// UPDATE THIS LINE
var FISHERIES_ASSET = 'users/YOUR_USERNAME/fisheries_25000';
```

---

## Usage Instructions

### Phase 1: Inspect Fisheries Dataset

Verify the fisheries reference dataset:

```powershell
python src/inspect_fisheries.py
```

**Output**: `output/reports/fisheries_inspection_report.txt`

**Review the report** to confirm:
- 25,000 records present
- All 120 months represented
- All coordinates within study area (0°-30°N, 50°-100°E)
- Unique fisheries_record_id for each observation

---

### Phase 2-4: Review Documentation

Before running GEE extraction, review:

1. **Satellite sources**: `output/reports/satellite_source_report.md`
2. **Extraction methodology**: `output/reports/extraction_methodology.md`

These documents explain:
- Why NOAA OISST and MODIS Aqua were selected
- How point-based extraction works
- How missing values are handled
- Expected data quality and gaps

---

### Phase 5: Test Extraction (Single Month)

Test the extraction methodology on January 2015 (~208 records):

1. Open GEE Code Editor: https://code.earthengine.google.com/
2. Copy contents of `gee/test_single_month.js`
3. Paste into Code Editor
4. Update asset ID (see Step 3 above)
5. Click "Run"
6. Review Console output
7. Click "Tasks" tab
8. Click "Run" on export task
9. Wait for completion (1-2 minutes)
10. Download from Google Drive: `GEE_Satellite_Exports/satellite_test_jan2015.csv`
11. Inspect manually in Excel/Python

**What to check**:
- Coordinates match fisheries data
- Dates preserved (all January 2015)
- SST values plausible (22-32°C for this region)
- Chlorophyll values plausible (0.01-50 mg/m³, many null values OK)
- Missing values documented as null (not 0 or -999)

---

### Phase 6: Full Extraction (All Years)

Once test is successful, run full extraction:

1. Open GEE Code Editor
2. Copy contents of `gee/satellite_generator.js`
3. Paste into Code Editor
4. Update asset ID
5. Click "Run"
6. Review Console statistics
7. Click "Tasks" tab
8. **Run all 10 export tasks** (one per year: 2015-2024)
   - Click "Run" for each task
   - Each task takes 10-30 minutes
   - You can close the browser; tasks run server-side
9. Monitor task progress at: https://code.earthengine.google.com/ (Tasks tab)

**Export files** (created in Google Drive):
```
GEE_Satellite_Exports/
  ├── satellite_2015.csv
  ├── satellite_2016.csv
  ├── satellite_2017.csv
  ├── satellite_2018.csv
  ├── satellite_2019.csv
  ├── satellite_2020.csv
  ├── satellite_2021.csv
  ├── satellite_2022.csv
  ├── satellite_2023.csv
  └── satellite_2024.csv
```

10. **Download all CSV files** from Google Drive
11. Place files in: `output/satellite_exports/`

---

### Phase 7: Consolidate Exports

Merge annual exports into single dataset:

```powershell
python src/merge_satellite_exports.py
```

**Output**: `output/final/satellite_25000_rebuilt.csv`

**What it does**:
- Loads all 10 annual CSV files
- Concatenates into single DataFrame
- Validates record count (should be 25,000)
- Checks for duplicate IDs
- Reorders columns
- Saves final dataset

---

### Phase 8: Validate Final Dataset

Run comprehensive validation:

```powershell
python src/validate_satellite.py
```

**Output**: `output/reports/satellite_validation_report.txt`

**Validation checks**:
1. Record count (25,000)
2. Unique identifiers (no duplicates)
3. Temporal coverage (all 120 months)
4. Geographical boundaries (all within 0°-30°N, 50°-100°E)
5. Environmental value ranges (plausible SST and chlorophyll)
6. One-to-one matching (every fisheries ID has one satellite record)
7. Coordinate and date preservation

**Expected result**: All checks PASSED

---

## Output Dataset

### File

`output/final/satellite_25000_rebuilt.csv`

### Schema

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `satellite_record_id` | string | Unique satellite record identifier | SAT_2015-01-15_00042 |
| `fisheries_record_id` | int | Original fisheries observation ID | 1234 |
| `date` | string | Observation date (YYYY-MM-DD) | 2015-01-15 |
| `year` | int | Year | 2015 |
| `month` | int | Month (1-12) | 1 |
| `latitude` | float | Latitude (degrees North) | 15.234567 |
| `longitude` | float | Longitude (degrees East) | 67.891234 |
| `sea_surface_temperature_c` | float | SST in degrees Celsius | 28.45 |
| `chlorophyll_a_mg_m3` | float | Chlorophyll-a in mg/m³ | 0.234 |
| `sst_source` | string | SST data source | NOAA OISST v2.1 |
| `chlorophyll_source` | string | Chlorophyll data source | MODIS Aqua Ocean Color L3SMI |
| `sst_dataset_id` | string | GEE dataset ID for SST | NOAA/CDR/OISST/V2_1 |
| `chlorophyll_dataset_id` | string | GEE dataset ID for chlorophyll | NASA/OCEANDATA/MODIS-Aqua/L3SMI |

### Characteristics

- **Total Records**: 25,000
- **Temporal Coverage**: 2015-2024 (120 months)
- **Geographic Coverage**: 0°-30°N, 50°-100°E
- **SST Completeness**: ~99% (few missing values)
- **Chlorophyll Completeness**: 30-70% (many gaps due to clouds - this is normal)
- **File Size**: ~2-3 MB

### Missing Values

- **Represented as**: null (empty cells in CSV)
- **Do not interpret as**: 0, -999, or any numeric value
- **Cause**: Satellite sensor gaps (clouds, sun glint, calibration)
- **Handling**: Documented transparently, not filled or interpolated

---

## Validation

### Automated Validation

Run `python src/validate_satellite.py` to check:

- ✓ Correct record count (25,000)
- ✓ Unique satellite and fisheries IDs
- ✓ All 120 months represented (2015-2024)
- ✓ All coordinates within study area
- ✓ Plausible environmental values
- ✓ One-to-one fisheries matching
- ✓ Coordinates and dates preserved

### Manual Integration Test

Verify the dataset can be joined with fisheries:

```python
import pandas as pd

# Load datasets
fisheries = pd.read_csv('fisheries_25000.csv')
satellite = pd.read_csv('output/final/satellite_25000_rebuilt.csv')

# Join on fisheries_record_id
merged = fisheries.merge(satellite, on='fisheries_record_id', how='inner')

# Verify
assert len(merged) == 25000, "Record count mismatch"
print(f"Successfully joined {len(merged):,} records")

# Check coordinate preservation
assert (merged['lat'] == merged['latitude']).all(), "Latitude mismatch"
assert (merged['lon'] == merged['longitude']).all(), "Longitude mismatch"
print("Coordinates preserved correctly")
```

---

## Troubleshooting

### Issue: "Asset not found" in GEE

**Solution**: 
- Verify fisheries CSV upload completed successfully
- Check asset ID matches your username
- Wait a few minutes after upload before running script

### Issue: "Computation timed out" in GEE

**Solution**:
- This is rare for annual batches (~2,500 records each)
- Re-run the failed export task
- Reduce BATCH_SIZE if necessary

### Issue: Missing satellite export files

**Solution**:
- Check Google Drive folder: `GEE_Satellite_Exports`
- Verify all 10 export tasks completed (check Tasks tab)
- Re-run failed tasks

### Issue: Merge script can't find files

**Solution**:
```powershell
# Verify files exist
Get-ChildItem "output\satellite_exports\satellite_*.csv"

# If files are elsewhere, move them:
Move-Item "path\to\files\satellite_*.csv" "output\satellite_exports\"
```

### Issue: High chlorophyll missing rate (>70%)

**Explanation**: 
- This is NORMAL for ocean color satellite data
- Clouds block optical sensors frequently
- Tropical regions have higher cloud cover
- Indian Ocean monsoon seasons have extensive clouds
- Missing values should be preserved as null

### Issue: Validation fails on coordinate preservation

**Cause**: 
- Possible rounding during GEE export
- GEE geometry conversion issues

**Solution**:
- Check if differences are very small (< 0.000001°)
- Small floating-point differences may be acceptable
- Review first few mismatches manually

---

## Scientific Methodology

### Sampling Strategy

**Point-based extraction at fisheries coordinates**
- No independent satellite grid
- No random sampling
- Exact coordinate and date matching

### Why This Approach?

1. **Preserves spatial-temporal alignment**: Environmental conditions experienced by fishing vessels
2. **Maintains statistical independence**: Each observation remains independent
3. **Enables causal analysis**: Environmental predictors of fishing activity
4. **Transparent uncertainty**: Missing values explicitly documented

### Alternative Approaches NOT Used

- ❌ **Independent satellite grid**: Would not align with fisheries observations
- ❌ **Climatological values**: Loses temporal variability
- ❌ **Temporal interpolation**: Obscures actual observation gaps
- ❌ **Composite periods**: Loses daily temporal precision

### Data Quality Notes

**Sea Surface Temperature (SST)**:
- Source: NOAA OISST v2.1
- Reliability: Very high (gap-filled product)
- Expected missing: <1%
- Typical values: 24-32°C in study area

**Chlorophyll-a**:
- Source: MODIS Aqua L3SMI
- Reliability: Moderate (frequent gaps)
- Expected missing: 30-70%
- Typical values: 0.05-5 mg/m³ (open ocean), up to 20 mg/m³ (coastal)
- Gap causes: Clouds, sun glint, aerosols, algorithm failures

---

## References

### Google Earth Engine

- Documentation: https://developers.google.com/earth-engine/
- Code Editor: https://code.earthengine.google.com/
- Forum: https://groups.google.com/g/google-earth-engine-developers

### Satellite Data Sources

- NOAA OISST: https://www.ncei.noaa.gov/products/optimum-interpolation-sst
- MODIS Ocean Color: https://oceancolor.gsfc.nasa.gov/
- GEE Data Catalog: https://developers.google.com/earth-engine/datasets/

---

## Project Status

### Completed

- ✅ Project structure created
- ✅ Fisheries dataset inspected and validated
- ✅ Satellite sources documented
- ✅ Extraction methodology defined
- ✅ GEE scripts implemented (test and full)
- ✅ Python consolidation script
- ✅ Python validation script
- ✅ Comprehensive documentation

### Remaining Manual Steps

- ⏳ Upload fisheries CSV to GEE as Table Asset
- ⏳ Run test extraction (single month)
- ⏳ Run full extraction (10 annual batches)
- ⏳ Download exports from Google Drive
- ⏳ Run merge script
- ⏳ Run validation script
- ⏳ Verify final dataset

### Final Deliverable

`output/final/satellite_25000_rebuilt.csv` - 25,000 satellite environmental observations aligned with fisheries data (2015-2024)

---

## Support

For project-specific issues:
- Review this README
- Check `gee/README.md` for GEE-specific help
- Review methodology documents in `output/reports/`

For Google Earth Engine issues:
- GEE Forum: https://groups.google.com/g/google-earth-engine-developers
- GEE Documentation: https://developers.google.com/earth-engine/

---

**Project Version**: 1.0  
**Last Updated**: 2026-11-16  
**Status**: Development Complete - Ready for GEE Execution
