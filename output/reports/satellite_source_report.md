# Satellite Data Source Report

**Project:** Satellite Dataset Generation using Google Earth Engine  
**Study Period:** January 2015 - December 2024 (120 months)  
**Study Area:** 0°-30°N, 50°-100°E  
**Report Date:** 2026-11-16

---

## 1. Overview

This report documents the satellite data sources selected for extracting environmental measurements aligned with fisheries observations. All sources must:

1. Cover the complete study period (2015-2024)
2. Provide scientifically meaningful marine environmental data
3. Be available in Google Earth Engine
4. Have documented bands, units, and quality flags

---

## 2. Primary Data Sources

### 2.1 Sea Surface Temperature (SST)

**Dataset:** NOAA Optimum Interpolation Sea Surface Temperature (OISST) v2.1

- **GEE Dataset ID:** `NOAA/CDR/OISST/V2_1`
- **Provider:** NOAA National Centers for Environmental Information
- **Description:** Daily optimum interpolation SST on a 0.25-degree global grid
- **Temporal Coverage:** September 1981 - Present
- **Temporal Resolution:** Daily
- **Spatial Resolution:** 0.25 degrees (~25 km)
- **Latency:** ~1-2 days
- **Band Name:** `sst`
- **Units:** Degrees Celsius
- **Scale Factor:** 1.0 (values already in °C)
- **Valid Range:** -3°C to 45°C (typical ocean range: -2°C to 35°C)
- **Missing Values:** Masked

**Coverage Verification for Study Period (2015-2024):**
- ✓ **CONFIRMED:** Dataset fully covers 2015-2024
- ✓ Available since 1981, continuous daily coverage
- ✓ Covers global ocean including study area (0°-30°N, 50°-100°E)

**Quality Considerations:**
- Gap-free analysis using optimal interpolation
- Blends satellite IR and microwave SST with in-situ data
- Quality flags available (ice concentration, error estimates)
- Widely used in climate and marine research

**Extraction Strategy:**
- Extract daily SST value at exact fisheries observation date and coordinates
- Apply quality masks to identify low-confidence pixels
- Handle missing/masked values transparently

