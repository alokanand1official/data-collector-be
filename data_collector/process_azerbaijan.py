"""
Batch process all Azerbaijan cities through the complete ETL pipeline
"""

from orchestrator import Orchestrator
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("AzerbaijanBatchProcessor")

# Azerbaijan cities to process
AZERBAIJAN_CITIES = [
    'Baku',
    'Gabala',
    'Sheki',
    'Ganja',
    'Quba',
    'Lahij',
    'Gobustan'
]

def run_azerbaijan_pipeline():
    """Run complete pipeline for all Azerbaijan cities"""
    
    start_time = datetime.now()
    
    print("="*80)
    print("🇦🇿 AZERBAIJAN DATA COLLECTION - COMPLETE PIPELINE")
    print("="*80)
    print(f"\nCities to process: {len(AZERBAIJAN_CITIES)}")
    for i, city in enumerate(AZERBAIJAN_CITIES, 1):
        print(f"  {i}. {city}")
    print("\n" + "="*80)
    
    orch = Orchestrator()
    
    results = {
        'success': [],
        'failed': [],
        'stats': {}
    }
    
    for i, city in enumerate(AZERBAIJAN_CITIES, 1):
        print(f"\n{'='*80}")
        print(f"🏙️  Processing {city} ({i}/{len(AZERBAIJAN_CITIES)})")
        print(f"{'='*80}\n")
        
        city_start = datetime.now()
        
        try:
            # Step 1: Bronze Layer (OSM Extraction)
            print(f"\n📥 Step 1/4: Bronze Layer - Extracting OSM data for {city}")
            orch.run_bronze_layer(city)
            
            # Step 2: Silver Layer (Translation + Validation)
            print(f"\n🔄 Step 2/4: Silver Layer - Translating and validating data for {city}")
            orch.run_silver_layer(city)
            
            # Step 3: Gold Layer (AI Enrichment)
            print(f"\n✨ Step 3/4: Gold Layer - AI enrichment with Gemma 3 for {city}")
            orch.run_gold_layer(city)
            
            # Step 4: Load Layer (Database)
            print(f"\n📤 Step 4/4: Load Layer - Loading to Supabase for {city}")
            orch.run_load_layer(city)
            
            city_duration = (datetime.now() - city_start).total_seconds()
            
            results['success'].append(city)
            results['stats'][city] = {
                'duration': city_duration,
                'status': 'success'
            }
            
            print(f"\n✅ {city} completed in {city_duration:.1f} seconds")
            
        except Exception as e:
            logger.error(f"❌ Failed to process {city}: {e}")
            results['failed'].append(city)
            results['stats'][city] = {
                'duration': (datetime.now() - city_start).total_seconds(),
                'status': 'failed',
                'error': str(e)
            }
            print(f"\n❌ {city} failed: {e}")
            continue
    
    # Final summary
    total_duration = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "="*80)
    print("📊 AZERBAIJAN PIPELINE - FINAL SUMMARY")
    print("="*80)
    print(f"\nTotal Time: {total_duration/60:.1f} minutes")
    print(f"Successful: {len(results['success'])}/{len(AZERBAIJAN_CITIES)}")
    print(f"Failed: {len(results['failed'])}/{len(AZERBAIJAN_CITIES)}")
    
    if results['success']:
        print(f"\n✅ Successfully processed:")
        for city in results['success']:
            duration = results['stats'][city]['duration']
            print(f"   - {city} ({duration:.1f}s)")
    
    if results['failed']:
        print(f"\n❌ Failed:")
        for city in results['failed']:
            print(f"   - {city}")
    
    print("\n" + "="*80)
    print("🎉 Azerbaijan data collection complete!")
    print("="*80)
    
    return results

if __name__ == "__main__":
    results = run_azerbaijan_pipeline()
