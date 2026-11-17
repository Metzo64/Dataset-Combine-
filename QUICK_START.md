# Quick Start Guide

This is a simplified guide to get you started quickly. For detailed information, see `README.md`.

---

## Prerequisites

1. ✅ Python 3.8+ installed
2. ⏳ Google Earth Engine account (register at https://earthengine.google.com/)
3. ⏳ Google Drive account

---

## Installation (5 minutes)

```powershell
# Navigate to project directory
cd "D:\Projects\Projects\maj maj"

# Install Python dependencies
pip install pandas numpy

# Verify installation
python -c "import pandas, numpy; print('Ready!')"
```

---

## Phase 1: Inspect Fisheries Data (2 minutes)

```powershell
python src/inspect_fisheries.py
```

**Check output**: `output/reports/fisheries_inspection_report.txt`

**Expected result**: "ALL CHECKS PASSED"

---

## Phase 2: Google Earth Engine Setup (10 minutes + approval wait)

### Register for GEE
1. Go to: https://earthengine.google.com/
2. Click "Sign Up"
3. Use your Google account
4. Wait for approval (1-2 days, sometimes instant)

### Upload Fisheries Dataset
1. Go to: https://code.earthengine.google.com/
2. Click "Assets" tab (left panel)
3. Click "NEW" → "CSV file"
4. Select `fisheries_25000.csv`
5. Name: `fisheries_25000`
6. Click "Upload"
7. Wait ~5 minutes
8. Note your asset ID: `users/YOUR_USERNAME/fisheries_25000`

---

## Phase 3: Configure GEE Scripts (2 minutes)

Open both files and update the asset ID:
- `gee/satellite_generator.js`
- `gee/test_single_month.js`

Find this line:
```javascript
var FISHERIES_ASSET = 'users/YOUR_USERNAME/fisheries_25000';
```

Replace `YOUR_USERNAME` with your actual GEE username.

---

## Phase 4: Test Extraction (5 minutes)

1. Open GEE Code Editor: https://code.earthengine.google.com/
2. Copy contents of `gee/test_single_month.js`
3. Paste into Code Editor
4. Click "Run"
5. Click "Tasks" tab
6. Click "Run" on the export task
7. Wait ~2 minutes
8. Download from Google Drive: `GEE_Satellite_Exports/satellite_test_jan2015.csv`
9. Open in Excel to verify data looks good

**What to check**:
- ~208 rows (January 2015)
- Coordinates are valid (0-30°N, 50-100°E)
- SST values reasonable (22-32°C)
- Many chlorophyll values may be null (this is OK!)

---

## Phase 5: Full Extraction (2-5 hours)

1. Open GEE Code Editor
2. Copy contents of `gee/satellite_generator.js`
3. Paste into Code Editor
4. Click "Run"
5. Click "Tasks" tab
6. **Run all 10 tasks** (click "Run" for each):
   - satellite_2015
   - satellite_2016
   - ... (all 10 years)
7. Wait for all to complete (10-30 min each)
8. Go to Google Drive
9. Download all 10 CSV files from `GEE_Satellite_Exports` folder
10. Place in: `output/satellite_exports/`

**You can close the browser - tasks run in the background!**

Check progress at: https://code.earthengine.google.com/ (Tasks tab)

---

## Phase 6: Consolidate Data (1 minute)

```powershell
python src/merge_satellite_exports.py
```

**Creates**: `output/final/satellite_25000_rebuilt.csv`

---

## Phase 7: Validate Dataset (1 minute)

```powershell
python src/validate_satellite.py
```

**Check output**: `output/reports/satellite_validation_report.txt`

**Expected result**: "ALL VALIDATION CHECKS PASSED"

---

## Done! 🎉

Your final dataset is ready:
- **File**: `output/final/satellite_25000_rebuilt.csv`
- **Records**: 25,000
- **Columns**: 13
- **Coverage**: 2015-2024 (120 months)
- **Area**: 0°-30°N, 50°-100°E

---

## Quick Test of Final Dataset

```python
import pandas as pd

# Load datasets
fisheries = pd.read_csv('fisheries_25000.csv')
satellite = pd.read_csv('output/final/satellite_25000_rebuilt.csv')

# Join them
merged = fisheries.merge(satellite, on='fisheries_record_id')

print(f"Successfully joined {len(merged):,} records!")
print(f"\nSample data:")
print(merged[['date', 'lat', 'lon', 'sea_surface_temperature_c', 'chlorophyll_a_mg_m3']].head())
```

---

## Troubleshooting

### Can't find pandas module
```powershell
pip install pandas numpy
```

### GEE says "Asset not found"
- Wait a few minutes after upload
- Check asset ID matches your username
- Verify upload completed in Assets tab

### Missing export files
- Check Google Drive folder: `GEE_Satellite_Exports`
- Verify all tasks completed (green checkmark in Tasks tab)
- Re-run failed tasks if needed

### Merge script fails
```powershell
# Check files exist
Get-ChildItem "output\satellite_exports\*.csv"

# Should show 10 files: satellite_2015.csv through satellite_2024.csv
```

### Many null chlorophyll values
**This is NORMAL!** Ocean color satellites often miss data due to clouds. Typical completion: 30-70%.

---

## Need More Details?

- **Full documentation**: README.md
- **GEE help**: gee/README.md
- **Methodology**: output/reports/extraction_methodology.md
- **Data sources**: output/reports/satellite_source_report.md

---

## Summary of Time Required

| Step | Your Time | Wait Time | Total |
|------|-----------|-----------|-------|
| Install Python packages | 2 min | 2 min | 2 min |
| Inspect fisheries | 1 min | 1 min | 1 min |
| Register for GEE | 3 min | 1-2 days* | 1-2 days |
| Upload fisheries CSV | 2 min | 5 min | 7 min |
| Configure scripts | 2 min | - | 2 min |
| Test extraction | 3 min | 2 min | 5 min |
| Full extraction | 5 min | 100-300 min | 2-5 hours |
| Download exports | 5 min | - | 5 min |
| Consolidate & validate | 2 min | 2 min | 2 min |
| **TOTAL** | **25 min** | **2-5 hours** | **1-3 days** |

*GEE approval usually faster, sometimes instant

**Most of the time is automatic processing - you just start tasks and wait!**

---

**Ready to start? Begin with Phase 1!**

```powershell
python src/inspect_fisheries.py
```
