# Satellite Environmental Data Extraction Methodology

**Project:** Satellite Dataset Generation using Google Earth Engine  
**Study Period:** 2015-2024  
**Study Area:** 0°-30°N, 50°-100°E  
**Target Records:** 25,000  
**Document Version:** 1.0  
**Date:** 2026-11-16

---

## 1. Methodology Overview

This document defines the complete methodology for extracting satellite environmental measurements aligned with fisheries observations. The approach ensures:

1. **One-to-one correspondence** between fisheries and satellite records
2. **Preservation** of original spatial and temporal characteristics
3. **Transparency** in handling missing satellite measurements
4. **Reproducibility** through documented procedures
5. **Scientific validity** through quality-controlled sources

---

## 2. Core Principle: Fisheries-Driven Sampling

### 2.1 Reference Dataset

**The fisheries dataset is the ONLY reference for extraction locations and times.**

- **Do NOT generate** independent coordinates
- **Do NOT generate** independent dates
- **Do NOT create** random sampling points
- **Do NOT distribute** observations arbitrarily across years/months

### 2.2 Extraction Logic

```
FOR EACH fisheries observation:
    1. Read fisheries_record_id
    2. Read observation date
    3. Read latitude
    4. Read longitude
    5. Extract SST at (date, lat, lon)
    6. Extract Chlorophyll at (date, lat, lon)
    7. Create satellite record with fisheries_record_id
    8. Preserve missing measurements as null
END FOR

Result: Exactly one satellite record per fisheries observation
```

---

## 3. Geographical Framework

### 3.1 Official Study Area

**Boundaries:**
- Minimum Latitude: 0.0°N (Equator)
- Maximum Latitude: 30.0°N
- Minimum Longitude: 50.0°E
- Maximum Longitude: 100.0°E

**Region:** Northern Indian Ocean (Arabian Sea and Bay of Bengal)

### 3.2 Study Area Implementation in GEE

```javascript
// Define study area geometry
var studyArea = ee.Geometry.Rectangle({
  coords: [50, 0, 100, 30],
  proj: 'EPSG:4326',
  geodesic: false
});

// Visualize on map
Map.centerObject(studyArea, 5);
Map.addLayer(studyArea, {color: 'blue'}, 'Study Area');
```

### 3.3 Coordinate Validation

**Pre-extraction validation:**
1. Load fisheries dataset
2. Filter records where latitude is between 0° and 30°N
3. Filter records where longitude is between 50° and 100°E
4. Report any records outside boundaries
5. Proceed only with valid coordinates

**During extraction:**
- Use original fisheries coordinates without modification
- Do not round coordinates unnecessarily
- Preserve full coordinate precision
- Extract from nearest satellite pixel

### 3.4 Spatial Resolution Handling

Different satellite products have different spatial resolutions:

| Product | Resolution | Pixel Size | Extraction Method |
|---------|------------|------------|-------------------|
| NOAA OISST | 0.25° | ~25 km | Nearest neighbor |
| MODIS Aqua | 4 km | 4 km | Nearest neighbor |

**Implementation:**
```javascript
// Point-based extraction
var extractValue = function(image, point) {
  return image.reduceRegion({
    reducer: ee.Reducer.first(),  // Nearest pixel
    geometry: point,
    scale: 1000,  // 1km internal resolution
    maxPixels: 1
  });
};
```

---

## 4. Temporal Framework

### 4.1 Study Period

**Duration:** January 1, 2015 - December 31, 2024
- **Total Years:** 10
- **Total Months:** 120
- **Expected Records per Year:** ~2,500
- **Expected Records per Month:** ~208

### 4.2 Temporal Matching Strategy

**Principle: Use actual observation dates**

```
Fisheries Date → Satellite Date (same day)
```

**For Daily Products (SST, Chlorophyll):**
1. Parse fisheries observation date (YYYY-MM-DD)
2. Query satellite image for exact date
3. Extract measurement at observation coordinates
4. If no image exists for that date → null value

