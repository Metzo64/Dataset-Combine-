# Dataset Combine Project - Context

**Last Updated**: 2026-11-17  
**Project Status**: Satellite extraction complete, quality assessment in progress

---

## Project Overview

This project combines fisheries vessel observations with satellite-derived environmental measurements to enable analysis of fishing activity in relation to oceanographic conditions.

**Goal**: Create a unified dataset matching 25,000 fisheries observations with satellite-derived sea surface temperature (SST) and chlorophyll-a measurements from the same dates and locations.

**Approach**: 
1. Fisheries dataset (`fisheries_25000.csv`) serves as the reference
2. Extract satellite data from Google Earth Engine (GEE) for each fisheries observation
3. Combine datasets based on date and coordinates
4. Validate data quality and address missing/anomalous values

---

## Study Area and Period

### Geographic Coverage
- **Region**: Indian Ocean
- **Latitude**: 0°N to 30°N
- **Longitude**: 50°E to 100°E
- **Coverage**: Tropical Indian Ocean, Bay of Bengal, Arabian Sea, Gulf of Oman

### Temporal Coverage
- **Period**: January 2015 to December 2024
- **Duration**: 10 years (120 months)
- **Observations**: 25,000 discrete fishing events

---

## Dataset Requirements

### Target Outputs

**1. Fisheries Dataset** (`fisheries_25000.csv`)
- 25,000 fishing vessel observations
- Columns include: fisheries_record_id, date, lat, lon, vessel details, gear type, hours, etc.
- Already complete and validated

**2. Satellite Dataset** (`satellite_25000.csv`)
- 25,000 satellite observations
- One-to-one match with fisheries observations
- Exact same dates and coordinates as fisheries dataset
- Must follow specific 12-column schema (see below)

### Matching Strategy

The satellite dataset is built to match the fisheries dataset:
- **Date matching**: Extract satellite data for the exact fisheries observation date
- **Coordinate matching**: Sample satellite pixels at fisheries observation coordinates
- **One-to-one**: Each fisheries record gets exactly one satellite record
- **Preservation**: All 25,000 fisheries records must have corresponding satellite records

---

## Satellite Variables

### Environmental Measurements

**ONLY TWO VARIABLES**:

1. **Sea Surface Temperature (SST)**
   - Units: Degrees Celsius (°C)
   - Expected range: 15-35°C (tropical Indian Ocean)
   - Source: NOAA OISST v2.1

2. **Chlorophyll-a Concentration**
   - Units: milligrams per cubic meter (mg/m³)
   - Expected range: 0.05-25 mg/m³ (oligotrophic to eutrophic)
   - Source: Copernicus Marine Ocean Color

**DO NOT ADD**:
- Salinity
- Ocean currents
- Wind speed
- Wave height
- Turbidity
- Sea surface height
- Any other variables

---

## Google Earth Engine (GEE) Data Sources

### 1. Sea Surface Temperature (SST)

**Dataset**: `NOAA/CDR/OISST/V2_1`
- **Name**: NOAA Optimum Interpolation Sea Surface Temperature (OISST) v2.1
- **Band**: `sst`
- **Resolution**: 0.25° (~25 km)
- **Temporal**: Daily
- **Scale Factor**: **0.01** (CRITICAL!)

**CRITICAL SST SCALING**:
```python
# CORRECT - Scale the IMAGE before sampling
sst_image_scaled = sst_image.multiply(0.01)
sst_value = sst_image_scaled.reduceRegion(...).get('sst')

# WRONG - Scaling after sampling doesn't persist through export
sst_value_raw = sst_image.reduceRegion(...).get('sst')
sst_value = ee.Number(sst_value_raw).multiply(0.01)  # This won't be in the exported CSV!
```

The raw `sst` band stores values like 2835 which represent 28.35°C. The 0.01 scale factor MUST be applied to the image pixels BEFORE sampling, otherwise GEE exports will contain unscaled values.

### 2. Chlorophyll-a

**Dataset**: `COPERNICUS/MARINE/SATELLITE_OCEAN_COLOR/V6`
- **Name**: Copernicus Marine Environment Monitoring Service (CMEMS) Global Ocean Color
- **Band**: `chlor_a` (NOT 'CHL')
- **Resolution**: 4 km
- **Temporal**: Daily
- **Scale Factor**: None (values already in mg/m³)

**Band Name**: The correct band name is `chlor_a`. Do NOT use `CHL` or any other band name.

---

## Current Extraction Status

### Completed Work

✅ **Full extraction completed** (2026-11-17)
- 25,000 satellite observations extracted
- All 10 GEE export tasks completed successfully (2015-2024, 2,500 records each)
- Execution time: ~6 minutes
- No task failures

