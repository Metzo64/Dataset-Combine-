"""
PHASE 1: Fisheries Dataset Inspection

This script performs comprehensive inspection of the fisheries reference dataset
to verify its quality, completeness, and alignment with study requirements.

Requirements:
- 25,000 valid records
- Coverage: 2015-2024 (120 months)
- Geography: 0°-30°N, 50°-100°E
- Unique fisheries_record_id for each observation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime
from config.config import (
    FISHERIES_CSV,
    FISHERIES_INSPECTION_REPORT,
    STUDY_AREA,
    START_DATE,
    END_DATE,
    EXPECTED_FISHERIES_RECORDS,
    TOTAL_MONTHS
)


def inspect_fisheries_dataset():
    """
    Perform comprehensive inspection of the fisheries dataset.
    
    Returns:
        dict: Inspection results
    """
    print("=" * 80)
    print("PHASE 1: FISHERIES DATASET INSPECTION")
    print("=" * 80)
    print()
    
    # Check if file exists
    if not os.path.exists(FISHERIES_CSV):
        print(f"ERROR: Fisheries CSV not found at {FISHERIES_CSV}")
        return None
    
    print(f"Loading fisheries dataset from: {FISHERIES_CSV}")
    print()
    
    # Load dataset
    try:
        df = pd.read_csv(FISHERIES_CSV)
        print(f"[OK] Successfully loaded fisheries dataset")
        print()
    except Exception as e:
        print(f"ERROR loading CSV: {e}")
        return None
    
    # Initialize inspection results
    results = {
        "file_path": FISHERIES_CSV,
        "inspection_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset": df
    }
    
    # ========================================================================
    # BASIC DATASET STRUCTURE
    # ========================================================================
    print("-" * 80)
    print("1. BASIC DATASET STRUCTURE")
    print("-" * 80)
    
    results["total_rows"] = len(df)
    results["total_columns"] = len(df.columns)
    results["column_names"] = list(df.columns)
    
    print(f"Total rows: {results['total_rows']:,}")
    print(f"Total columns: {results['total_columns']}")
    print(f"Expected rows: {EXPECTED_FISHERIES_RECORDS:,}")
    print()
    
    print("Column names:")
    for i, col in enumerate(results["column_names"], 1):
        print(f"  {i:2d}. {col}")
    print()
    
    # Check for expected record count
    if results["total_rows"] == EXPECTED_FISHERIES_RECORDS:
        print(f"[OK] Record count matches expectation ({EXPECTED_FISHERIES_RECORDS:,} records)")
    else:
        print(f"[WARNING] Record count mismatch: {results['total_rows']:,} vs expected {EXPECTED_FISHERIES_RECORDS:,}")
    print()
    
    # ========================================================================
    # DATA TYPES AND MISSING VALUES
    # ========================================================================
    print("-" * 80)
    print("2. DATA TYPES AND MISSING VALUES")
    print("-" * 80)
    
    results["data_types"] = df.dtypes.to_dict()
    results["missing_values"] = df.isnull().sum().to_dict()
    results["missing_percentage"] = (df.isnull().sum() / len(df) * 100).to_dict()
    
    print("Data types and missing values:")
    print()
    print(f"{'Column':<30} {'Type':<15} {'Missing':<10} {'%':<10}")
    print("-" * 65)
    for col in df.columns:
        dtype = str(df[col].dtype)
        missing = results["missing_values"][col]
        pct = results["missing_percentage"][col]
        print(f"{col:<30} {dtype:<15} {missing:<10} {pct:<10.2f}")
    print()
    
    # ========================================================================
    # UNIQUE IDENTIFIERS
    # ========================================================================
    print("-" * 80)
    print("3. UNIQUE IDENTIFIERS")
    print("-" * 80)
    
    if "fisheries_record_id" in df.columns:
        results["unique_record_ids"] = df["fisheries_record_id"].nunique()
        results["duplicate_record_ids"] = len(df) - results["unique_record_ids"]
        
        print(f"Total records: {len(df):,}")
        print(f"Unique fisheries_record_id values: {results['unique_record_ids']:,}")
        print(f"Duplicate fisheries_record_id values: {results['duplicate_record_ids']:,}")
        
        if results["duplicate_record_ids"] == 0:
            print("[OK] All fisheries_record_id values are unique")
        else:
            print(f"[WARNING] Found {results['duplicate_record_ids']:,} duplicate record IDs")
            duplicates = df[df.duplicated(subset=["fisheries_record_id"], keep=False)]
            print(f"  Duplicate IDs: {duplicates['fisheries_record_id'].unique()[:10].tolist()}")
    else:
        print("[WARNING] Column 'fisheries_record_id' not found")
        results["unique_record_ids"] = None
    
    print()
    
    # ========================================================================
    # TEMPORAL ANALYSIS
    # ========================================================================
    print("-" * 80)
    print("4. TEMPORAL ANALYSIS")
    print("-" * 80)
    
    if "date" in df.columns:
        # Convert date column to datetime
        df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
        results["invalid_dates"] = df["date_parsed"].isnull().sum()
        
        print(f"Invalid dates: {results['invalid_dates']:,}")
        
        if results["invalid_dates"] > 0:
            print("[WARNING] Warning: Some dates could not be parsed")
            invalid_samples = df[df["date_parsed"].isnull()]["date"].head(10).tolist()
            print(f"  Sample invalid dates: {invalid_samples}")
        else:
            print("[OK] All dates are valid")
        print()
        
        # Analyze valid dates
        valid_df = df[df["date_parsed"].notnull()].copy()
        
        if len(valid_df) > 0:
            results["date_min"] = valid_df["date_parsed"].min()
            results["date_max"] = valid_df["date_parsed"].max()
            results["date_range_days"] = (results["date_max"] - results["date_min"]).days
            
            print(f"Date range:")
            print(f"  Earliest: {results['date_min'].strftime('%Y-%m-%d')}")
            print(f"  Latest:   {results['date_max'].strftime('%Y-%m-%d')}")
            print(f"  Span:     {results['date_range_days']:,} days")
            print()
            
            # Extract year and month
            valid_df["year"] = valid_df["date_parsed"].dt.year
            valid_df["month"] = valid_df["date_parsed"].dt.month
            
            # Year distribution
            results["years"] = sorted(valid_df["year"].unique())
            results["year_counts"] = valid_df["year"].value_counts().sort_index().to_dict()
            
            print(f"Year distribution ({len(results['years'])} years):")
            for year in results["years"]:
                count = results["year_counts"][year]
                pct = count / len(valid_df) * 100
                bar = "#" * int(pct / 2)
                print(f"  {year}: {count:>5,} records ({pct:>5.1f}%) {bar}")
            print()
            
            # Month distribution
            results["months"] = sorted(valid_df["month"].unique())
            results["month_counts"] = valid_df["month"].value_counts().sort_index().to_dict()
            
            print(f"Month distribution ({len(results['months'])} months):")
            for month in range(1, 13):
                if month in results["month_counts"]:
                    count = results["month_counts"][month]
                    pct = count / len(valid_df) * 100
                    bar = "#" * int(pct)
                    print(f"  Month {month:>2}: {count:>5,} records ({pct:>5.1f}%) {bar}")
                else:
                    print(f"  Month {month:>2}: Missing")
            print()
            
            # Year-Month combinations
            valid_df["year_month"] = valid_df["date_parsed"].dt.to_period("M")
            results["unique_year_months"] = valid_df["year_month"].nunique()
            
            print(f"Unique year-month combinations: {results['unique_year_months']}")
            print(f"Expected: {TOTAL_MONTHS} months (2015-2024)")
            
            if results["unique_year_months"] == TOTAL_MONTHS:
                print("[OK] All 120 months are represented")
            else:
                print(f"[WARNING] Missing {TOTAL_MONTHS - results['unique_year_months']} months")
            print()
            
            # Check study period compliance
            study_start = pd.to_datetime(START_DATE)
            study_end = pd.to_datetime(END_DATE)
            
            before_study = valid_df[valid_df["date_parsed"] < study_start]
            after_study = valid_df[valid_df["date_parsed"] > study_end]
            
            results["records_before_study"] = len(before_study)
            results["records_after_study"] = len(after_study)
            results["records_within_study"] = len(valid_df) - len(before_study) - len(after_study)
            
            print(f"Study period compliance (2015-2024):")
            print(f"  Before 2015: {results['records_before_study']:,} records")
            print(f"  Within 2015-2024: {results['records_within_study']:,} records")
            print(f"  After 2024: {results['records_after_study']:,} records")
            
            if results["records_before_study"] == 0 and results["records_after_study"] == 0:
                print("[OK] All records fall within study period")
            else:
                print("[WARNING] Some records fall outside study period")
            print()
    else:
        print("[ WARNING] Column 'date' not found")
    
    # ========================================================================
    # GEOGRAPHICAL ANALYSIS
    # ========================================================================
    print("-" * 80)
    print("5. GEOGRAPHICAL ANALYSIS")
    print("-" * 80)
    
    if "lat" in df.columns and "lon" in df.columns:
        # Check for missing coordinates
        results["missing_lat"] = df["lat"].isnull().sum()
        results["missing_lon"] = df["lon"].isnull().sum()
        
        print(f"Missing latitude values: {results['missing_lat']:,}")
        print(f"Missing longitude values: {results['missing_lon']:,}")
        print()
        
        # Analyze valid coordinates
        valid_coords = df[df["lat"].notnull() & df["lon"].notnull()].copy()
        
        if len(valid_coords) > 0:
            results["lat_min"] = valid_coords["lat"].min()
            results["lat_max"] = valid_coords["lat"].max()
            results["lon_min"] = valid_coords["lon"].min()
            results["lon_max"] = valid_coords["lon"].max()
            
            print(f"Coordinate ranges:")
            print(f"  Latitude:  {results['lat_min']:.6f} to {results['lat_max']:.6f}")
            print(f"  Longitude: {results['lon_min']:.6f} to {results['lon_max']:.6f}")
            print()
            
            print(f"Study area boundaries:")
            print(f"  Latitude:  {STUDY_AREA['south']}° to {STUDY_AREA['north']}°N")
            print(f"  Longitude: {STUDY_AREA['west']}° to {STUDY_AREA['east']}°E")
            print()
            
            # Check study area compliance
            outside_lat = valid_coords[
                (valid_coords["lat"] < STUDY_AREA["south"]) |
                (valid_coords["lat"] > STUDY_AREA["north"])
            ]
            outside_lon = valid_coords[
                (valid_coords["lon"] < STUDY_AREA["west"]) |
                (valid_coords["lon"] > STUDY_AREA["east"])
            ]
            outside_both = valid_coords[
                ((valid_coords["lat"] < STUDY_AREA["south"]) |
                 (valid_coords["lat"] > STUDY_AREA["north"])) |
                ((valid_coords["lon"] < STUDY_AREA["west"]) |
                 (valid_coords["lon"] > STUDY_AREA["east"]))
            ]
            
            results["records_outside_lat"] = len(outside_lat)
            results["records_outside_lon"] = len(outside_lon)
            results["records_outside_study_area"] = len(outside_both)
            results["records_inside_study_area"] = len(valid_coords) - len(outside_both)
            
            print(f"Study area compliance:")
            print(f"  Inside study area: {results['records_inside_study_area']:,} records")
            print(f"  Outside latitude bounds: {results['records_outside_lat']:,} records")
            print(f"  Outside longitude bounds: {results['records_outside_lon']:,} records")
            print(f"  Outside study area: {results['records_outside_study_area']:,} records")
            
            if results["records_outside_study_area"] == 0:
                print("[OK] All coordinates fall within study area")
            else:
                print(f"[WARNING] {results['records_outside_study_area']:,} records outside study area")
                print("\nSample coordinates outside study area:")
                print(outside_both[["fisheries_record_id", "date", "lat", "lon"]].head(10))
            print()
    else:
        print("[WARNING] Columns 'lat' and/or 'lon' not found")
    
    # ========================================================================
    # DUPLICATE DETECTION
    # ========================================================================
    print("-" * 80)
    print("6. DUPLICATE DETECTION")
    print("-" * 80)
    
    # Exact duplicate rows
    results["duplicate_rows"] = df.duplicated().sum()
    print(f"Exact duplicate rows: {results['duplicate_rows']:,}")
    
    if results["duplicate_rows"] > 0:
        print("[WARNING] Found exact duplicate rows")
    else:
        print("[OK] No exact duplicate rows")
    print()
    
    # Duplicate date-coordinate combinations
    if "date" in df.columns and "lat" in df.columns and "lon" in df.columns:
        results["duplicate_date_coords"] = df.duplicated(subset=["date", "lat", "lon"]).sum()
        print(f"Duplicate date-coordinate combinations: {results['duplicate_date_coords']:,}")
        
        if results["duplicate_date_coords"] > 0:
            print("[WARNING] Multiple fisheries observations share same date and coordinates")
            print("  This is why fisheries_record_id is essential for matching")
        else:
            print("[OK] All date-coordinate combinations are unique")
    print()
    
    # ========================================================================
    # VESSEL INFORMATION
    # ========================================================================
    print("-" * 80)
    print("7. VESSEL INFORMATION")
    print("-" * 80)
    
    if "vesselId" in df.columns:
        results["unique_vessels"] = df["vesselId"].nunique()
        print(f"Unique vessels: {results['unique_vessels']:,}")
    
    if "vesselType" in df.columns:
        results["vessel_types"] = df["vesselType"].value_counts().to_dict()
        print(f"\nVessel types:")
        for vtype, count in results["vessel_types"].items():
            print(f"  {vtype}: {count:,} records")
    
    if "geartype" in df.columns:
        results["gear_types"] = df["geartype"].value_counts().to_dict()
        print(f"\nGear types:")
        for gtype, count in results["gear_types"].items():
            print(f"  {gtype}: {count:,} records")
    print()
    
    # ========================================================================
    # SUMMARY AND RECOMMENDATIONS
    # ========================================================================
    print("=" * 80)
    print("INSPECTION SUMMARY")
    print("=" * 80)
    print()
    
    issues = []
    warnings = []
    
    # Check critical requirements
    if results["total_rows"] != EXPECTED_FISHERIES_RECORDS:
        issues.append(f"Record count: {results['total_rows']:,} (expected {EXPECTED_FISHERIES_RECORDS:,})")
    
    if "fisheries_record_id" in results and results.get("unique_record_ids") != results["total_rows"]:
        issues.append(f"Non-unique record IDs: {results['duplicate_record_ids']:,} duplicates")
    
    if "invalid_dates" in results and results["invalid_dates"] > 0:
        issues.append(f"Invalid dates: {results['invalid_dates']:,}")
    
    if "records_outside_study_area" in results and results["records_outside_study_area"] > 0:
        warnings.append(f"Records outside study area: {results['records_outside_study_area']:,}")
    
    if "unique_year_months" in results and results["unique_year_months"] != TOTAL_MONTHS:
        warnings.append(f"Missing months: {TOTAL_MONTHS - results['unique_year_months']}")
    
    if issues:
        print("CRITICAL ISSUES:")
        for issue in issues:
            print(f"  [X] {issue}")
        print()
    
    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  [!] {warning}")
        print()
    
    if not issues and not warnings:
        print("[OK] ALL CHECKS PASSED")
        print()
        print("The fisheries dataset is ready for satellite extraction.")
    else:
        print("RECOMMENDATION:")
        if issues:
            print("  Critical issues must be resolved before proceeding.")
        if warnings:
            print("  Warnings should be reviewed and documented.")
    
    print()
    print("=" * 80)
    
    return results


def write_inspection_report(results):
    """
    Write detailed inspection report to file.
    
    Args:
        results (dict): Inspection results
    """
    if results is None:
        print("ERROR: No results to write")
        return
    
    print(f"\nWriting inspection report to: {FISHERIES_INSPECTION_REPORT}")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(FISHERIES_INSPECTION_REPORT), exist_ok=True)
    
    with open(FISHERIES_INSPECTION_REPORT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("FISHERIES DATASET INSPECTION REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"File: {results['file_path']}\n")
        f.write(f"Inspection Date: {results['inspection_date']}\n")
        f.write(f"Total Records: {results['total_rows']:,}\n")
        f.write(f"Total Columns: {results['total_columns']}\n\n")
        
        f.write("-" * 80 + "\n")
        f.write("1. COLUMNS\n")
        f.write("-" * 80 + "\n\n")
        for i, col in enumerate(results["column_names"], 1):
            f.write(f"{i:2d}. {col}\n")
        f.write("\n")
        
        f.write("-" * 80 + "\n")
        f.write("2. MISSING VALUES\n")
        f.write("-" * 80 + "\n\n")
        f.write(f"{'Column':<30} {'Missing':<10} {'%':<10}\n")
        f.write("-" * 50 + "\n")
        for col, count in results["missing_values"].items():
            pct = results["missing_percentage"][col]
            f.write(f"{col:<30} {count:<10} {pct:<10.2f}\n")
        f.write("\n")
        
        f.write("-" * 80 + "\n")
        f.write("3. TEMPORAL ANALYSIS\n")
        f.write("-" * 80 + "\n\n")
        if "date_min" in results:
            f.write(f"Date Range: {results['date_min'].strftime('%Y-%m-%d')} to {results['date_max'].strftime('%Y-%m-%d')}\n")
            f.write(f"Duration: {results['date_range_days']:,} days\n")
            f.write(f"Invalid Dates: {results.get('invalid_dates', 0):,}\n\n")
            
            f.write(f"Year Distribution:\n")
            for year, count in sorted(results["year_counts"].items()):
                pct = count / results['total_rows'] * 100
                f.write(f"  {year}: {count:>5,} records ({pct:>5.1f}%)\n")
            f.write(f"\nUnique Year-Months: {results['unique_year_months']} / {TOTAL_MONTHS} expected\n\n")
        
        f.write("-" * 80 + "\n")
        f.write("4. GEOGRAPHICAL ANALYSIS\n")
        f.write("-" * 80 + "\n\n")
        if "lat_min" in results:
            f.write(f"Latitude Range:  {results['lat_min']:.6f} to {results['lat_max']:.6f}\n")
            f.write(f"Longitude Range: {results['lon_min']:.6f} to {results['lon_max']:.6f}\n\n")
            f.write(f"Study Area Compliance:\n")
            f.write(f"  Inside:  {results.get('records_inside_study_area', 0):,} records\n")
            f.write(f"  Outside: {results.get('records_outside_study_area', 0):,} records\n\n")
        
        f.write("-" * 80 + "\n")
        f.write("5. QUALITY CHECKS\n")
        f.write("-" * 80 + "\n\n")
        f.write(f"Unique Record IDs: {results.get('unique_record_ids', 'N/A'):,}\n")
        f.write(f"Duplicate Record IDs: {results.get('duplicate_record_ids', 'N/A'):,}\n")
        f.write(f"Exact Duplicate Rows: {results.get('duplicate_rows', 0):,}\n")
        f.write(f"Duplicate Date-Coords: {results.get('duplicate_date_coords', 0):,}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")
    
    print(f"[OK] Report saved successfully")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("SATELLITE DATASET GENERATION PROJECT")
    print("PHASE 1: FISHERIES DATASET INSPECTION")
    print("=" * 80 + "\n")
    
    # Run inspection
    results = inspect_fisheries_dataset()
    
    # Write report
    if results:
        write_inspection_report(results)
        print("\n[OK] Phase 1 complete")
    else:
        print("\n[X] Phase 1 failed")
        sys.exit(1)
