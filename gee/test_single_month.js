/*******************************************************************************
 * SINGLE MONTH TEST EXTRACTION
 * 
 * Purpose: Test satellite extraction methodology on one month before full processing
 * Test Period: January 2015 (first month of study)
 * Expected Records: ~208 fisheries observations
 * 
 * This script validates:
 * - Coordinate preservation
 * - Date preservation
 * - SST extraction
 * - Chlorophyll extraction
 * - Missing value handling
 * - Record ID matching
 ******************************************************************************/

// ============================================================================
// CONFIGURATION
// ============================================================================

// UPDATE THIS with your actual GEE asset ID
var FISHERIES_ASSET = 'users/YOUR_USERNAME/fisheries_25000';

// Test period - January 2015
var TEST_START = '2015-01-01';
var TEST_END = '2015-01-31';

// Study area
var STUDY_AREA = ee.Geometry.Rectangle([50, 0, 100, 30]);

// Satellite sources
var SST_DATASET = 'NOAA/CDR/OISST/V2_1';
var CHLOROPHYLL_DATASET = 'NASA/OCEANDATA/MODIS-Aqua/L3SMI';

// ============================================================================
// LOAD TEST DATA
// ============================================================================

print('================================================================================');
print('SINGLE MONTH TEST: January 2015');
print('================================================================================');
print('');

print('Loading fisheries dataset...');
var fisheriesFC = ee.FeatureCollection(FISHERIES_ASSET);

// Filter to test period
var testData = fisheriesFC
  .filterBounds(STUDY_AREA)
  .filter(ee.Filter.date(TEST_START, TEST_END));

var testCount = testData.size();
print('Test records (January 2015):', testCount);
print('Expected: ~208 records');
print('');

// Visualize
Map.centerObject(STUDY_AREA, 5);
Map.addLayer(STUDY_AREA, {color: 'blue'}, 'Study Area');
Map.addLayer(testData, {color: 'red'}, 'Test Fisheries (Jan 2015)');

// ============================================================================
// LOAD SATELLITE DATA
// ============================================================================

print('Loading satellite data for January 2015...');

// SST Collection
var sstCollection = ee.ImageCollection(SST_DATASET)
  .filterBounds(STUDY_AREA)
  .filterDate(TEST_START, TEST_END)
  .select('sst');

print('SST images available:', sstCollection.size());
print('Expected: ~31 images (daily)');

// Chlorophyll Collection
var chlorophyllCollection = ee.ImageCollection(CHLOROPHYLL_DATASET)
  .filterBounds(STUDY_AREA)
  .filterDate(TEST_START, TEST_END)
  .select('chlor_a');

print('Chlorophyll images available:', chlorophyllCollection.size());
print('Note: May be less than 31 due to clouds/gaps');
print('');

// Visualize one SST image
var sampleSST = sstCollection.first();
Map.addLayer(sampleSST, {
  min: 20,
  max: 32,
  palette: ['blue', 'cyan', 'yellow', 'red']
}, 'SST Sample (°C)', false);

// Visualize one Chlorophyll image
var sampleCHL = chlorophyllCollection.first();
Map.addLayer(sampleCHL, {
  min: 0.01,
  max: 10,
  palette: ['purple', 'blue', 'cyan', 'green', 'yellow', 'orange', 'red'],
  opacity: 0.7
}, 'Chlorophyll Sample (mg/m³)', false);

// ============================================================================
// EXTRACTION FUNCTIONS
// ============================================================================

function extractSST(feature) {
  var date = ee.Date(feature.get('date'));
  var point = feature.geometry();
  
  var sstImage = sstCollection
    .filterDate(date, date.advance(1, 'day'))
    .first();
  
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

function extractChlorophyll(feature) {
  var date = ee.Date(feature.get('date'));
  var point = feature.geometry();
  
  var chlImage = chlorophyllCollection
    .filterDate(date, date.advance(1, 'day'))
    .first();
  
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

function extractEnvironmental(feature) {
  feature = extractSST(feature);
  feature = extractChlorophyll(feature);
  return feature;
}

function addMetadata(feature, index) {
  var date = ee.Date(feature.get('date'));
  var satID = ee.String('SAT_TEST_').cat(ee.Number(index).format('%05d'));
  
  return feature.set({
    'satellite_record_id': satID,
    'year': date.get('year'),
    'month': date.get('month'),
    'latitude': feature.geometry().coordinates().get(1),
    'longitude': feature.geometry().coordinates().get(0)
  });
}

// ============================================================================
// PROCESS TEST DATA
// ============================================================================

print('Extracting environmental data...');

var satelliteTest = testData.map(extractEnvironmental);

// Add metadata
var satelliteList = satelliteTest.toList(satelliteTest.size());
satelliteTest = ee.FeatureCollection(
  ee.List.sequence(0, satelliteTest.size().subtract(1)).map(function(i) {
    var feature = ee.Feature(satelliteList.get(i));
    return addMetadata(feature, i);
  })
);

print('Extraction complete!');
print('');

// ============================================================================
// VALIDATION AND STATISTICS
// ============================================================================

print('================================================================================');
print('TEST RESULTS');
print('================================================================================');
print('');

// Sample results
print('Sample extracted records:');
var sample = satelliteTest.limit(5);
print(sample);
print('');

// Get first feature to check structure
var firstFeature = ee.Feature(satelliteTest.first());
print('First record structure:', firstFeature);
print('');

// Statistics
print('Dataset Statistics:');
print('-------------------');
print('Total records:', satelliteTest.size());

// Note: Computing statistics in GEE can be slow
// For detailed statistics, export and analyze in Python

print('');
print('================================================================================');
print('VALIDATION CHECKS');
print('================================================================================');
print('');

// Check for required fields
var requiredFields = [
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
  'chlorophyll_source'
];

print('Required fields present:');
var firstProps = firstFeature.propertyNames();
requiredFields.forEach(function(field) {
  var hasField = firstProps.contains(field);
  print('  ' + field + ': ' + (hasField.getInfo() ? '[OK]' : '[MISSING]'));
});

print('');

// ============================================================================
// EXPORT TEST DATA
// ============================================================================

print('================================================================================');
print('EXPORT TEST DATA');
print('================================================================================');
print('');

var outputColumns = [
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

Export.table.toDrive({
  collection: satelliteTest.select(outputColumns),
  description: 'satellite_test_jan2015',
  folder: 'GEE_Satellite_Exports',
  fileNamePrefix: 'satellite_test_jan2015',
  fileFormat: 'CSV',
  selectors: outputColumns
});

print('Test export task created');
print('');
print('Next steps:');
print('1. Click "Tasks" tab');
print('2. Click "Run" on the export task');
print('3. Download CSV from Google Drive');
print('4. Inspect values manually or with Python');
print('5. Verify:');
print('   - Coordinates match fisheries data');
print('   - Dates preserved correctly');
print('   - SST values are plausible (20-32°C)');
print('   - Chlorophyll values are plausible (0.01-50 mg/m³)');
print('   - Missing values are documented (null)');
print('');
print('If test looks good, proceed with full extraction!');
print('Use: satellite_generator.js');
print('');
print('================================================================================');

// ============================================================================
// ADDITIONAL TESTS (Optional)
// ============================================================================

// Test early and late period months
print('');
print('ADDITIONAL TEST SUGGESTIONS:');
print('----------------------------');
print('Test these months to verify source coverage:');
print('- January 2015 (first month) [current test]');
print('- December 2024 (last month)');
print('- June 2019 (mid-period, monsoon season)');
print('');
print('Update TEST_START and TEST_END dates above to test other months');
print('');
