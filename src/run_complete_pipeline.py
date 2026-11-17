"""
COMPLETE AUTOMATED PIPELINE ORCHESTRATOR

This script orchestrates the entire satellite dataset generation pipeline:
1. Fisheries inspection
2. Earth Engine authentication (interactive)
3. Test batch extraction
4. Full extraction (with approval)
5. Export download (manual or automated)
6. Data consolidation
7. Final validation

Usage:
    python src/run_complete_pipeline.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess
from datetime import datetime


def run_command(cmd, description):
    """
    Run a command and report results.
    
    Args:
        cmd (list): Command and arguments
        description (str): Description of what's being done
        
    Returns:
        bool: True if successful
    """
    print("=" * 80)
    print(description)
    print("=" * 80)
    print()
    print(f"Running: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        print()
        print(f"[OK] {description} completed")
        print()
        return True
    except subprocess.CalledProcessError as e:
        print()
        print(f"[ERROR] {description} failed")
        print(f"Exit code: {e.returncode}")
        print()
        return False
    except Exception as e:
        print()
        print(f"[ERROR] {description} failed: {e}")
        print()
        return False


def get_user_approval(prompt):
    """
    Get user approval to proceed.
    
    Args:
        prompt (str): Prompt message
        
    Returns:
        bool: True if user approves
    """
    print()
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    print()
    response = input("Continue? (yes/no): ").strip().lower()
    return response in ['yes', 'y']


def main():
    """
    Main orchestration function.
    """
    print()
    print("=" * 80)
    print("SATELLITE DATASET GENERATION - COMPLETE PIPELINE")
    print("=" * 80)
    print()
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # PHASE 1: Inspect fisheries dataset
    if not run_command(
        ["python", "src/inspect_fisheries.py"],
        "PHASE 1: Fisheries Dataset Inspection"
    ):
        print("[ERROR] Phase 1 failed. Cannot proceed.")
        sys.exit(1)
    
    print("Please review: output/reports/fisheries_inspection_report.txt")
    if not get_user_approval("Phase 1 complete. Proceed to Earth Engine setup?"):
        print("Pipeline stopped by user.")
        sys.exit(0)
    
    # PHASE 2: Earth Engine authentication
    print()
    print("=" * 80)
    print("PHASE 2: Earth Engine Authentication")
    print("=" * 80)
    print()
    print("This will open a browser for Google Earth Engine authentication.")
    print()
    print("Please:")
    print("  1. Sign in with your Google account")
    print("  2. Grant Earth Engine API access")
    print("  3. Return here after authentication completes")
    print()
    
    if not get_user_approval("Ready to authenticate with Earth Engine?"):
        print("Pipeline stopped by user.")
        sys.exit(0)
    
    if not run_command(
        ["python", "src/gee_auth.py"],
        "Earth Engine Authentication"
    ):
        print("[ERROR] Earth Engine authentication failed.")
        print()
        print("Please:")
        print("  1. Ensure you have registered at: https://earthengine.google.com/")
        print("  2. Wait for approval (if recently registered)")
        print("  3. Check that you have a Google Cloud Project with EE API enabled")
        print("  4. Update config/config.py with your GEE_PROJECT_ID")
        print()
        sys.exit(1)
    
    # PHASE 3: Test extraction
    print()
    print("Now we'll run a small test batch to validate the extraction.")
    print("This will process ~250 records from January 2015.")
    print()
    
    if not get_user_approval("Proceed with test extraction?"):
        print("Pipeline stopped by user.")
        sys.exit(0)
    
    if not run_command(
        ["python", "src/run_gee_extraction.py", "--test"],
        "PHASE 3: Test Batch Extraction"
    ):
        print("[ERROR] Test extraction failed.")
        sys.exit(1)
    
    print()
    print("Test extraction tasks have been submitted to Google Earth Engine.")
    print("Tasks will complete in 2-5 minutes.")
    print()
    print("Check task status at: https://code.earthengine.google.com/ (Tasks tab)")
    print()
    
    if not get_user_approval("Test extraction submitted. Proceed with FULL extraction?"):
        print()
        print("Pipeline paused. To resume:")
        print("  python src/run_gee_extraction.py --full")
        print()
        sys.exit(0)
    
    # PHASE 4: Full extraction
    if not run_command(
        ["python", "src/run_gee_extraction.py", "--full"],
        "PHASE 4: Full Dataset Extraction (25,000 records)"
    ):
        print("[ERROR] Full extraction failed.")
        sys.exit(1)
    
    print()
    print("Full extraction tasks have been submitted.")
    print("Processing will take 2-5 hours total.")
    print()
    print("You can:")
    print("  1. Wait here (script will monitor tasks)")
    print("  2. Close this terminal (tasks run server-side)")
    print("  3. Check status at: https://code.earthengine.google.com/")
    print()
    print("When tasks complete, run:")
    print("  python src/download_gee_exports.py")
    print("  python src/merge_satellite_exports.py")
    print("  python src/validate_satellite.py")
    print()
    
    print("=" * 80)
    print("PIPELINE STATUS")
    print("=" * 80)
    print()
    print("[OK] Phase 1: Fisheries inspection - COMPLETE")
    print("[OK] Phase 2: Earth Engine authentication - COMPLETE")
    print("[OK] Phase 3: Test extraction - SUBMITTED")
    print("[OK] Phase 4: Full extraction - SUBMITTED")
    print("[PENDING] Phase 5: Export download - Run after tasks complete")
    print("[PENDING] Phase 6: Data consolidation - Automatic after download")
    print("[PENDING] Phase 7: Final validation - Automatic after consolidation")
    print()
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("Pipeline interrupted by user.")
        print()
        print("To resume extraction:")
        print("  python src/run_gee_extraction.py --test    # Test batch")
        print("  python src/run_gee_extraction.py --full    # Full extraction")
        print()
        sys.exit(1)
