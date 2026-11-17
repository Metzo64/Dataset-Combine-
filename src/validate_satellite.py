"""
PHASE 7: Satellite Dataset Validation

This script performs comprehensive validation of the final satellite dataset
to ensure it meets all project requirements.

Validation Checks:
1. Record count (25,000 expected)
2. Unique identifiers
3. Temporal coverage (2015-2024, 120 months)
4. Geographical boundaries (0°-30°N, 50°-100°E)
5. Environmental value ranges
6. One-to-one matching with fisheries
7. Coordinate and date preservation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime
from config.config import (
    FISHERIES_CSV,
    FINAL_SATELLITE_CSV,
    VALIDATION_REPORT,
    STUDY_AREA,
    START_DATE,
    END_DATE,
    EXPECTED_SATELLITE_RECORDS,
    TOTAL_MONTHS,
    SST_MIN,
    SST_MAX,
    CHLOROPHYLL_MIN,
    CHLOROPHYLL_MAX
)


def load_datasets():
    """
    Load fisheries and satellite datasets.
    
    Returns:
        tuple: (fisheries_df, satellite_df) or (None, None) on error
    """
    print("=" * 80)
    print("PHASE 7: SATELLITE DATASET VALIDATION")
    print("=" * 80)
    print()
    
    print("Loading datasets...")
    print()
    
    # Load fisheries dataset
    if not os.path.exists(FISHERIES_CSV):
        print(f"ERROR: Fisheries dataset not found: {FISHERIES_CSV}")
        return None, None
    
    try:
        fisheries_df = pd.read_csv(FISHERIES_CSV)
        print(f"[OK] Fisheries dataset loaded: {len(fisheries_df):,} records")
    except Exception as e:
        print(f"ERROR loading fisheries dataset: {e}")
        return None, None
    
    # Load satellite dataset
    if not os.path.exists(FINAL_SATELLITE_CSV):
        print(f"ERROR: Satellite dataset not found: {FINAL_SATELLITE_CSV}")
        print("Please run merge_satellite_exports.py first")
        return None, None
    
    try:
        satellite_df = pd.read_csv(FINAL_SATELLITE_CSV)
        print(f"[OK] Satellite dataset loaded: {len(satellite_df):,} records")
    except Exception as e:
        print(f"ERROR loading satellite dataset: {e}")
        return None, None
    
    print()
    return fisheries_df, satellite_df


def validate_record_count(satellite_df):
    """
    Validate total record count.
    
    Args:
        satellite_df (pd.DataFrame): Satellite dataset
        
    Returns:
        dict: Validation results
    """
    print("-" * 80)
    print("1. RECORD COUNT VALIDATION")
    print("-" * 80)
    print()
    
    results = {
        "check": "Record Count",
        "passed": False,
        "details": {}
    }
    
    actual_count = len(satellite_df)
    expected_count = EXPECTED_SATELLITE_RECORDS
    
    results["details"]["actual"] = actual_count
    results["details"]["expected"] = expected_count
    results["details"]["difference"] = actual_count - expected_count
    
    print(f"Expected records: {expected_count:,}")
    print(f"Actual records:   {actual_count:,}")
    print(f"Difference:       {results['details']['difference']:+,}")
    print()
    
    if actual_count == expected_count:
        print("[OK] Record count matches expectation")
        results["passed"] = True
    else:
        print("[FAIL] Record count mismatch")
        results["passed"] = False
    
    print()
    return results


def validate_unique_identifiers(satellite_df):
    """
    Validate unique record identifiers.
    
    Args:
        satellite_df (pd.DataFrame): Satellite dataset
        
    Returns:
        dict: Validation results
    """
    print("-" * 80)
    print("2. UNIQUE IDENTIFIER VALIDATION")
    print("-" * 80)
    print()
    
    results = {
        "check": "Unique Identifiers",
        "passed": True,
        "details": {}
    }
    
    # Check satellite_record_id
    if "satellite_record_id" in satellite_df.columns:
        unique_sat_ids = satellite_df["satellite_record_id"].nunique()
        duplicate_sat_ids = len(satellite_df) - unique_sat_ids
        
        results["details"]["unique_satellite_ids"] = unique_sat_ids
        results["details"]["duplicate_satellite_ids"] = duplicate_sat_ids
        
        print(f"Satellite Record IDs:")
        print(f"  Total records: {len(satellite_df):,}")
        print(f"  Unique IDs:    {unique_sat_ids:,}")
        print(f"  Duplicates:    {duplicate_sat_ids:,}")
        
        if duplicate_sat_ids == 0:
            print("  [OK] All satellite_record_id values are unique")
        else:
            print("  [FAIL] Duplicate satellite_record_id values found")
            results["passed"] = False
    else:
        print("[FAIL] Column 'satellite_record_id' not found")
        results["passed"] = False
    
    print()
    
    # Check fisheries_record_id
    if "fisheries_record_id" in satellite_df.columns:
        unique_fish_ids = satellite_df["fisheries_record_id"].nunique()
        duplicate_fish_ids = len(satellite_df) - unique_fish_ids
        
        results["details"]["unique_fisheries_ids"] = unique_fish_ids
        results["details"]["duplicate_fisheries_ids"] = duplicate_fish_ids
        
        print(f"Fisheries Record IDs:")
        print(f"  Total records: {len(satellite_df):,}")
        print(f"  Unique IDs:    {unique_fish_ids:,}")
        print(f"  Duplicates:    {duplicate_fish_ids:,}")
        
        if duplicate_fish_ids == 0:
            print("  [OK] All fisheries_record_id values are unique")
        else:
            print("  [FAIL] Multiple satellite records per fisheries observation")
            results["passed"] = False
    else:
        print("[FAIL] Column 'fisheries_record_id' not found")
        results["passed"] = False
    
    print()
    return results


def validate_temporal_coverage(satellite_df):
    """
    Validate temporal coverage and distribution.
    
    Args:
        satellite_df (pd.DataFrame): Satellite dataset
        
    Returns:
        dict: Validation results
    """
    print("-" * 80)
    print("3. TEMPORAL COVERAGE VALIDATION")
    print("-" * 80)
    print()
    
    results = {
        "check": "Temporal Coverage",
        "passed": True,
        "details": {}
    }
    
    if "date" not in satellite_df.columns:
        print("[FAIL] Column 'date' not found")
        results["passed"] = False
        return results
    
    # Parse dates
    satellite_df["date_parsed"] = pd.to_datetime(satellite_df["date"], errors="coerce")
    invalid_dates = satellite_df["date_parsed"].isnull().sum()
    
    results["details"]["invalid_dates"] = invalid_dates
    
    if invalid_dates > 0:
        print(f"[WARNING] {invalid_dates:,} invalid dates found")
        results["passed"] = False
    
    valid_df = satellite_df[satellite_df["date_parsed"].notnull()].copy()
    
    if len(valid_df) == 0:
        print("[FAIL] No valid dates found")
        results["passed"] = False
        return results
    
    # Date range
    date_min = valid_df["date_parsed"].min()
    date_max = valid_df["date_parsed"].max()
    
    results["details"]["date_min"] = date_min
    results["details"]["date_max"] = date_max
    
    print(f"Date Range:")
    print(f"  Earliest: {date_min.strftime('%Y-%m-%d')}")
    print(f"  Latest:   {date_max.strftime('%Y-%m-%d')}")
    print(f"  Expected: {START_DATE} to {END_DATE}")
    print()
    
    study_start = pd.to_datetime(START_DATE)
    study_end = pd.to_datetime(END_DATE)
    
    if date_min >= study_start and date_max <= study_end:
        print("  [OK] All dates within study period")
    else:
        print("  [WARNING] Some dates outside study period")
        results["passed"] = False
    
    print()
    
    # Year distribution
    valid_df["year"] = valid_df["date_parsed"].dt.year
    year_counts = valid_df["year"].value_counts().sort_index()
    
    results["details"]["year_counts"] = year_counts.to_dict()
    
    print(f"Year Distribution:")
    for year in range(2015, 2025):
        count = year_counts.get(year, 0)
        pct = count / len(valid_df) * 100 if len(valid_df) > 0 else 0
        print(f"  {year}: {count:>5,} records ({pct:>5.1f}%)")
    
    print()
    
    # Month distribution
    valid_df["year_month"] = valid_df["date_parsed"].dt.to_period("M")
    unique_months = valid_df["year_month"].nunique()
    
    results["details"]["unique_months"] = unique_months
    
    print(f"Unique Year-Month Combinations: {unique_months}")
    print(f"Expected: {TOTAL_MONTHS} (2015-2024)")
    
    if unique_months == TOTAL_MONTHS:
        print("[OK] All 120 months represented")
    else:
        print(f"[FAIL] Missing {TOTAL_MONTHS - unique_months} months")
        results["passed"] = False
    
    print()
    return results


def validate_geographical_coverage(satellite_df):
    """
    Validate geographical boundaries.
    
    Args:
        satellite_df (pd.DataFrame): Satellite dataset
        
    Returns:
        dict: Validation results
    """
    print("-" * 80)
    print("4. GEOGRAPHICAL COVERAGE VALIDATION")
    print("-" * 80)
    print()
    
    results = {
        "check": "Geographical Coverage",
        "passed": True,
        "details": {}
    }
    
    if "latitude" not in satellite_df.columns or "longitude" not in satellite_df.columns:
        print("[FAIL] Coordinate columns not found")
        results["passed"] = False
        return results
    
    # Check for missing coordinates
    missing_lat = satellite_df["latitude"].isnull().sum()
    missing_lon = satellite_df["longitude"].isnull().sum()
    
    results["details"]["missing_lat"] = missing_lat
    results["details"]["missing_lon"] = missing_lon
    
    if missing_lat > 0 or missing_lon > 0:
        print(f"[WARNING] Missing coordinates: {missing_lat:,} lat, {missing_lon:,} lon")
        results["passed"] = False
    
    # Analyze valid coordinates
    valid_coords = satellite_df[
        satellite_df["latitude"].notnull() & satellite_df["longitude"].notnull()
    ].copy()
    
    if len(valid_coords) == 0:
        print("[FAIL] No valid coordinates found")
        results["passed"] = False
        return results
    
    lat_min = valid_coords["latitude"].min()
    lat_max = valid_coords["latitude"].max()
    lon_min = valid_coords["longitude"].min()
    lon_max = valid_coords["longitude"].max()
    
    results["details"]["lat_min"] = lat_min
    results["details"]["lat_max"] = lat_max
    results["details"]["lon_min"] = lon_min
    results["details"]["lon_max"] = lon_max
    
    print(f"Coordinate Ranges:")
    print(f"  Latitude:  {lat_min:.6f} to {lat_max:.6f}")
    print(f"  Longitude: {lon_min:.6f} to {lon_max:.6f}")
    print()
    
    print(f"Study Area Boundaries:")
    print(f"  Latitude:  {STUDY_AREA['south']}° to {STUDY_AREA['north']}°N")
    print(f"  Longitude: {STUDY_AREA['west']}° to {STUDY_AREA['east']}°E")
    print()
    
    # Check compliance
    outside_lat = valid_coords[
        (valid_coords["latitude"] < STUDY_AREA["south"]) |
        (valid_coords["latitude"] > STUDY_AREA["north"])
    ]
    outside_lon = valid_coords[
        (valid_coords["longitude"] < STUDY_AREA["west"]) |
        (valid_coords["longitude"] > STUDY_AREA["east"])
    ]
    outside_both = valid_coords[
        ((valid_coords["latitude"] < STUDY_AREA["south"]) |
         (valid_coords["latitude"] > STUDY_AREA["north"])) |
        ((valid_coords["longitude"] < STUDY_AREA["west"]) |
         (valid_coords["longitude"] > STUDY_AREA["east"]))
    ]
    
    results["details"]["outside_lat"] = len(outside_lat)
    results["details"]["outside_lon"] = len(outside_lon)
    results["details"]["outside_study_area"] = len(outside_both)
    results["details"]["inside_study_area"] = len(valid_coords) - len(outside_both)
    
    print(f"Study Area Compliance:")
    print(f"  Inside:  {results['details']['inside_study_area']:,} records")
    print(f"  Outside: {results['details']['outside_study_area']:,} records")
    
    if results["details"]["outside_study_area"] == 0:
        print("  [OK] All coordinates within study area")
    else:
        print("  [FAIL] Some coordinates outside study area")
        results["passed"] = False
    
    print()
    return results


def validate_environmental_values(satellite_df):
    """
    Validate environmental measurement ranges.
    
    Args:
        satellite_df (pd.DataFrame): Satellite dataset
        
    Returns:
        dict: Validation results
    """
    print("-" * 80)
    print("5. ENVIRONMENTAL VALUE VALIDATION")
    print("-" * 80)
    print()
    
    results = {
        "check": "Environmental Values",
        "passed": True,
        "details": {}
    }
    
    # SST validation
    if "sea_surface_temperature_c" in satellite_df.columns:
        sst = satellite_df["sea_surface_temperature_c"]
        sst_valid = sst[sst.notnull()]
        
        results["details"]["sst_count"] = len(sst)
        results["details"]["sst_missing"] = sst.isnull().sum()
        results["details"]["sst_missing_pct"] = results["details"]["sst_missing"] / len(sst) * 100
        
        if len(sst_valid) > 0:
            results["details"]["sst_min"] = sst_valid.min()
            results["details"]["sst_max"] = sst_valid.max()
            results["details"]["sst_mean"] = sst_valid.mean()
            results["details"]["sst_median"] = sst_valid.median()
            
            print(f"Sea Surface Temperature:")
            print(f"  Total values:   {len(sst):,}")
            print(f"  Missing:        {results['details']['sst_missing']:,} ({results['details']['sst_missing_pct']:.1f}%)")
            print(f"  Valid:          {len(sst_valid):,}")
            print(f"  Range:          {results['details']['sst_min']:.2f}°C to {results['details']['sst_max']:.2f}°C")
            print(f"  Mean:           {results['details']['sst_mean']:.2f}°C")
            print(f"  Median:         {results['details']['sst_median']:.2f}°C")
            print(f"  Expected range: {SST_MIN}°C to {SST_MAX}°C")
            
            # Check for values outside plausible range
            outside_range = sst_valid[(sst_valid < SST_MIN) | (sst_valid > SST_MAX)]
            results["details"]["sst_outside_range"] = len(outside_range)
            
            if len(outside_range) > 0:
                print(f"  [WARNING] {len(outside_range):,} values outside plausible range")
                print(f"            Min: {outside_range.min():.2f}°C, Max: {outside_range.max():.2f}°C")
            else:
                print(f"  [OK] All values within plausible range")
        else:
            print(f"Sea Surface Temperature:")
            print(f"  [WARNING] No valid SST values found")
            results["passed"] = False
        
        print()
    
    # Chlorophyll validation
    if "chlorophyll_a_mg_m3" in satellite_df.columns:
        chl = satellite_df["chlorophyll_a_mg_m3"]
        chl_valid = chl[chl.notnull()]
        
        results["details"]["chl_count"] = len(chl)
        results["details"]["chl_missing"] = chl.isnull().sum()
        results["details"]["chl_missing_pct"] = results["details"]["chl_missing"] / len(chl) * 100
        
        if len(chl_valid) > 0:
            results["details"]["chl_min"] = chl_valid.min()
            results["details"]["chl_max"] = chl_valid.max()
            results["details"]["chl_mean"] = chl_valid.mean()
            results["details"]["chl_median"] = chl_valid.median()
            
            print(f"Chlorophyll-a:")
            print(f"  Total values:   {len(chl):,}")
            print(f"  Missing:        {results['details']['chl_missing']:,} ({results['details']['chl_missing_pct']:.1f}%)")
            print(f"  Valid:          {len(chl_valid):,}")
            print(f"  Range:          {results['details']['chl_min']:.4f} to {results['details']['chl_max']:.4f} mg/m³")
            print(f"  Mean:           {results['details']['chl_mean']:.4f} mg/m³")
            print(f"  Median:         {results['details']['chl_median']:.4f} mg/m³")
            print(f"  Expected range: {CHLOROPHYLL_MIN} to {CHLOROPHYLL_MAX} mg/m³")
            
            # Check for values outside plausible range
            outside_range = chl_valid[(chl_valid < CHLOROPHYLL_MIN) | (chl_valid > CHLOROPHYLL_MAX)]
            results["details"]["chl_outside_range"] = len(outside_range)
            
            if len(outside_range) > 0:
                print(f"  [WARNING] {len(outside_range):,} values outside plausible range")
                print(f"            Min: {outside_range.min():.4f}, Max: {outside_range.max():.4f} mg/m³")
            else:
                print(f"  [OK] All values within plausible range")
            
            print()
            print(f"  Note: High missing rate for chlorophyll is expected due to clouds")
        else:
            print(f"Chlorophyll-a:")
            print(f"  [WARNING] No valid chlorophyll values found")
        
        print()
    
    return results


def validate_one_to_one_matching(fisheries_df, satellite_df):
    """
    Validate one-to-one matching between fisheries and satellite datasets.
    
    Args:
        fisheries_df (pd.DataFrame): Fisheries dataset
        satellite_df (pd.DataFrame): Satellite dataset
        
    Returns:
        dict: Validation results
    """
    print("-" * 80)
    print("6. ONE-TO-ONE MATCHING VALIDATION")
    print("-" * 80)
    print()
    
    results = {
        "check": "One-to-One Matching",
        "passed": True,
        "details": {}
    }
    
    if "fisheries_record_id" not in fisheries_df.columns:
        print("[FAIL] fisheries_record_id not found in fisheries dataset")
        results["passed"] = False
        return results
    
    if "fisheries_record_id" not in satellite_df.columns:
        print("[FAIL] fisheries_record_id not found in satellite dataset")
        results["passed"] = False
        return results
    
    fisheries_ids = set(fisheries_df["fisheries_record_id"])
    satellite_ids = set(satellite_df["fisheries_record_id"])
    
    results["details"]["fisheries_count"] = len(fisheries_ids)
    results["details"]["satellite_count"] = len(satellite_ids)
    results["details"]["ids_match"] = fisheries_ids == satellite_ids
    results["details"]["missing_in_satellite"] = list(fisheries_ids - satellite_ids)
    results["details"]["extra_in_satellite"] = list(satellite_ids - fisheries_ids)
    
    print(f"Fisheries record IDs: {len(fisheries_ids):,}")
    print(f"Satellite record IDs: {len(satellite_ids):,}")
    print()
    
    if fisheries_ids == satellite_ids:
        print("[OK] Perfect one-to-one match")
        print("    Every fisheries observation has exactly one satellite record")
    else:
        print("[FAIL] ID sets do not match")
        results["passed"] = False
        
        missing_count = len(results["details"]["missing_in_satellite"])
        extra_count = len(results["details"]["extra_in_satellite"])
        
        if missing_count > 0:
            print(f"  Missing in satellite: {missing_count:,} IDs")
            print(f"  Sample: {results['details']['missing_in_satellite'][:10]}")
        
        if extra_count > 0:
            print(f"  Extra in satellite: {extra_count:,} IDs")
            print(f"  Sample: {results['details']['extra_in_satellite'][:10]}")
    
    print()
    return results


def validate_coordinate_preservation(fisheries_df, satellite_df):
    """
    Validate that coordinates are preserved from fisheries dataset.
    
    Args:
        fisheries_df (pd.DataFrame): Fisheries dataset
        satellite_df (pd.DataFrame): Satellite dataset
        
    Returns:
        dict: Validation results
    """
    print("-" * 80)
    print("7. COORDINATE PRESERVATION VALIDATION")
    print("-" * 80)
    print()
    
    results = {
        "check": "Coordinate Preservation",
        "passed": True,
        "details": {}
    }
    
    # Merge on fisheries_record_id
    if "fisheries_record_id" not in fisheries_df.columns or "fisheries_record_id" not in satellite_df.columns:
        print("[FAIL] Cannot merge: fisheries_record_id missing")
        results["passed"] = False
        return results
    
    merged = fisheries_df[["fisheries_record_id", "lat", "lon", "date"]].merge(
        satellite_df[["fisheries_record_id", "latitude", "longitude", "date"]],
        on="fisheries_record_id",
        how="inner",
        suffixes=("_fish", "_sat")
    )
    
    results["details"]["merged_count"] = len(merged)
    
    print(f"Merged records: {len(merged):,}")
    print()
    
    if len(merged) == 0:
        print("[FAIL] No matching records found")
        results["passed"] = False
        return results
    
    # Check latitude preservation
    lat_match = (merged["lat"] == merged["latitude"]).sum()
    lat_mismatch = len(merged) - lat_match
    
    results["details"]["lat_match"] = lat_match
    results["details"]["lat_mismatch"] = lat_mismatch
    
    print(f"Latitude Preservation:")
    print(f"  Matches:    {lat_match:,}")
    print(f"  Mismatches: {lat_mismatch:,}")
    
    if lat_mismatch == 0:
        print("  [OK] All latitudes preserved")
    else:
        print("  [FAIL] Some latitudes not preserved")
        results["passed"] = False
    
    print()
    
    # Check longitude preservation
    lon_match = (merged["lon"] == merged["longitude"]).sum()
    lon_mismatch = len(merged) - lon_match
    
    results["details"]["lon_match"] = lon_match
    results["details"]["lon_mismatch"] = lon_mismatch
    
    print(f"Longitude Preservation:")
    print(f"  Matches:    {lon_match:,}")
    print(f"  Mismatches: {lon_mismatch:,}")
    
    if lon_mismatch == 0:
        print("  [OK] All longitudes preserved")
    else:
        print("  [FAIL] Some longitudes not preserved")
        results["passed"] = False
    
    print()
    
    # Check date preservation
    date_match = (merged["date_fish"] == merged["date_sat"]).sum()
    date_mismatch = len(merged) - date_match
    
    results["details"]["date_match"] = date_match
    results["details"]["date_mismatch"] = date_mismatch
    
    print(f"Date Preservation:")
    print(f"  Matches:    {date_match:,}")
    print(f"  Mismatches: {date_mismatch:,}")
    
    if date_mismatch == 0:
        print("  [OK] All dates preserved")
    else:
        print("  [FAIL] Some dates not preserved")
        results["passed"] = False
    
    print()
    return results


def write_validation_report(all_results):
    """
    Write comprehensive validation report.
    
    Args:
        all_results (list): List of validation result dictionaries
    """
    print("-" * 80)
    print("WRITING VALIDATION REPORT")
    print("-" * 80)
    print()
    
    os.makedirs(os.path.dirname(VALIDATION_REPORT), exist_ok=True)
    
    with open(VALIDATION_REPORT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("SATELLITE DATASET VALIDATION REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Dataset: {FINAL_SATELLITE_CSV}\n\n")
        
        # Summary
        f.write("-" * 80 + "\n")
        f.write("VALIDATION SUMMARY\n")
        f.write("-" * 80 + "\n\n")
        
        total_checks = len(all_results)
        passed_checks = sum(1 for r in all_results if r["passed"])
        failed_checks = total_checks - passed_checks
        
        f.write(f"Total Checks: {total_checks}\n")
        f.write(f"Passed: {passed_checks}\n")
        f.write(f"Failed: {failed_checks}\n\n")
        
        # Individual results
        for i, result in enumerate(all_results, 1):
            f.write("-" * 80 + "\n")
            f.write(f"{i}. {result['check']}\n")
            f.write("-" * 80 + "\n\n")
            f.write(f"Status: {'PASSED' if result['passed'] else 'FAILED'}\n\n")
            
            if result.get("details"):
                f.write("Details:\n")
                for key, value in result["details"].items():
                    if isinstance(value, (list, set)) and len(value) > 10:
                        f.write(f"  {key}: {len(value)} items\n")
                    elif isinstance(value, dict) and len(value) > 10:
                        f.write(f"  {key}: {len(value)} entries\n")
                    else:
                        f.write(f"  {key}: {value}\n")
                f.write("\n")
        
        # Final verdict
        f.write("=" * 80 + "\n")
        f.write("FINAL VERDICT\n")
        f.write("=" * 80 + "\n\n")
        
        if failed_checks == 0:
            f.write("ALL VALIDATION CHECKS PASSED\n\n")
            f.write("The satellite dataset meets all project requirements:\n")
            f.write("- Correct record count (25,000)\n")
            f.write("- Unique identifiers\n")
            f.write("- Complete temporal coverage (2015-2024, 120 months)\n")
            f.write("- Correct geographical boundaries\n")
            f.write("- Plausible environmental values\n")
            f.write("- One-to-one matching with fisheries\n")
            f.write("- Preserved coordinates and dates\n\n")
            f.write("The dataset is READY FOR ANALYSIS.\n")
        else:
            f.write(f"VALIDATION FAILED: {failed_checks} checks failed\n\n")
            f.write("Please review failed checks above and address issues.\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")
    
    print(f"[OK] Validation report saved: {VALIDATION_REPORT}")
    print()


def main():
    """
    Main execution function.
    """
    # Load datasets
    fisheries_df, satellite_df = load_datasets()
    
    if fisheries_df is None or satellite_df is None:
        print("[ERROR] Failed to load datasets. Exiting.")
        sys.exit(1)
    
    # Run validation checks
    all_results = []
    
    all_results.append(validate_record_count(satellite_df))
    all_results.append(validate_unique_identifiers(satellite_df))
    all_results.append(validate_temporal_coverage(satellite_df))
    all_results.append(validate_geographical_coverage(satellite_df))
    all_results.append(validate_environmental_values(satellite_df))
    all_results.append(validate_one_to_one_matching(fisheries_df, satellite_df))
    all_results.append(validate_coordinate_preservation(fisheries_df, satellite_df))
    
    # Write report
    write_validation_report(all_results)
    
    # Summary
    print("=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print()
    
    passed_count = sum(1 for r in all_results if r["passed"])
    failed_count = len(all_results) - passed_count
    
    print(f"Validation checks: {len(all_results)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print()
    
    if failed_count == 0:
        print("[OK] ALL CHECKS PASSED")
        print()
        print("The satellite dataset is ready for analysis!")
    else:
        print(f"[FAIL] {failed_count} checks failed")
        print()
        print("Please review the validation report for details:")
        print(f"  {VALIDATION_REPORT}")
    
    print()
    print("=" * 80)
    
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()
