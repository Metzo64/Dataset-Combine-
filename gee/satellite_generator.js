/*******************************************************************************
 * SATELLITE ENVIRONMENTAL DATA EXTRACTION
 * 
 * Project: Satellite Dataset Generation using Google Earth Engine
 * Purpose: Extract SST and Chlorophyll-a for 25,000 fisheries observations
 * Study Period: 2015-2024
 * Study Area: 0°-30°N, 50°-100°E (Northern Indian Ocean)
 * 
 * Instructions:
 * 1. Upload fisheries_25000.csv as a GEE Table Asset
 * 2. Update FISHERIES_ASSET variable below with your asset ID
 * 3. Click "Run" to execute
 * 4. Monitor "Tasks" tab for export progress
 * 5. Export all 10 annual batches to Google Drive
 ******************************************************************************/

// ============================================================================
// CONFIGURATION
// ============================================================================

// UPDATE THIS with your actual GEE asset ID
var FISHERIES_ASSET = 'users/YOUR_USERNAME/fisheries_25000';

// Study area boundaries
var STUDY_AREA = ee.Geometry.Rectangle({
  coords: [50, 0, 100, 30],  // [west, south, east, north]
  proj: 'EPSG:4326',
  geodesic: false
});

// Study period
var START_DATE = '2015-01-01';
var END_DATE = '2024-12-31';

// Satellite data sources
var SST_DATASET = 'NOAA/CDR/OISST/V2_1';
var CHLOROPHYLL_DATASET = 'NASA/OCEANDATA/MODIS-Aqua/L3SMI';

// Export configuration
var EXPORT_FOLDER = 'GEE_Satellite_Exports';
var BATCH_BY_YEAR = true;  // Export annual batches

// ============================================================================
// LOAD AND VALIDATE FISHERIES DATA
// ============================================================================

print('================================================================================');
print('SATELLITE ENVIRONMENTAL DATA EXTRACTION');
print('================================================================================');
print('');

print('Loading fisheries dataset...');
var fisheriesFC = ee.FeatureCollection(FISHERIES_ASSET);

// Get total count
var totalCount = fisheriesFC.size();
print('Total fisheries records:', totalCount);

// Check required fields
var first = fisheriesFC.first();
print('Sample fisheries record:', first);
print('');

// Filter to study period and area
var fisheriesFiltered = fisheriesFC
  .filterBounds(STUDY_AREA)
  .filter(ee.Filter.date(START_DATE, END_DATE));

var filteredCount = fisheriesFiltered.size();
print('Records within study area and period:', filteredCount);
print('');

// Visualize study area
Map.centerObject(STUDY_AREA, 5);
Map.addLayer(STUDY_AREA, {color: '0000FF'}, 'Study Area', false);
Map.addLayer(fisheriesFiltered.limit(1000), {color: 'FF0000'}, 'Fisheries Sample (1000)', false);

// ============================================================================
// LOAD SATELLITE DATA COLLECTIONS
// ============================================================================

print('Loading satellite data collections...');

// Sea Surface Temperature (NOAA OISST v2.1)
var sstCollection = ee.ImageCollection(SST_DATASET)
  .filterBounds(STUDY_AREA)
  .filterDate(START_DATE, END_DATE)
  .select('sst');

print('SST images available:', sstCollection.size());

// Chlorophyll-a (MODIS Aqua)
var chlorophyllCollection = ee.ImageCollection(CHLOROPHYLL_DATASET)
  .filterBounds(STUDY_AREA)
  .filterDate(START_DATE, END_DATE)
  .select('chlor_a');

print('Chlorophyll images available:', chlorophyllCollection.size());
print('');

// ============================================================================
// EXTRACTION FUNCTIONS
// ============================================================================

/**
 * Extract SST value at a point location for a specific date
 */
function extractSST(feature) {
  var date = ee.Date(feature.get('date'));
  var point = feature.geometry();
  
  // Get SST image for this date
  var sstImage = sstCollection
    .filterDate(date, date.advance(1, 'day'))
    .first();
  
  // Extract SST value
  var sstValue = ee.Algorithms.If(
    ee.Algorithms.IsEqual(sstImage, null),
    null,
    sstImage.reduceRegion({
      reducer: ee.Reducer.first(),
      geometry: point,
      scale: 1000,
      maxPixels: 1
    }).get('sst')
  );
  
  return feature.set({
    'sea_surface_temperature_c': sstValue,
    'sst_source': 'NOAA OISST v2.1',
    'sst_dataset_id': SST_DATASET
  });
}

/**
 * Extract Chlorophyll-a value at a point location for a specific date
 */
