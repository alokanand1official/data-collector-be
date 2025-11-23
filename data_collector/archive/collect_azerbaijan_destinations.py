#!/usr/bin/env python3
"""
Collect destination data for Azerbaijan cities only
Saves to byd_escapism schema
"""

import logging
from config.cities_config import CITIES
from sources.wikidata import WikidataCollector
from utils.database import Database
from utils.llm import LocalLLM

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AzerbaijanDestinationCollector:
    def __init__(self):
        self.wikidata = WikidataCollector()
        self.db = Database(schema='byd_escapism')
        self.llm = LocalLLM()
        
    def collect_all_azerbaijan(self):
        """Collect all Azerbaijan destinations"""
        azerbaijan_cities = [
            (key, config) for key, config in CITIES.items() 
            if config['country'] == 'Azerbaijan'
        ]
        
        logger.info(f"Found {len(azerbaijan_cities)} Azerbaijan destinations to collect")
        
        for i, (key, config) in enumerate(azerbaijan_cities, 1):
            city_name = config['name']
            logger.info(f"\n{'='*60}")
            logger.info(f"[{i}/{len(azerbaijan_cities)}] Processing: {city_name}")
            logger.info(f"{'='*60}")
            
            try:
                self.collect_city(city_name, config)
            except Exception as e:
                logger.error(f"Failed to collect {city_name}: {e}")
                import traceback
                traceback.print_exc()
                
    def collect_city(self, city_name: str, config: dict):
        """Collect and save a single city"""
        
        # 1. Try Wikidata first
        logger.info(f"Fetching Wikidata for {city_name}...")
        data = self.wikidata.get_city_details(city_name)
        
        # 2. Fallback to config-based data
        if not data:
            logger.warning(f"Wikidata failed for {city_name}. Using fallback.")
            bbox = config.get('bbox')
            if bbox:
                lat = (bbox['north'] + bbox['south']) / 2
                lng = (bbox['east'] + bbox['west']) / 2
                data = {
                    "name": city_name,
                    "description": f"A beautiful destination in {config['country']}.",
                    "image": None,
                    "coordinates": {"lat": lat, "lng": lng},
                    "country": config['country']
                }
            else:
                logger.error(f"No bbox for {city_name}, skipping")
                return
        
        # 3. Enrich with LLM
        logger.info(f"Enriching {city_name} with AI...")
        enrichment = self.llm.generate_destination_content(
            city_name, 
            data.get('country', 'Azerbaijan')
        )
        
        # 4. Build destination object
        destination = {
            "name": data['name'],
            "description": enrichment.get('description', data['description']),
            "short_description": enrichment.get('short_description'),
            "image_url": data.get('image'),
            "images": [data['image']] if data.get('image') else [],
            "coordinates": data['coordinates'],
            "country": data.get('country', 'Azerbaijan'),
            
            # LLM enrichment
            "vibe_tags": enrichment.get('vibe_tags', []),
            "category_tags": enrichment.get('category_tags', []),
            "budget_range": enrichment.get('budget_range', 'moderate').lower(),
            "price_per_day_min": enrichment.get('price_per_day_min', 40),
            "price_per_day_max": enrichment.get('price_per_day_max', 120),
            "average_trip_duration": enrichment.get('average_trip_duration', 4),
            "best_time_to_visit": enrichment.get('best_time_to_visit'),
            "climate_type": enrichment.get('climate_type'),
            "language": enrichment.get('language', 'Azerbaijani'),
            "currency": enrichment.get('currency', 'AZN'),
            "time_zone": enrichment.get('time_zone', 'UTC+4'),
            
            "is_featured": False,
            "data_quality_score": 80 if data.get('image') else 60
        }
        
        # 5. Save to database
        self.save_destination(destination)
        
    def save_destination(self, data: dict):
        """Save or update destination in database"""
        try:
            # Check if exists
            existing = self.db.client.table('destinations').select('id').eq('name', data['name']).execute()
            
            if existing.data:
                logger.info(f"Updating existing: {data['name']}")
                self.db.client.table('destinations').update(data).eq('name', data['name']).execute()
            else:
                logger.info(f"Creating new: {data['name']}")
                self.db.client.table('destinations').insert(data).execute()
                
            logger.info(f"✅ Saved {data['name']} to byd_escapism.destinations")
            
        except Exception as e:
            logger.error(f"Failed to save {data['name']}: {e}")
            raise

if __name__ == "__main__":
    collector = AzerbaijanDestinationCollector()
    collector.collect_all_azerbaijan()
    logger.info("\n🎉 Azerbaijan destination collection complete!")