**References:**
- [GEE Catalog](https://developers.google.com/earth-engine/datasets/catalog/NOAA_CDR_OISST_V2_1)
- Huang et al. (2021). Improvements of the Daily Optimum Interpolation Sea Surface Temperature

---

### 2.2 Chlorophyll-a Concentration

**Dataset:** MODIS Aqua Ocean Color (Fallback - confirmed availability)

- **GEE Dataset ID:** `NASA/OCEANDATA/MODIS-Aqua/L3SMI`
- **Provider:** NASA Ocean Biology Processing Group
- **Description:** MODIS Aqua Level-3 Standard Mapped Image for ocean color
- **Temporal Coverage:** July 2002 - Present
- **Temporal Resolution:** Daily (8-day and monthly composites also available)
- **Spatial Resolution:** 4 km
- **Band Name:** `chlor_a`
- **Units:** mg/m³ (milligrams per cubic meter)
- **Scale Factor:** 1.0
- **Valid Range:** 0.001 - 100 mg/m³
- **Missing Values:** Common over clouds, high aerosol, sun glint

**Coverage Verification for Study Period (2015-2024):**
- ✓ **CONFIRMED:** Dataset fully covers 2015-2024
- ✓ Available since July 2002
- ✓ Covers study area (tropical Indian Ocean)

**Quality Considerations:**
- Daily coverage may have gaps due to clouds
- Quality flags indicate processing flags and error estimates
- Invalid pixels over land, ice, and high turbidity
- Gaps more common during monsoon seasons

**Extraction Strategy:**
- Extract daily chlorophyll-a at exact observation coordinates and date
- Apply quality masks (processing flags)
- Document missing values (return null, do not fabricate)
- Consider using 8-day composites if daily coverage is insufficient

**Alternative Consideration:**
- **Primary option investigated:** `COPERNICUS/MARINE/SATELLITE_OCEAN_COLOR/V6`
  - **Issue:** Need to verify actual availability for full 2015-2024 period
  - **Status:** MODIS Aqua confirmed; Copernicus to be verified during implementation

**References:**
- [GEE Catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_OCEANDATA_MODIS-Aqua_L3SMI)
- NASA Ocean Color Web: https://oceancolor.gsfc.nasa.gov/

---

## 3. Additional Useful Parameters (Future Enhancement)

The following parameters could enhance the dataset in future iterations:

### 3.1 Sea Surface Temperature Anomaly
- **Source:** Can be derived from OISST by computing climatology
- **Usefulness:** Identifies unusual thermal conditions affecting fish distribution

### 3.2 Suspended Particulate Matter (SPM) / Turbidity
- **Potential Source:** Derived from Sentinel-2 or Landsat (coastal areas)
- **Challenge:** 30m resolution may not cover all open-ocean fisheries locations
- **Alternative:** Derive turbidity proxy from ocean color bands

### 3.3 Ocean Color Quality Flags
- **Source:** Available in MODIS products
- **Usefulness:** Quality control for chlorophyll measurements
- **Implementation:** Include processing flags in metadata

### 3.4 Sea Surface Salinity
- **Potential Source:** SMAP/SMOS satellite missions
- **Temporal Coverage:** Limited (SMAP from 2015, coarse temporal resolution)
- **Consideration:** Low spatial resolution (~40-60 km)

### 3.5 Ocean Productivity Indices
- **Primary Production:** Can be estimated from chlorophyll + SST + light
- **Net Primary Production (NPP):** MOD17 (land), ocean NPP models
- **Status:** Requires additional modeling, not direct satellite observation

---

## 4. Data Source Limitations

### 4.1 Temporal Gaps
- **Chlorophyll-a:** Daily imagery frequently has missing pixels due to:
  - Cloud cover
  - Sun glint
  - High aerosol loading
  - Instrument calibration periods
- **Mitigation:** Document missing values; consider 8-day composites for gap-filling analysis

### 4.2 Spatial Resolution Mismatch
- **SST:** 0.25° (~25 km) - coarser than fisheries point locations
- **Chlorophyll:** 4 km - finer resolution but more gaps
- **Note:** Point extraction uses nearest pixel value

### 4.3 Quality Control
- **Ocean Color:** More prone to errors in:
  - Coastal waters (Case 2 waters)
  - High suspended sediment areas
  - Very oligotrophic (low chlorophyll) waters
- **Recommendation:** Include quality flags in output metadata

---

## 5. Extraction Methodology Summary

### 5.1 Point-Based Extraction
- Extract environmental measurements at **exact fisheries coordinates**
- Use **exact fisheries observation dates**
- One satellite record per fisheries observation
- Preserve fisheries_record_id for one-to-one matching

### 5.2 Temporal Matching
- **SST:** Daily observation on exact date
- **Chlorophyll:** Daily observation on exact date (with expected gaps)
- **No temporal interpolation:** Use actual satellite observation or null

### 5.3 Missing Value Handling
- **Strategy:** Preserve record, set environmental value to null
- **Do not:** Drop observations, fabricate values, or interpolate arbitrarily
- **Document:** Report missing value statistics per year/month

### 5.4 Quality Assurance
- Apply source-specific quality masks
- Document quality flag distributions
- Validate extracted value ranges against known oceanographic conditions

---

## 6. Implementation Checklist

- [x] Identify SST source with 2015-2024 coverage
- [x] Identify chlorophyll source with 2015-2024 coverage
- [x] Document band names and units
- [x] Document scale factors
- [x] Document quality flags
- [ ] Verify actual GEE dataset access
- [ ] Implement test extraction for single month (January 2015)
- [ ] Verify extracted value ranges
- [ ] Implement full extraction with quality control
- [ ] Document missing value statistics
- [ ] Validate final dataset

---

## 7. Expected Output Columns

| Column | Source | Units | Description |
|--------|--------|-------|-------------|
| `satellite_record_id` | Generated | - | Unique identifier for each satellite record |
| `date` | Fisheries | YYYY-MM-DD | Original observation date |
| `year` | Derived | - | Year extracted from date |
| `month` | Derived | - | Month extracted from date |
| `latitude` | Fisheries | Decimal degrees | Original latitude |
| `longitude` | Fisheries | Decimal degrees | Original longitude |
| `sea_surface_temperature_c` | NOAA OISST | °C | Daily SST |
| `chlorophyll_a_mg_m3` | MODIS Aqua | mg/m³ | Daily chlorophyll-a |
| `sst_source` | Metadata | - | "NOAA OISST v2.1" |
| `chlorophyll_source` | Metadata | - | "MODIS Aqua Ocean Color L3SMI" |
| `sst_dataset_id` | Metadata | - | GEE dataset ID |
| `chlorophyll_dataset_id` | Metadata | - | GEE dataset ID |
| `fisheries_record_id` | Fisheries | - | Original fisheries observation ID |

---

## 8. Conclusion

The selected satellite data sources provide comprehensive coverage of the study period (2015-2024) and study area (0°-30°N, 50°-100°E):

1. **NOAA OISST v2.1:** Reliable daily SST with complete coverage
2. **MODIS Aqua:** Daily chlorophyll-a with expected gaps due to clouds

Both sources are well-documented, scientifically validated, and available in Google Earth Engine. The extraction methodology ensures one-to-one alignment with fisheries observations while transparently handling missing satellite measurements.

**Next Steps:**
1. Implement single-month test extraction (Phase 5)
2. Validate extracted measurements
3. Proceed with full dataset generation (Phase 6)

---

**Document Version:** 1.0  
**Last Updated:** 2026-11-16  
**Author:** Satellite Dataset Generation System