✅ **Data matching verified**
- All 25,000 records match fisheries observations by date and coordinates
- 100% coordinate preservation (lat/lon match exactly)
- 100% date preservation (dates match exactly)
- All 120 months (2015-2024) represented

✅ **SST scaling corrected**
- Initial extraction had unscaled SST (2001-2900 instead of 20-29°C)
- Fixed by applying 0.01 scale factor to IMAGE before sampling
- Final SST range: 15.16-35.71°C (properly scaled)

✅ **Schema corrections applied**
- Added `satellite_record_id` column (format: SAT_YYYY-MM-DD_N)
- Removed temporary `fisheries_record_id` column
- Removed temporary `date_parsed` column
- Reordered columns to match original satellite schema

✅ **Files created**
- `output/final/satellite_25000.csv` - Final corrected satellite dataset
- `output/final/satellite_25000_rebuilt.csv` - Intermediate version (has extra columns)

---

## Current Data Quality Issues

### 1. Chlorophyll-a Missing Values

**Status**: 13,868 / 25,000 records missing (55.47%)

**Temporal Distribution**:
- 2015: 77.4% missing (worst year)
- 2019-2021: 40-46% missing (best years)
- 2022-2024: 54-55% missing

**Monthly Pattern**:
- July: 64.8% missing (monsoon season, heavy clouds)
- February-March: 51-52% missing (best clarity)

**Preliminary Assessment**:
- Daily ocean color data naturally has 30-60% missing rate due to clouds
- Missing values represent "no valid measurement" not extraction errors
- BUT: 55% is on the high end and requires further investigation

**Questions to Investigate**:
1. Are there recoverable observations in the source dataset that failed to extract?
2. Is the temporal matching too strict (same-day only)?
3. Would a small temporal window (±1-2 days) recover valid measurements?
4. Are there masked pixels that could be unmasked?
5. Is sensor availability an issue in certain periods?

**Current Decision**: KEEP as NULL until investigation complete

### 2. SST Missing Values

**Status**: 313 / 25,000 records missing (1.25%)

**Distribution**: Evenly spread across years and geography

**Preliminary Assessment**:
- <2% missing is excellent for daily satellite data
- Likely due to pixel-level cloud cover or edge-of-swath gaps

**Questions to Investigate**:
1. Are these truly unavailable in NOAA OISST (which is gap-filled)?
2. Did extraction fail for technical reasons?
3. Can these be recovered from the source?

**Current Decision**: KEEP as NULL until investigation complete

### 3. High SST Values (>35°C)

**Status**: 97 records with SST > 35°C (0.39% of dataset)

**Range**: 35.01-35.71°C

**Geographic Pattern**:
- ALL concentrated in Northern Arabian Sea / Gulf of Oman
- Latitude: 24.2-28.6°N
- Longitude: 50.1-53.3°E (clustered around 51°E)

**Temporal Pattern**:
- 95% occur in August (92 records)
- Remaining 5% in early September
- Years: 2016-2017, 2022-2024

**Scientific Plausibility**:
- Shallow enclosed seas (Persian Gulf, Gulf of Oman) can reach 35-36°C in summer
- August is peak warming month for northern Arabian Sea
- Geographic and temporal clustering suggests real phenomena, not random errors

**HOWEVER**: Requires verification against original source data

**Questions to Investigate**:
1. Do NOAA OISST source pixels actually contain these values?
2. Is this a known characteristic of NOAA OISST in enclosed seas?
3. Are these values consistent across multiple satellite sensors?
4. Do nearby pixels show similar values or are these isolated?

**Current Decision**: VALUES RETAINED but flagged for verification

---

## Approved Remediation Principles

### Core Principles

1. **Never fabricate measurements**
   - Do NOT replace missing values with zero
   - Do NOT use arbitrary averages or medians
   - Do NOT interpolate without scientific justification

2. **Investigate before acting**
   - Check source data availability first
   - Identify extraction failures vs. true data gaps
   - Distinguish recoverable from unrecoverable missing values

3. **Re-extract when valid source exists**
   - If original GEE source has valid data that wasn't extracted → re-extract
   - If extraction parameters were too strict → relax appropriately
   - If masking was too aggressive → unmask if scientifically justified

4. **Temporal interpolation constraints**
   - ONLY consider for small gaps (e.g., 1-3 days)
   - ONLY for variables with high temporal autocorrelation (e.g., SST, not chlorophyll)
   - ONLY after confirming source data is truly unavailable
   - MUST be scientifically defensible for the intended analysis
   - Requires explicit gap limit and interpolation method documentation

