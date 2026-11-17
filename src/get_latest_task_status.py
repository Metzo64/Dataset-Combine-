"""
Get status of the most recent GEE task
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ee
from gee_auth import setup_earth_engine
from datetime import datetime

# Setup EE (silent)
try:
    ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
except:
    print("Authentication required. Run: python src/gee_auth.py")
    sys.exit(1)

# Get most recent task
try:
    tasks = ee.data.getTaskList()
    
    if not tasks:
        print("No tasks found")
        sys.exit(0)
    
    # Get most recent task
    task = tasks[0]
    
    print("=" * 80)
    print("MOST RECENT GEE TASK STATUS")
    print("=" * 80)
    print()
    print(f"Description: {task.get('description', 'N/A')}")
    print(f"State: {task.get('state', 'N/A')}")
    print(f"Task Type: {task.get('task_type', 'N/A')}")
    print()
    
    # Show timestamp
    ts_ms = task.get('creation_timestamp_ms', 0)
    if ts_ms:
        ts = datetime.fromtimestamp(ts_ms / 1000)
        print(f"Created: {ts.strftime('%Y-%m-%d %H:%M:%S')}")
    
    update_ms = task.get('update_timestamp_ms', 0)
    if update_ms:
        ts = datetime.fromtimestamp(update_ms / 1000)
        print(f"Updated: {ts.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print()
    
    # State-specific info
    state = task.get('state', 'UNKNOWN')
    
    if state == 'COMPLETED':
        print("[OK] Task completed successfully!")
        print()
        print("Output should be available in Google Drive:")
        print(f"  Folder: GEE_Satellite_Exports")
        print(f"  File: satellite_test.csv")
        print()
    elif state == 'RUNNING':
        print("[INFO] Task is currently running...")
        print("Check back in a few minutes.")
        print()
    elif state == 'READY':
        print("[INFO] Task is queued and ready to run...")
        print()
    elif state == 'FAILED':
        print("[ERROR] Task failed!")
        print(f"Error: {task.get('error_message', 'Unknown error')}")
        print()
    elif state == 'CANCELLED':
        print("[WARNING] Task was cancelled")
        print()
    else:
        print(f"[INFO] Task state: {state}")
        print()
    
    print("=" * 80)
    
except Exception as e:
    print(f"Error getting task status: {e}")
    sys.exit(1)
