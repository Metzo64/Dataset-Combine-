"""
Google Earth Engine Authentication and Initialization Module

This module handles Earth Engine authentication and initialization,
checking for existing credentials and guiding the user through
authentication if needed.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ee
from config.config import GEE_PROJECT_ID


def check_ee_credentials():
    """
    Check if Earth Engine credentials exist.
    
    Returns:
        bool: True if credentials exist, False otherwise
    """
    try:
        # Try to initialize without authentication
        # This will succeed if credentials already exist
        ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
        return True
    except Exception:
        return False


def authenticate_earth_engine():
    """
    Authenticate with Google Earth Engine.
    
    This launches an interactive authentication flow in the browser.
    """
    print("=" * 80)
    print("GOOGLE EARTH ENGINE AUTHENTICATION")
    print("=" * 80)
    print()
    print("Earth Engine credentials not found or expired.")
    print()
    print("You will be redirected to a browser to authenticate.")
    print("Please:")
    print("  1. Sign in with your Google account")
    print("  2. Grant Earth Engine API access")
    print("  3. Return to this terminal after authentication completes")
    print()
    print("Starting authentication...")
    print()
    
    try:
        ee.Authenticate()
        print()
        print("[OK] Authentication successful!")
        print()
        return True
    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")
        print()
        print("Please ensure:")
        print("  1. You have a Google account")
        print("  2. You have registered for Earth Engine: https://earthengine.google.com/")
        print("  3. Your Earth Engine access has been approved")
        print()
        return False


def initialize_earth_engine(project_id=None):
    """
    Initialize Google Earth Engine with project ID.
    
    Args:
        project_id (str): Google Cloud Project ID
        
    Returns:
        bool: True if initialization successful, False otherwise
    """
    print("=" * 80)
    print("INITIALIZING GOOGLE EARTH ENGINE")
    print("=" * 80)
    print()
    
    # Use provided project_id or fall back to config
    if project_id is None:
        project_id = GEE_PROJECT_ID
    
    # Check if project ID is configured
    if project_id is None or project_id == "":
        print("[ERROR] Google Cloud Project ID not configured")
        print()
        print("Please configure your Project ID:")
        print("  1. Go to: https://console.cloud.google.com/")
        print("  2. Select or create a project")
        print("  3. Enable Earth Engine API for the project")
        print("  4. Copy the Project ID (not the project name)")
        print("  5. Update config/config.py: GEE_PROJECT_ID = 'your-project-id'")
        print()
        print("Alternatively, you can initialize without a project ID,")
        print("but some features may be limited.")
        print()
        
        # Try to initialize without project ID
        try:
            print("Attempting initialization without project ID...")
            ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
            print("[WARNING] Initialized without project ID - some features may be limited")
            print()
            return True
        except Exception as e:
            print(f"[ERROR] Initialization failed: {e}")
            print()
            return False
    
    # Initialize with project ID
    try:
        print(f"Project ID: {project_id}")
        ee.Initialize(project=project_id, opt_url='https://earthengine-highvolume.googleapis.com')
        print("[OK] Earth Engine initialized successfully")
        print()
        return True
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        print()
        print("Common issues:")
        print("  1. Project ID is incorrect")
        print("  2. Earth Engine API not enabled for this project")
        print("     Enable at: https://console.cloud.google.com/apis/library/earthengine.googleapis.com")
        print("  3. You don't have permission to access this project")
        print()
        
        # Try without project ID as fallback
        try:
            print("Attempting initialization without project ID...")
            ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
            print("[WARNING] Initialized without project ID - some features may be limited")
            print()
            return True
        except Exception as e2:
            print(f"[ERROR] Fallback initialization also failed: {e2}")
            print()
            return False


def setup_earth_engine(project_id=None):
    """
    Complete Earth Engine setup: authenticate if needed, then initialize.
    
    Args:
        project_id (str): Optional Google Cloud Project ID
        
    Returns:
        bool: True if setup successful, False otherwise
    """
    print()
    print("=" * 80)
    print("GOOGLE EARTH ENGINE SETUP")
    print("=" * 80)
    print()
    
    # Check for existing credentials
    if check_ee_credentials():
        print("[OK] Earth Engine credentials found")
        print()
    else:
        print("Earth Engine credentials not found")
        print()
        
        # Authenticate
        if not authenticate_earth_engine():
            return False
    
    # Initialize
    if not initialize_earth_engine(project_id):
        return False
    
    # Test connection
    print("Testing Earth Engine connection...")
    try:
        # Try a simple operation
        point = ee.Geometry.Point([0, 0])
        result = point.getInfo()
        print("[OK] Earth Engine connection test successful")
        print()
        return True
    except Exception as e:
        print(f"[ERROR] Connection test failed: {e}")
        print()
        return False


def get_gee_info():
    """
    Get information about the current Earth Engine session.
    
    Returns:
        dict: Session information
    """
    try:
        # Get user info (if available)
        info = {
            "authenticated": True,
            "test_successful": False
        }
        
        # Try a simple operation
        try:
            point = ee.Geometry.Point([0, 0])
            result = point.getInfo()
            info["test_successful"] = True
        except:
            pass
        
        return info
    except:
        return {
            "authenticated": False,
            "test_successful": False
        }


if __name__ == "__main__":
    """
    Test Earth Engine authentication and initialization.
    """
    print()
    print("=" * 80)
    print("EARTH ENGINE AUTHENTICATION TEST")
    print("=" * 80)
    print()
    
    # Run setup
    success = setup_earth_engine()
    
    if success:
        print("=" * 80)
        print("SETUP SUCCESSFUL")
        print("=" * 80)
        print()
        print("Earth Engine is ready to use!")
        print()
        print("Next steps:")
        print("  1. Run: python src/run_gee_extraction.py --test")
        print("  2. Review test results")
        print("  3. Run full extraction: python src/run_gee_extraction.py --full")
        print()
    else:
        print("=" * 80)
        print("SETUP FAILED")
        print("=" * 80)
        print()
        print("Please resolve the issues above and try again.")
        print()
        sys.exit(1)
