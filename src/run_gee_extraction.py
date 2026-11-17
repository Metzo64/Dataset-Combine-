"""
AUTOMATED GOOGLE EARTH ENGINE SATELLITE EXTRACTION

This script performs automated satellite data extraction using the
Google Earth Engine Python API.

Features:
- Automated authentication
- Direct Python API processing (no manual JavaScript)
- Batch processing with progress monitoring
- Automated export monitoring and download
- Comprehensive error handling and recovery

Usage:
    python src/run_gee_extraction.py --test     # Test with small batch
    python src/run_gee_extraction.py --full     # Full extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import time
import pandas as pd
import ee
from datetime import datetime
from tqdm import tqdm

from config.config import (
    FISHERIES_CSV,
    EXPORTS_DIR,
    LOGS_DIR,
    STUDY_AREA,
    START_DATE,
    END_DATE,
    SST_DATASET,
    CHLOROPHYLL_DATASET,
    CHLOROPHYLL_ALTERNATIVE,
    EXPORT_BATCH_SIZE,
    EXPORT_TEST_BATCH_SIZE,
    EXPORT_DRIVE_FOLDER,
    MAX_FEATURES_PER_BATCH,
    MAX_CONCURRENT_TASKS,
    TASK_CHECK_INTERVAL
)

from gee_auth import setup_earth_engine


class GEESatelliteExtractor:
    """
    Google Earth Engine Satellite Data Extractor
    """
    
    def __init__(self, test_mode=False):
        """
        Initialize the extractor.
        
        Args:
            test_mode (bool): If True, process only a small test batch
        """
        self.test_mode = test_mode
        self.fisheries_df = None
        self.sst_collection = None
        self.chl_collection = None
        self.study_area_geom = None
        self.active_tasks = []
        self.completed_tasks = []
        self.failed_tasks = []
        
        # Setup logging
        self.log_file = os.path.join(
            LOGS_DIR, 
            f"gee_extraction_{'test' if test_mode else 'full'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        os.makedirs(LOGS_DIR, exist_ok=True)
    
    def log(self, message):
        """Log message to console and file."""
        print(message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    
    def load_fisheries_data(self):
        """Load and validate fisheries reference dataset."""
        self.log("=" * 80)
        self.log("LOADING FISHERIES REFERENCE DATASET")
        self.log("=" * 80)
        self.log("")
        
        if not os.path.exists(FISHERIES_CSV):
            self.log(f"[ERROR] Fisheries CSV not found: {FISHERIES_CSV}")
            return False
        
        try:
            self.fisheries_df = pd.read_csv(FISHERIES_CSV)
            self.log(f"[OK] Loaded {len(self.fisheries_df):,} fisheries records")
            self.log("")
            
            # Validate required columns
            required_cols = ['fisheries_record_id', 'date', 'lat', 'lon']
            missing_cols = [col for col in required_cols if col not in self.fisheries_df.columns]
            
            if missing_cols:
                self.log(f"[ERROR] Missing required columns: {missing_cols}")
                return False
            
            self.log("[OK] All required columns present")
            self.log("")
            
            # Filter to study period
            self.fisheries_df['date_parsed'] = pd.to_datetime(self.fisheries_df['date'])
            study_start = pd.to_datetime(START_DATE)
            study_end = pd.to_datetime(END_DATE)
            
            self.fisheries_df = self.fisheries_df[
                (self.fisheries_df['date_parsed'] >= study_start) &
                (self.fisheries_df['date_parsed'] <= study_end)
            ].copy()
            
            self.log(f"Records within study period (2015-2024): {len(self.fisheries_df):,}")
            self.log("")
            
            # Filter to study area
            self.fisheries_df = self.fisheries_df[
                (self.fisheries_df['lat'] >= STUDY_AREA['south']) &
                (self.fisheries_df['lat'] <= STUDY_AREA['north']) &
                (self.fisheries_df['lon'] >= STUDY_AREA['west']) &
                (self.fisheries_df['lon'] <= STUDY_AREA['east'])
            ].copy()
            
            self.log(f"Records within study area: {len(self.fisheries_df):,}")
            self.log("")
            
            # Test mode: use only first month
            if self.test_mode:
                first_month = self.fisheries_df['date_parsed'].dt.to_period('M').min()
                self.fisheries_df = self.fisheries_df[
                    self.fisheries_df['date_parsed'].dt.to_period('M') == first_month
                ].head(EXPORT_TEST_BATCH_SIZE).copy()
                self.log(f"[TEST MODE] Using only {len(self.fisheries_df)} records from {first_month}")
                self.log("")
            
            return True
            
        except Exception as e:
            self.log(f"[ERROR] Failed to load fisheries data: {e}")
            return False
    
    def setup_gee_collections(self):
        """Setup Google Earth Engine image collections."""
        self.log("=" * 80)
        self.log("SETTING UP SATELLITE DATA COLLECTIONS")
        self.log("=" * 80)
        self.log("")
        
        try:
            # Define study area geometry
            self.study_area_geom = ee.Geometry.Rectangle([
                STUDY_AREA['west'],
                STUDY_AREA['south'],
                STUDY_AREA['east'],
                STUDY_AREA['north']
            ])
            self.log("[OK] Study area geometry created")
            self.log("")
            
            # Setup SST collection
            self.log(f"Loading SST collection: {SST_DATASET['id']}")
            self.sst_collection = ee.ImageCollection(SST_DATASET['id']) \
                .filterBounds(self.study_area_geom) \
                .filterDate(START_DATE, END_DATE) \
                .select(SST_DATASET['band'])
            
            sst_count = self.sst_collection.size().getInfo()
            self.log(f"[OK] SST images available: {sst_count}")
            self.log(f"     Scale factor: {SST_DATASET['scale_factor']} (raw values will be multiplied)")
            self.log("")
            
            # Setup Chlorophyll collection - try primary first
            try:
                self.log(f"Loading Chlorophyll collection: {CHLOROPHYLL_DATASET['id']}")
                self.chl_collection = ee.ImageCollection(CHLOROPHYLL_DATASET['id']) \
                    .filterBounds(self.study_area_geom) \
                    .filterDate(START_DATE, END_DATE) \
                    .select(CHLOROPHYLL_DATASET['band'])
                
                chl_count = self.chl_collection.size().getInfo()
                self.log(f"[OK] Chlorophyll images available: {chl_count}")
                self.log(f"     Band: {CHLOROPHYLL_DATASET['band']}")
                self.log(f"     Units: {CHLOROPHYLL_DATASET['units']}")
                
                # Test a specific date to check availability
                test_date = '2015-01-15'
                test_images = self.chl_collection.filterDate(test_date, '2015-01-16')
                test_count = test_images.size().getInfo()
                self.log(f"     Test date ({test_date}): {test_count} images available")
                
                if test_count == 0:
                    self.log(f"     [WARNING] No chlorophyll images for test date!")
                    self.log(f"     This may indicate sparse temporal coverage.")
                
                self.chl_source = CHLOROPHYLL_DATASET
            except Exception as e:
                self.log(f"[WARNING] Primary chlorophyll source failed: {e}")
                self.log(f"Trying alternative: {CHLOROPHYLL_ALTERNATIVE['id']}")
                
                self.chl_collection = ee.ImageCollection(CHLOROPHYLL_ALTERNATIVE['id']) \
                    .filterBounds(self.study_area_geom) \
                    .filterDate(START_DATE, END_DATE) \
                    .select(CHLOROPHYLL_ALTERNATIVE['band'])
                
                chl_count = self.chl_collection.size().getInfo()
                self.log(f"[OK] Chlorophyll images available (alternative): {chl_count}")
                self.chl_source = CHLOROPHYLL_ALTERNATIVE
            
            self.log("")
            return True
            
        except Exception as e:
            self.log(f"[ERROR] Failed to setup GEE collections: {e}")
            return False
    
    def create_point_features(self, df_batch):
        """
        Convert fisheries observations to EE features.
        
        Args:
            df_batch (pd.DataFrame): Batch of fisheries observations
            
        Returns:
            ee.FeatureCollection: Point features
        """
        features = []
        
        for idx, row in df_batch.iterrows():
            point = ee.Geometry.Point([row['lon'], row['lat']])
            feature = ee.Feature(point, {
                'fisheries_record_id': int(row['fisheries_record_id']),
                'date': row['date'],
                'latitude': float(row['lat']),
                'longitude': float(row['lon'])
            })
            features.append(feature)
        
        return ee.FeatureCollection(features)
    
    def extract_environmental_data(self, feature):
        """
        Extract SST and chlorophyll for a single feature.
        
        CRITICAL: SST scaling must be applied to the IMAGE before sampling,
        not to the extracted value, to ensure the scaled value is exported.
        
        Args:
            feature (ee.Feature): Point feature with date and location
            
        Returns:
            ee.Feature: Feature with environmental data added
        """
        # Get date and point
        date = ee.Date(feature.get('date'))
        point = feature.geometry()
        
        # Extract SST with scaling applied to IMAGE
        # NOAA OISST stores values scaled by 100 (raw value 2835 = 28.35°C)
        # Must multiply the IMAGE by 0.01 BEFORE sampling
        sst_image_raw = self.sst_collection \
            .filterDate(date, date.advance(1, 'day')) \
            .first()
        
        # Scale the image itself so the export contains scaled values
        sst_image_scaled = ee.Algorithms.If(
            sst_image_raw,
            sst_image_raw.multiply(SST_DATASET['scale_factor']),
            None
        )
        
        # Sample the scaled image
        sst_value = ee.Algorithms.If(
            sst_image_scaled,
            ee.Image(sst_image_scaled).reduceRegion(
                reducer=ee.Reducer.first(),
                geometry=point,
                scale=1000
            ).get(SST_DATASET['band']),
            None
        )
        
        # Extract Chlorophyll (no scaling needed)
        chl_image = self.chl_collection \
            .filterDate(date, date.advance(1, 'day')) \
            .first()
        
        chl_value = ee.Algorithms.If(
            chl_image,
            chl_image.reduceRegion(
                reducer=ee.Reducer.first(),
                geometry=point,
                scale=1000
            ).get(self.chl_source['band']),
            None
        )
        
        # Add metadata
        year = date.get('year')
        month = date.get('month')
        
        return feature.set({
            'year': year,
            'month': month,
            'sea_surface_temperature_c': sst_value,
            'chlorophyll_a_mg_m3': chl_value,
            'sst_source': SST_DATASET['name'],
            'chlorophyll_source': self.chl_source['name'],
            'sst_dataset_id': SST_DATASET['id'],
            'chlorophyll_dataset_id': self.chl_source['id']
        })
    
    def process_batch(self, batch_df, batch_name):
        """
        Process a batch of observations and create export task.
        
        Args:
            batch_df (pd.DataFrame): Batch of observations
            batch_name (str): Name for this batch
            
        Returns:
            ee.batch.Task or None: Export task
        """
        self.log(f"Processing batch: {batch_name} ({len(batch_df)} records)")
        
        try:
            # Create features
            features = self.create_point_features(batch_df)
            
            # Apply environmental extraction
            features_with_env = features.map(self.extract_environmental_data)
            
            # Create export task
            task = ee.batch.Export.table.toDrive(
                collection=features_with_env,
                description=f'satellite_{batch_name}',
                folder=EXPORT_DRIVE_FOLDER,
                fileNamePrefix=f'satellite_{batch_name}',
                fileFormat='CSV'
            )
            
            return task
            
        except Exception as e:
            self.log(f"[ERROR] Failed to process batch {batch_name}: {e}")
            return None
    
    def start_export_tasks(self):
        """
        Create and start all export tasks.
        """
        self.log("=" * 80)
        self.log("CREATING EXPORT TASKS")
        self.log("=" * 80)
        self.log("")
        
        # Group by year for batching
        self.fisheries_df['year'] = self.fisheries_df['date_parsed'].dt.year
        
        if self.test_mode:
            # Single test batch
            batch_name = "test"
            task = self.process_batch(self.fisheries_df, batch_name)
            if task:
                self.log(f"Starting export task: {batch_name}")
                task.start()
                self.active_tasks.append({
                    'task': task,
                    'name': batch_name,
                    'records': len(self.fisheries_df),
                    'start_time': datetime.now()
                })
                self.log(f"[OK] Task started: {batch_name}")
                self.log("")
        else:
            # Annual batches
            for year in sorted(self.fisheries_df['year'].unique()):
                year_df = self.fisheries_df[self.fisheries_df['year'] == year]
                batch_name = str(year)
                
                task = self.process_batch(year_df, batch_name)
                if task:
                    self.log(f"Starting export task: {batch_name}")
                    task.start()
                    self.active_tasks.append({
                        'task': task,
                        'name': batch_name,
                        'records': len(year_df),
                        'start_time': datetime.now()
                    })
                    self.log(f"[OK] Task started: {batch_name}")
                    self.log("")
                    
                    # Limit concurrent tasks
                    if len(self.active_tasks) >= MAX_CONCURRENT_TASKS:
                        self.log(f"Reached max concurrent tasks ({MAX_CONCURRENT_TASKS}), waiting...")
                        self.wait_for_tasks(wait_for_all=False)
        
        self.log(f"Total export tasks created: {len(self.active_tasks)}")
        self.log("")
    
    def wait_for_tasks(self, wait_for_all=True):
        """
        Monitor and wait for export tasks to complete.
        
        Args:
            wait_for_all (bool): If True, wait for all tasks. If False, wait until one completes.
        """
        self.log("=" * 80)
        self.log("MONITORING EXPORT TASKS")
        self.log("=" * 80)
        self.log("")
        
        initial_active = len(self.active_tasks)
        
        with tqdm(total=initial_active, desc="Export Progress") as pbar:
            while self.active_tasks:
                time.sleep(TASK_CHECK_INTERVAL)
                
                still_active = []
                
                for task_info in self.active_tasks:
                    task = task_info['task']
                    status = task.status()
                    state = status['state']
                    
                    if state == 'COMPLETED':
                        elapsed = (datetime.now() - task_info['start_time']).total_seconds()
                        self.log(f"[OK] Task completed: {task_info['name']} ({elapsed:.0f}s)")
                        self.completed_tasks.append(task_info)
                        pbar.update(1)
                        
                        if not wait_for_all:
                            # Move remaining tasks back
                            still_active.extend([t for t in self.active_tasks if t != task_info])
                            self.active_tasks = still_active
                            return
                    
                    elif state == 'FAILED':
                        self.log(f"[ERROR] Task failed: {task_info['name']}")
                        self.log(f"  Error: {status.get('error_message', 'Unknown error')}")
                        self.failed_tasks.append(task_info)
                        pbar.update(1)
                    
                    elif state in ['RUNNING', 'READY']:
                        still_active.append(task_info)
                    
                    else:
                        self.log(f"[WARNING] Task in unexpected state: {task_info['name']} - {state}")
                        still_active.append(task_info)
                
                self.active_tasks = still_active
                
                if not wait_for_all and len(still_active) < MAX_CONCURRENT_TASKS:
                    return
        
        self.log("")
        self.log(f"Tasks completed: {len(self.completed_tasks)}")
        self.log(f"Tasks failed: {len(self.failed_tasks)}")
        self.log("")
    
    def run(self):
        """
        Execute the complete extraction pipeline.
        """
        self.log("")
        self.log("=" * 80)
        self.log(f"GOOGLE EARTH ENGINE SATELLITE EXTRACTION")
        self.log(f"MODE: {'TEST' if self.test_mode else 'FULL'}")
        self.log("=" * 80)
        self.log("")
        
        # Step 1: Setup Earth Engine
        self.log("Step 1: Setting up Earth Engine...")
        if not setup_earth_engine():
            self.log("[ERROR] Earth Engine setup failed")
            return False
        
        # Step 2: Load fisheries data
        self.log("Step 2: Loading fisheries data...")
        if not self.load_fisheries_data():
            self.log("[ERROR] Failed to load fisheries data")
            return False
        
        # Step 3: Setup GEE collections
        self.log("Step 3: Setting up satellite collections...")
        if not self.setup_gee_collections():
            self.log("[ERROR] Failed to setup GEE collections")
            return False
        
        # Step 4: Start export tasks
        self.log("Step 4: Starting export tasks...")
        self.start_export_tasks()
        
        # Step 5: Wait for completion
        self.log("Step 5: Waiting for tasks to complete...")
        self.wait_for_tasks(wait_for_all=True)
        
        # Summary
        self.log("=" * 80)
        self.log("EXTRACTION SUMMARY")
        self.log("=" * 80)
        self.log("")
        self.log(f"Tasks completed: {len(self.completed_tasks)}")
        self.log(f"Tasks failed: {len(self.failed_tasks)}")
        self.log(f"Total records processed: {sum(t['records'] for t in self.completed_tasks)}")
        self.log("")
        
        if self.failed_tasks:
            self.log("[WARNING] Some tasks failed. Check log for details.")
            self.log("")
        
        self.log(f"Log file: {self.log_file}")
        self.log("")
        self.log("=" * 80)
        self.log("NEXT STEPS")
        self.log("=" * 80)
        self.log("")
        self.log("Exports have been created in Google Drive.")
        self.log(f"Folder: {EXPORT_DRIVE_FOLDER}")
        self.log("")
        self.log("To download and consolidate:")
        self.log("  python src/download_gee_exports.py")
        self.log("")
        
        return len(self.failed_tasks) == 0


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Automated Google Earth Engine Satellite Data Extraction'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (small batch)'
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='Run full extraction (all years)'
    )
    
    args = parser.parse_args()
    
    if not args.test and not args.full:
        print("Please specify --test or --full mode")
        print()
        print("Usage:")
        print("  python src/run_gee_extraction.py --test   # Test with small batch")
        print("  python src/run_gee_extraction.py --full   # Full extraction")
        sys.exit(1)
    
    # Create extractor
    extractor = GEESatelliteExtractor(test_mode=args.test)
    
    # Run extraction
    success = extractor.run()
    
    if success:
        print()
        print("[OK] Extraction completed successfully!")
        sys.exit(0)
    else:
        print()
        print("[ERROR] Extraction completed with errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