**No Temporal Interpolation:**
- Do not use measurements from different dates
- Do not average across multiple days
- Do not substitute nearby dates
- Document missing measurements

### 4.3 Date Parsing and Validation

```javascript
// Parse date from fisheries record
var parseDate = function(feature) {
  var dateString = feature.get('date');
  var date = ee.Date(dateString);
  
  // Validate date within study period
  var studyStart = ee.Date('2015-01-01');
  var studyEnd = ee.Date('2024-12-31');
  
  var isValid = date.gte(studyStart).and(date.lte(studyEnd));
  
  return feature.set('date_valid', isValid);
};
```

### 4.4 Monthly Distribution Preservation

The satellite dataset must preserve the exact monthly distribution of the fisheries dataset:

```
Fisheries Month Distribution → Satellite Month Distribution (identical)
```

**Verification:**
```python
# Post-extraction validation
fisheries_monthly = fisheries_df['date'].dt.to_period('M').value_counts()
satellite_monthly = satellite_df['date'].dt.to_period('M').value_counts()

assert (fisheries_monthly == satellite_monthly).all()
```

---

## 5. Environmental Parameter Extraction

### 5.1 Sea Surface Temperature (SST)

**Source:** NOAA OISST v2.1 (`NOAA/CDR/OISST/V2_1`)

**Extraction Process:**
```javascript
// Load SST image collection
var sstCollection = ee.ImageCollection('NOAA/CDR/OISST/V2_1')
  .filterBounds(studyArea)
  .filterDate('2015-01-01', '2024-12-31')
  .select('sst');

// Extract SST for specific date and location
var extractSST = function(feature) {
  var date = ee.Date(feature.get('date'));
  var point = feature.geometry();
  
  // Get SST image for this date
  var sstImage = sstCollection
    .filterDate(date, date.advance(1, 'day'))
    .first();
  
  // Extract value
  var sstValue = sstImage.reduceRegion({
    reducer: ee.Reducer.first(),
    geometry: point,
    scale: 1000
  }).get('sst');
  
  return feature.set({
    'sea_surface_temperature_c': sstValue,
    'sst_source': 'NOAA OISST v2.1',
    'sst_dataset_id': 'NOAA/CDR/OISST/V2_1'
  });
};
```

**Units:** Degrees Celsius (°C)  
**Scale Factor:** 1.0 (no conversion needed)  
**Expected Range:** -2°C to 35°C (tropical ocean)  
**Missing Values:** Possible over land or ice (should not occur in study area)

### 5.2 Chlorophyll-a Concentration

**Source:** MODIS Aqua L3SMI (`NASA/OCEANDATA/MODIS-Aqua/L3SMI`)

**Extraction Process:**
```javascript
// Load chlorophyll image collection
var chlCollection = ee.ImageCollection('NASA/OCEANDATA/MODIS-Aqua/L3SMI')
  .filterBounds(studyArea)
  .filterDate('2015-01-01', '2024-12-31')
  .select('chlor_a');

// Extract chlorophyll for specific date and location
var extractChlorophyll = function(feature) {
  var date = ee.Date(feature.get('date'));
  var point = feature.geometry();
  
  // Get chlorophyll image for this date
  var chlImage = chlCollection
    .filterDate(date, date.advance(1, 'day'))
    .first();
  
  // Extract value
  var chlValue = chlImage.reduceRegion({
    reducer: ee.Reducer.first(),
    geometry: point,
    scale: 1000
  }).get('chlor_a');
  
  return feature.set({
    'chlorophyll_a_mg_m3': chlValue,
    'chlorophyll_source': 'MODIS Aqua Ocean Color L3SMI',
    'chlorophyll_dataset_id': 'NASA/OCEANDATA/MODIS-Aqua/L3SMI'
  });
};
```