5. **Keep unresolved values as NULL**
   - If no valid source data exists → keep NULL
   - If recovery method is not scientifically defensible → keep NULL
   - NULL represents "no valid measurement" which is scientifically valid

6. **Preserve all 25,000 records**
   - Do NOT drop records due to missing satellite data
   - Fisheries observations remain valid even without satellite data
   - One-to-one matching must be maintained

7. **Handle anomalous values carefully**
   - Do NOT automatically remove high/low values
   - Investigate potential causes first
   - Remove ONLY if proven to be errors
   - Document all removals with justification

8. **Do not change methodology without approval**
   - Current approach: daily observations, same-day matching
   - Do NOT switch to 8-day composites without explicit approval
   - Do NOT switch to monthly composites
   - Do NOT add temporal buffers without approval

---

## Final Satellite Schema

### Required Columns (12 total, in order)

```
1.  satellite_record_id          (string, format: SAT_YYYY-MM-DD_N)
2.  date                          (string, format: YYYY-MM-DD)
3.  year                          (integer, 2015-2024)
4.  month                         (integer, 1-12)
5.  latitude                      (float, 0.0-30.0)
6.  longitude                     (float, 50.0-100.0)
7.  sea_surface_temperature_c     (float, °C, can be NULL)
8.  chlorophyll_a_mg_m3           (float, mg/m³, can be NULL)
9.  sst_source                    (string, "NOAA OISST v2.1")
10. chlorophyll_source            (string, "Copernicus Marine Ocean Color")
11. sst_dataset_id                (string, "NOAA/CDR/OISST/V2_1")
12. chlorophyll_dataset_id        (string, "COPERNICUS/MARINE/SATELLITE_OCEAN_COLOR/V6")
```

### Important Notes

**satellite_record_id**:
- Format: `SAT_YYYY-MM-DD_N` where N is sequential within each date
- Example: `SAT_2015-01-01_0`, `SAT_2015-01-01_1`, etc.
- MUST be unique for all 25,000 records
- Deterministic (same input produces same IDs)

**fisheries_record_id**:
- Was used during extraction for matching
- IS NOT part of the final satellite schema
- Remove from final satellite dataset
- Keep in fisheries dataset for joining/analysis

**Missing values**:
- Represented as empty/NULL in CSV
- Do NOT use 0, -999, or other sentinel values
- NULL means "no valid measurement available"

**Column order**:
- MUST match the order shown above
- Tools/scripts may depend on column order
- Use the original `satellite_25000.csv` as reference

---

## Project Structure

```
Dataset-Combine/
├── config/
│   └── config.py                    # GEE dataset configurations, study area
├── src/
│   ├── run_gee_extraction.py        # Main extraction script (Python API)
│   ├── merge_satellite_exports.py   # Merge GEE exports into single CSV
│   ├── validate_satellite.py        # Validation checks
│   ├── gee_auth.py                  # GEE authentication helper
│   ├── check_task_status.py         # Monitor GEE task progress
│   ├── download_gee_exports.py      # Download exports from Google Drive
│   └── inspect_fisheries.py         # Fisheries dataset analysis
├── gee/
│   ├── satellite_generator.js       # Original JavaScript implementation (deprecated)
│   └── test_single_month.js         # JavaScript test script (deprecated)
├── output/
│   ├── final/
│   │   ├── satellite_25000.csv           # FINAL corrected dataset
│   │   └── satellite_25000_rebuilt.csv   # Intermediate (has extra columns)
│   ├── reports/
│   │   ├── satellite_validation_report.txt
│   │   ├── fisheries_inspection_report.txt
│   │   └── extraction_methodology.md
│   └── satellite_exports/            # GEE export CSVs (git-ignored)
├── logs/
│   └── gee_extraction_*.log          # Extraction run logs
├── fisheries_25000.csv               # Reference fisheries dataset (25K records)
├── satellite_25000.csv               # Original satellite schema reference
├── requirements.txt                  # Python dependencies
├── .gitignore                        # Git ignore patterns
├── README.md                         # Project overview
├── PROJECT_CONTEXT.md                # This file
├── NEXT_STEPS.md                     # Continuation guide
└── [Additional documentation files]
```

### Key Files

**Data Files**:
- `fisheries_25000.csv` - Fisheries observations (reference dataset)
- `satellite_25000.csv` - Original satellite dataset (schema reference)
- `output/final/satellite_25000.csv` - **FINAL corrected satellite dataset**
- `output/final/satellite_25000_rebuilt.csv` - Intermediate version (has extra columns)

**Scripts**:
- `src/run_gee_extraction.py` - Main extraction script
- `src/merge_satellite_exports.py` - Merge GEE exports
- `src/validate_satellite.py` - Validate final dataset
- `create_final_satellite.py` - Generate corrected final file
- `diagnose_satellite_quality.py` - Quality assessment script