function extractChlorophyll(feature) {
  var date = ee.Date(feature.get('date'));
  var point = feature.geometry();
  
  // Get chlorophyll image for this date
  var chlImage = chlorophyllCollection
    .filterDate(date, date.advance(1, 'day'))
    .first();
  
  // Extract chlorophyll value
  var chlValue = ee.Algorithms.If(
    ee.Algorithms.IsEqual(chlImage, null),
    null,
    chlImage.reduceRegion({
      reducer: ee.Reducer.first(),
      geometry: point,
      scale: 1000,
      maxPixels: 1
    }).get('chlor_a')
  );
  
  return feature.set({
    'chlorophyll_a_mg_m3': chlValue,
    'chlorophyll_source': 'MODIS Aqua Ocean Color L3SMI',
    'chlorophyll_dataset_id': CHLOROPHYLL_DATASET
  });
}

/**
 * Extract both SST and Chlorophyll for a feature
 */
function extractEnvironmental(feature) {
  feature = extractSST(feature);
  feature = extractChlorophyll(feature);
  return feature;
}

/**
 * Add satellite record metadata
 */
function addSatelliteMetadata(feature, index) {
  var date = ee.Date(feature.get('date'));
  var year = date.get('year');
  var month = date.get('month');
  
  // Generate satellite_record_id
  var dateStr = date.format('YYYY-MM-dd');
  var satID = ee.String('SAT_').cat(dateStr).cat('_').cat(ee.Number(index).format('%05d'));
  
  return feature.set({
    'satellite_record_id': satID,
    'year': year,
    'month': month,
    'latitude': feature.geometry().coordinates().get(1),
    'longitude': feature.geometry().coordinates().get(0)
  });
}

// ============================================================================
// PROCESS ALL FISHERIES OBSERVATIONS
// ============================================================================

print('Extracting environmental data for all fisheries observations...');
print('This may take a few minutes...');
print('');

// Extract environmental data
var satelliteData = fisheriesFiltered.map(extractEnvironmental);

// Add sequential IDs and metadata
var satelliteList = satelliteData.toList(satelliteData.size());
satelliteData = ee.FeatureCollection(
  ee.List.sequence(0, satelliteData.size().subtract(1)).map(function(i) {
    var feature = ee.Feature(satelliteList.get(i));
    return addSatelliteMetadata(feature, i);
  })
);

print('Environmental extraction complete');
print('Total satellite records:', satelliteData.size());
print('');

// ============================================================================
// EXPORT CONFIGURATION
// ============================================================================

// Define output columns
var OUTPUT_COLUMNS = [
  'satellite_record_id',
  'fisheries_record_id',
  'date',
  'year',
  'month',
  'latitude',
  'longitude',
  'sea_surface_temperature_c',
  'chlorophyll_a_mg_m3',
  'sst_source',
  'chlorophyll_source',
  'sst_dataset_id',
  'chlorophyll_dataset_id'
];

// ============================================================================
// EXPORT ANNUAL BATCHES
// ============================================================================

if (BATCH_BY_YEAR) {
  print('Preparing annual export tasks...');
  print('');
  
  for (var year = 2015; year <= 2024; year++) {
    var yearStart = ee.Date.fromYMD(year, 1, 1);
    var yearEnd = yearStart.advance(1, 'year');
    
    var yearData = satelliteData.filter(
      ee.Filter.date(yearStart, yearEnd)
    );
    
    var yearCount = yearData.size();
    print('Year ' + year + ': ' + yearCount.getInfo() + ' records');
    
    // Export to Google Drive
    Export.table.toDrive({
      collection: yearData.select(OUTPUT_COLUMNS),
      description: 'satellite_' + year,
      folder: EXPORT_FOLDER,
      fileNamePrefix: 'satellite_' + year,
      fileFormat: 'CSV',
      selectors: OUTPUT_COLUMNS
    });
  }
  
  print('');
  print('================================================================================');
  print('EXPORT TASKS READY');
  print('================================================================================');
  print('');
  print('10 export tasks have been created (one per year: 2015-2024)');
  print('');
  print('Next steps:');
  print('1. Click the "Tasks" tab in the top-right corner');
  print('2. Click "Run" for each export task');
  print('3. Wait for all tasks to complete (10-30 minutes each)');
  print('4. Download CSVs from Google Drive folder: ' + EXPORT_FOLDER);
  print('5. Place files in: output/satellite_exports/');
  print('6. Run: python src/merge_satellite_exports.py');
  print('7. Run: python src/validate_satellite.py');
  print('');
  print('================================================================================');
  
} else {
  // Export all data as single file (not recommended for 25,000 records)
  print('Preparing single export task...');
  
  Export.table.toDrive({
    collection: satelliteData.select(OUTPUT_COLUMNS),
    description: 'satellite_all_years',
    folder: EXPORT_FOLDER,
    fileNamePrefix: 'satellite_all_years',
    fileFormat: 'CSV',
    selectors: OUTPUT_COLUMNS
  });
  
  print('Export task created. Check Tasks tab to run.');
}

// ============================================================================
// STATISTICS AND VALIDATION
// ============================================================================

print('');
print('Dataset Statistics:');
print('-------------------');

// Sample some records to check values
var sample = satelliteData.limit(10);
print('Sample satellite records:', sample);

print('');
print('================================================================================');
print('READY FOR EXPORT');
print('================================================================================');