**Units:** mg/m³ (milligrams per cubic meter)  
**Scale Factor:** 1.0  
**Expected Range:** 0.01 - 10 mg/m³ (open ocean); up to 50 mg/m³ (coastal)  
**Missing Values:** Common due to clouds, sun glint, aerosols

### 5.3 Quality Control Measures

**Value Range Validation:**
```javascript
// Flag suspicious values
var validateValues = function(feature) {
  var sst = ee.Number(feature.get('sea_surface_temperature_c'));
  var chl = ee.Number(feature.get('chlorophyll_a_mg_m3'));
  
  var sst_valid = sst.gt(-2).and(sst.lt(35));
  var chl_valid = chl.gt(0).and(chl.lt(100));
  
  return feature.set({
    'sst_valid': sst_valid,
    'chl_valid': chl_valid
  });
};
```

**Quality Flags (Future Enhancement):**
- SST: Ice concentration, error estimates
- Chlorophyll: Processing flags, atmospheric correction quality

---

## 6. Missing Value Handling

### 6.1 Missing Value Philosophy

**Principle: Transparency over fabrication**

When a satellite measurement is unavailable:
1. **Preserve the observation record** (do not delete)
2. **Set environmental value to null**
3. **Document the reason** (if determinable)
4. **Report statistics** on missing values

**Do NOT:**
- Delete observations with missing satellite data
- Fabricate values
- Interpolate from nearby dates without documentation
- Use default or placeholder values

### 6.2 Causes of Missing Values

**Sea Surface Temperature (SST):**
- Rare (OISST is gap-filled by design)
- Possible over ice (not in study area)
- Possible during sensor calibration

**Chlorophyll-a:**
- Common (30-70% of daily images may have gaps)
- Cloud cover
- Sun glint
- High aerosol loading
- Instrument calibration
- Algorithm failure in turbid/coastal waters

### 6.3 Missing Value Implementation

```javascript
// Handle null values explicitly
var extractEnvironmental = function(feature) {
  var sst = extractSST(feature);
  var chl = extractChlorophyll(feature);
  
  // Check for null values
  var sstNull = ee.Algorithms.IsEqual(sst, null);
  var chlNull = ee.Algorithms.IsEqual(chl, null);
  
  return feature.set({
    'sea_surface_temperature_c': sst,
    'chlorophyll_a_mg_m3': chl,
    'sst_missing': sstNull,
    'chl_missing': chlNull
  });
};
```

### 6.4 Missing Value Reporting

**Post-extraction analysis:**
```python
# Count missing values
sst_missing = satellite_df['sea_surface_temperature_c'].isnull().sum()
chl_missing = satellite_df['chlorophyll_a_mg_m3'].isnull().sum()

# Calculate percentages
sst_missing_pct = sst_missing / len(satellite_df) * 100
chl_missing_pct = chl_missing / len(satellite_df) * 100

# Report by year/month
missing_by_month = satellite_df.groupby(['year', 'month']).agg({
    'sea_surface_temperature_c': lambda x: x.isnull().sum(),
    'chlorophyll_a_mg_m3': lambda x: x.isnull().sum()
})
```

---

## 7. Record Identification and Matching

### 7.1 Unique Record Identifiers

**Primary Key: `fisheries_record_id`**
- Preserves exact one-to-one correspondence
- Enables reliable joining
- Survives sorting and filtering

**Secondary Key: `satellite_record_id`**
- Generated unique identifier for satellite records
- Format: `SAT_{year}-{month:02d}-{day:02d}_{sequence}`
- Example: `SAT_2015-01-15_00042`

### 7.2 Record Generation Logic

```javascript
// Generate satellite record ID
var generateSatelliteID = function(feature, index) {
  var date = ee.Date(feature.get('date'));
  var dateStr = date.format('YYYY-MM-dd');
  var satID = ee.String('SAT_').cat(dateStr).cat('_').cat(ee.Number(index).format('%05d'));
  
  return feature.set({
    'satellite_record_id': satID,
    'fisheries_record_id': feature.get('fisheries_record_id')
  });
};
```

