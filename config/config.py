"""
Configuration file for Satellite Dataset Generation Project
"""

import os

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Input files
FISHERIES_CSV = os.path.join(PROJECT_ROOT, "fisheries_25000.csv")
OLD_SATELLITE_CSV = os.path.join(PROJECT_ROOT, "satellite_25000.csv")

# Output directories
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
EXPORTS_DIR = os.path.join(OUTPUT_DIR, "satellite_exports")
FINAL_DIR = os.path.join(OUTPUT_DIR, "final")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

# Output files
FISHERIES_INSPECTION_REPORT = os.path.join(REPORTS_DIR, "fisheries_inspection_report.txt")
SATELLITE_SOURCE_REPORT = os.path.join(REPORTS_DIR, "satellite_source_report.md")
EXTRACTION_METHODOLOGY = os.path.join(REPORTS_DIR, "extraction_methodology.md")
VALIDATION_REPORT = os.path.join(REPORTS_DIR, "satellite_validation_report.txt")

FINAL_SATELLITE_CSV = os.path.join(FINAL_DIR, "satellite_25000_rebuilt.csv")

# ============================================================================
# STUDY AREA CONFIGURATION
# ============================================================================

# Official study area boundaries
STUDY_AREA = {
    "west": 50.0,      # Longitude minimum
    "east": 100.0,     # Longitude maximum
    "south": 0.0,      # Latitude minimum
    "north": 30.0      # Latitude maximum
}

# ============================================================================
# TEMPORAL CONFIGURATION
# ============================================================================

# Study period
START_YEAR = 2015
END_YEAR = 2024
START_DATE = "2015-01-01"
END_DATE = "2024-12-31"

# Expected temporal coverage
TOTAL_YEARS = 10
TOTAL_MONTHS = 120
EXPECTED_RECORDS_PER_YEAR = 2500

# ============================================================================
# DATASET EXPECTATIONS
# ============================================================================

# Expected fisheries dataset characteristics
EXPECTED_FISHERIES_RECORDS = 25000
EXPECTED_FISHERIES_COLUMNS = 18

# Expected satellite dataset output
EXPECTED_SATELLITE_RECORDS = 25000

# ============================================================================
# SATELLITE DATA SOURCES (Google Earth Engine)
# ============================================================================

# Sea Surface Temperature
# IMPORTANT: NOAA OISST v2.1 stores SST with scale factor 0.01
# Raw values like 2835 must be multiplied by 0.01 to get 28.35°C
SST_DATASET = {
    "id": "NOAA/CDR/OISST/V2_1",
    "name": "NOAA OISST v2.1",
    "band": "sst",
    "description": "NOAA Optimum Interpolation Sea Surface Temperature",
    "temporal_resolution": "daily",
    "spatial_resolution": "0.25 degrees",
    "units": "degrees Celsius",
    "scale_factor": 0.01,  # CRITICAL: Must multiply raw values by 0.01
    "available_from": "1981-09-01"
}

# Chlorophyll-a concentration
# Note: COPERNICUS/MARINE uses band name 'chlor_a' (not 'CHL')
CHLOROPHYLL_DATASET = {
    "id": "COPERNICUS/MARINE/SATELLITE_OCEAN_COLOR/V6",
    "name": "Copernicus Marine Ocean Color",
    "band": "chlor_a",  # CORRECTED: actual band name is 'chlor_a'
    "description": "Global Ocean Colour (Copernicus-GlobColour)",
    "temporal_resolution": "daily",
    "spatial_resolution": "4 km",
    "units": "mg/m³",
    "scale_factor": 1.0,
    "available_from": "1997-09-04"
}

# Alternative chlorophyll source (if primary unavailable)
CHLOROPHYLL_ALTERNATIVE = {
    "id": "NASA/OCEANDATA/MODIS-Aqua/L3SMI",
    "name": "MODIS Aqua Ocean Color",
    "band": "chlor_a",
    "description": "MODIS Aqua Level-3 Standard Mapped Image",
    "temporal_resolution": "daily",
    "spatial_resolution": "4 km",
    "units": "mg/m³",
    "scale_factor": 1.0,
    "available_from": "2002-07-04"
}

# ============================================================================
# OUTPUT SCHEMA
# ============================================================================

# Required output columns in final satellite CSV
OUTPUT_COLUMNS = [
    "satellite_record_id",
    "date",
    "year",
    "month",
    "latitude",
    "longitude",
    "sea_surface_temperature_c",
    "chlorophyll_a_mg_m3",
    "sst_source",
    "chlorophyll_source",
    "sst_dataset_id",
    "chlorophyll_dataset_id",
    "fisheries_record_id"  # NEW: for one-to-one matching
]

# ============================================================================
# VALIDATION THRESHOLDS
# ============================================================================

# Plausible value ranges for quality checks
SST_MIN = -2.0      # Minimum plausible SST (°C)
SST_MAX = 35.0      # Maximum plausible SST (°C)
CHLOROPHYLL_MIN = 0.0    # Minimum plausible chlorophyll (mg/m³)
CHLOROPHYLL_MAX = 100.0  # Maximum plausible chlorophyll (mg/m³)

# ============================================================================
# GOOGLE EARTH ENGINE CONFIGURATION
# ============================================================================

# Google Cloud Project ID (required for Earth Engine API)
# To find your project ID:
# 1. Go to: https://console.cloud.google.com/
# 2. Select or create a project
# 3. Enable Earth Engine API for the project
# 4. Copy the Project ID (not the project name)
GEE_PROJECT_ID = "terrascope-484715" # UPDATE THIS: e.g., "my-project-12345"

# Export configuration
EXPORT_BATCH_SIZE = 2500  # Records per export task (annual batches)
EXPORT_TEST_BATCH_SIZE = 250  # Smaller batch for testing
EXPORT_FILE_FORMAT = "CSV"
EXPORT_DRIVE_FOLDER = "GEE_Satellite_Exports"

# Processing configuration
MAX_CONCURRENT_TASKS = 5  # Maximum concurrent export tasks
TASK_CHECK_INTERVAL = 30  # Seconds between task status checks
MAX_FEATURES_PER_BATCH = 500  # Features per Earth Engine computation batch

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
