"""
PHASE 6: Merge and Consolidate Satellite Exports

This script consolidates annual satellite data exports from Google Earth Engine
into a single final dataset.

Requirements:
- Annual CSV files in output/satellite_exports/
- All 10 years present (2015-2024)
- 25,000 total records expected
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import glob
from datetime import datetime
from config.config import (
    EXPORTS_DIR,
    FINAL_SATELLITE_CSV,
    EXPECTED_SATELLITE_RECORDS,
    OUTPUT_COLUMNS
)


def find_export_files():
    """
    Find all satellite export CSV files.
    
    Returns:
        list: Sorted list of export file paths
    """
    print("=" * 80)
    print("PHASE 6: MERGE SATELLITE EXPORTS")
    print("=" * 80)
    print()
    
    print(f"Looking for export files in: {EXPORTS_DIR}")
    print()
    
    # Look for annual export files
    pattern = os.path.join(EXPORTS_DIR, "satellite_*.csv")
    files = sorted(glob.glob(pattern))
    
    if not files:
        print(f"ERROR: No export files found matching: {pattern}")
        print()
        print("Please ensure:")
        print("1. You have downloaded CSV exports from Google Drive")
        print("2. Files are placed in: output/satellite_exports/")
        print("3. Files are named: satellite_2015.csv, satellite_2016.csv, etc.")
        return None
    
    print(f"Found {len(files)} export files:")
    for f in files:
        size = os.path.getsize(f) / 1024  # KB
        print(f"  {os.path.basename(f):<30} ({size:>10.1f} KB)")
    print()
    
    return files


def load_and_merge_exports(files):
    """
    Load all export files and merge into single DataFrame.
    
    Args:
        files (list): List of CSV file paths
        
    Returns:
        pd.DataFrame: Merged satellite dataset
    """
    print("-" * 80)
    print("LOADING AND MERGING EXPORTS")
    print("-" * 80)
    print()
    
    dfs = []
    total_records = 0
    
    for filepath in files:
        filename = os.path.basename(filepath)
        print(f"Loading {filename}...", end=" ")
        
        try:
            df = pd.read_csv(filepath)
            
            # Remove GEE system fields if present
            system_cols = ['system:index', '.geo']
            cols_to_drop = [col for col in system_cols if col in df.columns]
            if cols_to_drop:
                df = df.drop(columns=cols_to_drop)
                print(f"[INFO] Removed GEE system columns: {cols_to_drop}", end=" ")
            
            records = len(df)
            total_records += records
            dfs.append(df)
            print(f"[OK] {records:,} records")
        except Exception as e:
            print(f"[ERROR] {e}")
            return None
    
    print()
    print(f"Total records loaded: {total_records:,}")
    print(f"Expected: {EXPECTED_SATELLITE_RECORDS:,}")
    
    if total_records != EXPECTED_SATELLITE_RECORDS:
        print(f"[WARNING] Record count mismatch!")
        print(f"  Loaded: {total_records:,}")
        print(f"  Expected: {EXPECTED_SATELLITE_RECORDS:,}")
        print(f"  Difference: {total_records - EXPECTED_SATELLITE_RECORDS:,}")
    else:
        print("[OK] Record count matches expectation")
    
    print()
    print("Concatenating dataframes...")
    
    merged_df = pd.concat(dfs, ignore_index=True)
    print(f"[OK] Merged dataset: {len(merged_df):,} records, {len(merged_df.columns)} columns")
    print()
    
    return merged_df


def validate_merged_dataset(df):
    """
    Perform basic validation on merged dataset.
    
    Args:
        df (pd.DataFrame): Merged satellite dataset
        
    Returns:
        dict: Validation results
    """
    print("-" * 80)
    print("VALIDATION CHECKS")
    print("-" * 80)
    print()
    
    results = {}
    
    # Check record count
    print("1. Record Count")
    results["total_records"] = len(df)
    print(f"   Total records: {results['total_records']:,}")
    print(f"   Expected: {EXPECTED_SATELLITE_RECORDS:,}")
    
    if results["total_records"] == EXPECTED_SATELLITE_RECORDS:
        print("   [OK] Correct number of records")
    else:
        print("   [WARNING] Record count mismatch")
    print()
    
    # Check for duplicate satellite record IDs
    print("2. Unique Satellite Record IDs")
    if "satellite_record_id" in df.columns:
        results["unique_sat_ids"] = df["satellite_record_id"].nunique()
        results["duplicate_sat_ids"] = len(df) - results["unique_sat_ids"]
        print(f"   Unique satellite_record_id: {results['unique_sat_ids']:,}")
        print(f"   Duplicates: {results['duplicate_sat_ids']:,}")
        
        if results["duplicate_sat_ids"] == 0:
            print("   [OK] All satellite record IDs are unique")
        else:
            print("   [ERROR] Duplicate satellite record IDs found")
            duplicates = df[df.duplicated(subset=["satellite_record_id"], keep=False)]
            print(f"   Sample duplicates: {duplicates['satellite_record_id'].head().tolist()}")
    else:
        print("   [WARNING] Column 'satellite_record_id' not found")
    print()
    
    # Check for duplicate fisheries record IDs
    print("3. Unique Fisheries Record IDs")
    if "fisheries_record_id" in df.columns:
        results["unique_fish_ids"] = df["fisheries_record_id"].nunique()
        results["duplicate_fish_ids"] = len(df) - results["unique_fish_ids"]
        print(f"   Unique fisheries_record_id: {results['unique_fish_ids']:,}")
        print(f"   Duplicates: {results['duplicate_fish_ids']:,}")
        
        if results["duplicate_fish_ids"] == 0:
            print("   [OK] All fisheries record IDs are unique")
        else:
            print("   [WARNING] Some fisheries observations have multiple satellite records")
    else:
        print("   [WARNING] Column 'fisheries_record_id' not found")
    print()
    
    # Check columns
    print("4. Output Columns")
    results["columns"] = list(df.columns)
    print(f"   Columns present: {len(results['columns'])}")
    
    missing_cols = [col for col in OUTPUT_COLUMNS if col not in results["columns"]]
    extra_cols = [col for col in results["columns"] if col not in OUTPUT_COLUMNS]
    
    if missing_cols:
        print(f"   [WARNING] Missing columns: {missing_cols}")
    
    if extra_cols:
        print(f"   [INFO] Extra columns: {extra_cols}")
    
    if not missing_cols:
        print("   [OK] All required columns present")
    print()
    
    # Check missing values
    print("5. Missing Environmental Values")
    if "sea_surface_temperature_c" in df.columns:
        sst = df["sea_surface_temperature_c"]
        sst_valid = sst[sst.notnull()]
        
        results["sst_count"] = len(sst)
        results["sst_missing"] = sst.isnull().sum()
        results["sst_missing_pct"] = results["sst_missing"] / len(sst) * 100
        print(f"   SST missing: {results['sst_missing']:,} ({results['sst_missing_pct']:.1f}%)")
        
        # Check for realistic values
        if len(sst_valid) > 0:
            results["sst_min"] = sst_valid.min()
            results["sst_max"] = sst_valid.max()
            results["sst_mean"] = sst_valid.mean()
            
            print(f"   SST range: {results['sst_min']:.2f}°C to {results['sst_max']:.2f}°C")
            print(f"   SST mean: {results['sst_mean']:.2f}°C")
            
            # Check for unscaled values (>100 indicates scaling not applied)
            unscaled_count = (sst_valid > 100).sum()
            if unscaled_count > 0:
                print(f"   [ERROR] {unscaled_count} SST values > 100°C - SCALING NOT APPLIED!")
                results["sst_scaling_issue"] = True
            else:
                print(f"   [OK] SST values appear properly scaled")
                results["sst_scaling_issue"] = False
    
    if "chlorophyll_a_mg_m3" in df.columns:
        chl = df["chlorophyll_a_mg_m3"]
        chl_valid = chl[chl.notnull()]
        
        results["chl_count"] = len(chl)
        results["chl_missing"] = chl.isnull().sum()
        results["chl_missing_pct"] = results["chl_missing"] / len(chl) * 100
        print(f"   Chlorophyll missing: {results['chl_missing']:,} ({results['chl_missing_pct']:.1f}%)")
        
        if len(chl_valid) > 0:
            results["chl_min"] = chl_valid.min()
            results["chl_max"] = chl_valid.max()
            results["chl_mean"] = chl_valid.mean()
            print(f"   Chlorophyll range: {results['chl_min']:.4f} to {results['chl_max']:.4f} mg/m³")
            print(f"   Chlorophyll mean: {results['chl_mean']:.4f} mg/m³")
    
    print()
    print("   Note: Some missing values are expected, especially for chlorophyll")
    print("   due to cloud cover and sensor limitations.")
    print()
    
    # Check date range
    print("6. Temporal Coverage")
    if "date" in df.columns:
        df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
        results["date_min"] = df["date_parsed"].min()
        results["date_max"] = df["date_parsed"].max()
        print(f"   Date range: {results['date_min'].strftime('%Y-%m-%d')} to {results['date_max'].strftime('%Y-%m-%d')}")
        
        if results["date_min"].year == 2015 and results["date_max"].year == 2024:
            print("   [OK] Covers expected period (2015-2024)")
        else:
            print("   [WARNING] Date range unexpected")
    print()
    
    return results


def reorder_columns(df):
    """
    Reorder columns to match expected output schema.
    
    Args:
        df (pd.DataFrame): Satellite dataset
        
    Returns:
        pd.DataFrame: Dataset with reordered columns
    """
    print("-" * 80)
    print("REORDERING COLUMNS")
    print("-" * 80)
    print()
    
    # Reorder columns to match OUTPUT_COLUMNS
    available_cols = [col for col in OUTPUT_COLUMNS if col in df.columns]
    extra_cols = [col for col in df.columns if col not in OUTPUT_COLUMNS]
    
    ordered_cols = available_cols + extra_cols
    df_ordered = df[ordered_cols].copy()
    
    print(f"Column order:")
    for i, col in enumerate(ordered_cols, 1):
        print(f"  {i:2d}. {col}")
    print()
    
    return df_ordered


def save_final_dataset(df):
    """
    Save the final merged and validated satellite dataset.
    
    Args:
        df (pd.DataFrame): Final satellite dataset
    """
    print("-" * 80)
    print("SAVING FINAL DATASET")
    print("-" * 80)
    print()
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(FINAL_SATELLITE_CSV), exist_ok=True)
    
    print(f"Saving to: {FINAL_SATELLITE_CSV}")
    
    try:
        df.to_csv(FINAL_SATELLITE_CSV, index=False, encoding="utf-8")
        
        # Verify file was created
        if os.path.exists(FINAL_SATELLITE_CSV):
            file_size = os.path.getsize(FINAL_SATELLITE_CSV) / 1024 / 1024  # MB
            print(f"[OK] File saved successfully ({file_size:.2f} MB)")
        else:
            print("[ERROR] File not found after save")
    except Exception as e:
        print(f"[ERROR] Failed to save file: {e}")
        return False
    
    print()
    return True


def main():
    """
    Main execution function.
    """
    print()
    print("=" * 80)
    print("SATELLITE EXPORT CONSOLIDATION")
    print("=" * 80)
    print()
    
    # Find export files
    files = find_export_files()
    if files is None:
        print("[ERROR] No export files found. Exiting.")
        sys.exit(1)
    
    # Load and merge
    merged_df = load_and_merge_exports(files)
    if merged_df is None:
        print("[ERROR] Failed to load exports. Exiting.")
        sys.exit(1)
    
    # Validate
    validation_results = validate_merged_dataset(merged_df)
    
    # Reorder columns
    final_df = reorder_columns(merged_df)
    
    # Save
    success = save_final_dataset(final_df)
    
    if not success:
        print("[ERROR] Failed to save final dataset. Exiting.")
        sys.exit(1)
    
    # Summary
    print("=" * 80)
    print("CONSOLIDATION COMPLETE")
    print("=" * 80)
    print()
    print(f"Final dataset: {FINAL_SATELLITE_CSV}")
    print(f"Total records: {len(final_df):,}")
    print(f"Total columns: {len(final_df.columns)}")
    print()
    
    if validation_results.get("duplicate_sat_ids", 0) > 0:
        print("[WARNING] Dataset contains duplicate satellite record IDs")
    
    if validation_results.get("duplicate_fish_ids", 0) > 0:
        print("[WARNING] Dataset contains duplicate fisheries record IDs")
    
    print()
    print("Next steps:")
    print("1. Run validation: python src/validate_satellite.py")
    print("2. Review validation report: output/reports/satellite_validation_report.txt")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