### 7.3 One-to-One Mapping Verification

**Requirement:**
```
For every fisheries_record_id in fisheries dataset,
there exists exactly one satellite_record_id in satellite dataset
with the same fisheries_record_id.
```

**Validation:**
```python
# Check one-to-one correspondence
fisheries_ids = set(fisheries_df['fisheries_record_id'])
satellite_ids = set(satellite_df['fisheries_record_id'])

assert fisheries_ids == satellite_ids, "ID mismatch detected"

# Check for duplicates
assert satellite_df['fisheries_record_id'].is_unique
assert satellite_df['satellite_record_id'].is_unique
```

---

## 8. Export Strategy

### 8.1 Batch Processing

**Challenge:** GEE has computational limits for large-scale processing

**Solution:** Annual batch exports
- 2015: ~2,500 records → `satellite_2015.csv`
- 2016: ~2,500 records → `satellite_2016.csv`
- ...
- 2024: ~2,500 records → `satellite_2024.csv`

### 8.2 Export Configuration

```javascript
// Export annual batch
var exportYear = function(year) {
  var yearStart = ee.Date.fromYMD(year, 1, 1);
  var yearEnd = yearStart.advance(1, 'year');
  
  var yearData = processedData.filter(
    ee.Filter.date(yearStart, yearEnd)
  );
  
  Export.table.toDrive({
    collection: yearData,
    description: 'satellite_' + year,
    folder: 'GEE_Satellite_Exports',
    fileNamePrefix: 'satellite_' + year,
    fileFormat: 'CSV'
  });
};

// Export all years
for (var year = 2015; year <= 2024; year++) {
  exportYear(year);
}
```

### 8.3 Export Parameters

- **Format:** CSV
- **Destination:** Google Drive
- **Folder:** `GEE_Satellite_Exports`
- **Compression:** None (for easy inspection)
- **CRS:** WGS84 (EPSG:4326)

---

## 9. Post-Export Consolidation

### 9.1 Merging Annual Exports

**Script:** `src/merge_satellite_exports.py`

**Process:**
```python
import pandas as pd
import glob

# Load all annual exports
export_files = sorted(glob.glob('output/satellite_exports/satellite_*.csv'))
dfs = [pd.read_csv(f) for f in export_files]

# Concatenate
satellite_df = pd.concat(dfs, ignore_index=True)

# Validate
assert len(satellite_df) == 25000, f"Expected 25000, got {len(satellite_df)}"
assert satellite_df['fisheries_record_id'].is_unique

# Save final dataset
satellite_df.to_csv('output/final/satellite_25000_rebuilt.csv', index=False)
```

### 9.2 Column Order

Final CSV column order:
```
1.  satellite_record_id
2.  date
3.  year
4.  month
5.  latitude
6.  longitude
7.  sea_surface_temperature_c
8.  chlorophyll_a_mg_m3
9.  sst_source
10. chlorophyll_source
11. sst_dataset_id
12. chlorophyll_dataset_id
13. fisheries_record_id
```

---

## 10. Validation Framework

### 10.1 Validation Checks

**Post-processing validation script:** `src/validate_satellite.py`

**Checks:**
1. **Record count:** Exactly 25,000 records
2. **Unique IDs:** No duplicate satellite_record_id or fisheries_record_id
3. **Date range:** All dates within 2015-2024
4. **Geography:** All coordinates within study area
5. **Monthly coverage:** All 120 months represented
6. **Coordinate preservation:** Matches fisheries coordinates
7. **Value ranges:** SST and chlorophyll within plausible ranges
8. **Missing values:** Documented and reported

### 10.2 Integration Test

