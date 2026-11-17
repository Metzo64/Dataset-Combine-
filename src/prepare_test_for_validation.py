"""
Prepare test export for validation

This script:
1. Looks for satellite_test.csv in common locations
2. Copies it to output/satellite_exports/
3. Runs merge script
4. Runs validation script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shutil
from pathlib import Path

# Search locations
search_paths = [
    ".",
    "output",
    "output/satellite_exports",
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Desktop"),
]

test_filename = "satellite_test.csv"
target_dir = "output/satellite_exports"

print("=" * 80)
print("PREPARING TEST EXPORT FOR VALIDATION")
print("=" * 80)
print()

# Search for the file
found_path = None
for search_dir in search_paths:
    search_path = Path(search_dir)
    if search_path.exists():
        test_file = search_path / test_filename
        if test_file.exists():
            found_path = test_file
            print(f"[OK] Found test file: {found_path}")
            break

if not found_path:
    print(f"[ERROR] Could not find {test_filename} in:")
    for path in search_paths:
        print(f"  - {path}")
    print()
    print("Please:")
    print("  1. Download satellite_test.csv from Google Drive")
    print("  2. Place it in one of the above locations")
    print("  3. Or specify location manually")
    sys.exit(1)

# Ensure target directory exists
os.makedirs(target_dir, exist_ok=True)

# Copy to target location
target_path = Path(target_dir) / test_filename
if target_path.exists() and target_path.samefile(found_path):
    print("[INFO] File already in correct location")
else:
    shutil.copy(found_path, target_path)
    print(f"[OK] Copied to: {target_path}")

print()
print("=" * 80)
print("File prepared for validation")
print(f"Location: {target_path}")
print("=" * 80)
print()
print("Next steps:")
print("  1. Run: python src/merge_satellite_exports.py")
print("  2. Run: python src/validate_satellite.py")