**Documentation**:
- `QUALITY_ASSESSMENT_REPORT.md` - Comprehensive quality assessment
- `FINAL_DATASET_REPORT.md` - Final dataset validation report
- `SCALING_FIX_STATUS.md` - SST scaling issue documentation

---

## Technology Stack

### Required Software

**Python**: 3.8 or higher
- pandas (data manipulation)
- numpy (numerical operations)
- earthengine-api (Google Earth Engine Python API)
- google-auth, google-auth-oauthlib (GEE authentication)

**Google Earth Engine**: 
- Account with access to GEE Python API
- Authenticated via `earthengine authenticate` command

**Git**: For version control and GitHub sync

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Authenticate with Google Earth Engine (one-time)
earthengine authenticate
```

---

## Pending Work

### Priority 1: Investigation

1. **Investigate Chlorophyll Missing Values** (13,868 / 55.5%)
   - Check GEE source availability for missing dates/locations
   - Identify if extractions failed due to masking/QC filters
   - Evaluate if small temporal window (±1-2 days) would recover valid measurements
   - Document findings and propose remediation strategy

2. **Investigate SST Missing Values** (313 / 1.25%)
   - Verify NOAA OISST availability for missing dates/locations
   - Check if extraction code failed for specific conditions
   - Attempt re-extraction if source data exists

3. **Verify High SST Values** (97 records, 35-36°C)
   - Query NOAA OISST source directly for affected pixels
   - Check if values are consistent across multiple dates/nearby pixels
   - Compare with other SST products (MODIS, VIIRS) if available
   - Make retention/removal decision based on evidence

### Priority 2: Remediation

4. **Remediate Recoverable Missing Values**
   - Re-extract if valid source data exists
   - Apply scientifically defensible recovery methods
   - Document all changes and justifications

5. **Finalize Satellite Dataset**
   - Apply approved remediations
   - Update `output/final/satellite_25000.csv`
   - Run final validation
   - Generate updated validation reports

### Priority 3: Dataset Combination

6. **Combine Fisheries and Satellite Datasets**
   - Join fisheries_25000.csv with satellite_25000.csv
   - Verify one-to-one matching
   - Create combined analysis dataset
   - Document combined dataset schema

7. **Final Independent Validation**
   - External validation of combined dataset
   - Check for any remaining issues
   - Generate final quality report

---

## Important Commands

### GEE Extraction

```bash
# Test extraction (209 records from January 2015)
python src/run_gee_extraction.py --test

# Full extraction (25,000 records, all years)
python src/run_gee_extraction.py --full

# Check GEE task status
python src/check_task_status.py
```

### Data Processing

```bash
# Merge GEE exports into single CSV
python src/merge_satellite_exports.py

# Validate satellite dataset
python src/validate_satellite.py

# Create final corrected dataset
python create_final_satellite.py

# Run quality diagnostics
python diagnose_satellite_quality.py
```

### Quality Checks

```bash
# Quick SST scaling check
python check_sst_scaling.py

# Check for duplicates
python check_duplicates.py

# Verify final dataset
python verify_final.py
```

---

## Warnings and Constraints

### Do NOT

❌ Modify `fisheries_25000.csv` (reference dataset)  
❌ Rerun full GEE extraction without justification  
❌ Change daily observation methodology without approval  
❌ Add variables beyond SST and chlorophyll-a  
❌ Fabricate or impute missing values without investigation  
❌ Remove high/low values without verification  
❌ Force-push to GitHub  
❌ Commit sensitive credentials or API keys  

### DO

✅ Investigate before acting  
✅ Document all changes and decisions  
✅ Preserve all 25,000 records  
✅ Keep unresolved missing values as NULL  
✅ Verify anomalies before removal  
✅ Follow approved remediation principles  
✅ Maintain one-to-one fisheries-satellite matching  
✅ Use the final 12-column schema  

---

## Contact and Continuation

This project is designed to be continued by other AI coding assistants or developers.

**For Continuation**:
1. Read this file completely
2. Read `NEXT_STEPS.md` for immediate tasks
3. Review `QUALITY_ASSESSMENT_REPORT.md` for quality issues
4. Check `logs/` for recent extraction results
5. Verify `output/final/satellite_25000.csv` is present

**For Questions**:
- Check documentation in `output/reports/`
- Review validation reports
- Inspect extraction logs
- Reference GEE dataset documentation

---

**Document Version**: 1.0  
**Last Extraction**: 2026-11-17 09:09 UTC  
**Dataset Status**: Complete, quality assessment in progress  
**Next Action**: Investigate missing values and verify anomalies