**Join with fisheries dataset:**
```python
# Merge on fisheries_record_id
merged = fisheries_df.merge(
    satellite_df,
    on='fisheries_record_id',
    how='inner',
    suffixes=('_fish', '_sat')
)

# Verify all records matched
assert len(merged) == 25000

# Verify coordinate preservation
assert (merged['lat'] == merged['latitude']).all()
assert (merged['lon'] == merged['longitude']).all()

# Verify date preservation
assert (merged['date_fish'] == merged['date_sat']).all()
```

---

## 11. Methodology Summary

| Aspect | Approach |
|--------|----------|
| **Sampling Strategy** | Point-based extraction at fisheries coordinates |
| **Temporal Matching** | Exact date matching (daily observations) |
| **Spatial Coverage** | 0°-30°N, 50°-100°E (Arabian Sea & Bay of Bengal) |
| **Temporal Coverage** | 2015-2024 (120 months) |
| **Target Records** | 25,000 (one per fisheries observation) |
| **SST Source** | NOAA OISST v2.1 (daily, 0.25°) |
| **Chlorophyll Source** | MODIS Aqua L3SMI (daily, 4km) |
| **Missing Values** | Preserved as null, documented |
| **Quality Control** | Range validation, quality flags |
| **Record Matching** | fisheries_record_id (one-to-one) |
| **Export Strategy** | Annual batches to Google Drive |
| **Validation** | Automated checks on final dataset |

---

## 12. Scientific Justification

### 12.1 Why This Approach?

**1. Preserves Spatial-Temporal Alignment**
- Environmental conditions experienced by fishing vessels
- No artificial sampling introduces bias

**2. Maintains Statistical Independence**
- Fisheries observations are independent
- Satellite measurements preserve this independence

**3. Enables Causal Analysis**
- Environmental conditions as predictors of fishing activity
- Fish distribution models

**4. Transparent Uncertainty**
- Missing values explicitly documented
- No hidden interpolation or substitution

### 12.2 Alternative Approaches (Not Used)

**❌ Independent Satellite Grid**
- Would not align with fisheries observations
- Spatial mismatch introduces noise

**❌ Climatological Values**
- Loses temporal variability
- Cannot detect anomalies or trends

**❌ Temporal Interpolation**
- Obscures actual observation gaps
- Introduces artificial correlation

**❌ Composite Periods (Weekly/Monthly)**
- Loses daily temporal precision
- Masks sub-weekly variability

---

## 13. Reproducibility

### 13.1 Required Information for Reproduction

1. **Fisheries dataset:** `fisheries_25000.csv`
2. **GEE scripts:** `gee/satellite_generator.js`
3. **Configuration:** `config/config.py`
4. **Google Earth Engine account** with access to:
   - NOAA/CDR/OISST/V2_1
   - NASA/OCEANDATA/MODIS-Aqua/L3SMI
5. **Python environment:** `requirements.txt`

### 13.2 Reproduction Steps

```
1. Upload fisheries CSV to GEE as Table Asset
2. Update asset ID in satellite_generator.js
3. Run satellite_generator.js in GEE Code Editor
4. Wait for export tasks to complete (~10 tasks)
5. Download exports from Google Drive
6. Place in output/satellite_exports/
7. Run: python src/merge_satellite_exports.py
8. Run: python src/validate_satellite.py
9. Final output: output/final/satellite_25000_rebuilt.csv
```

---

## 14. Conclusion

This methodology ensures scientifically rigorous extraction of satellite environmental measurements that are spatially and temporally aligned with fisheries observations. The approach prioritizes:

1. **Accuracy:** Original dates and coordinates preserved
2. **Completeness:** All 25,000 observations included
3. **Transparency:** Missing values documented
4. **Reproducibility:** Fully documented procedure
5. **Scientific Validity:** Quality-controlled sources

The resulting dataset enables robust analysis of environmental influences on fisheries activity and fish distribution across the northern Indian Ocean from 2015-2024.

---

**Document Status:** Final  
**Version:** 1.0  
**Last Updated:** 2026-11-16  
**Next Phase:** Implement test extraction (Phase 5)
