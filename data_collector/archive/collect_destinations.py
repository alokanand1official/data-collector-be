import logging
import argparse
import json
from typing import List, Dict
from sources.wikidata import WikidataCollector
from utils.database import Database
from utils.llm import LocalLLM
from main import CITIES

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DestinationCollector:
    def __init__(self):
        self.wikidata = WikidataCollector()
        self.db = Database(schema='byd_escapism')
        self.llm = LocalLLM()

    def collect_all(self):
        """Collect data for all configured cities."""
        for key, config in CITIES.items():
            self.collect_city(config['name'])

    def collect_city(self, city_name: str):
        logger.info(f"Collecting destination data for {city_name}...")
        
        # 1. Fetch from Wikidata
        data = self.wikidata.get_city_details(city_name)
        
        # Fallback if Wikidata fails
        if not data:
            logger.warning(f"Failed to fetch Wikidata for {city_name}. Using fallback data.")
            # Find config
            city_config = None
            for key, conf in CITIES.items():
                if conf['name'].lower() == city_name.lower():
                    city_config = conf
                    break
            
            if city_config and city_config.get('bbox'):
                bbox = city_config['bbox']
                # Calculate center
                lat = (bbox['north'] + bbox['south']) / 2
                lng = (bbox['east'] + bbox['west']) / 2
                
                data = {
                    "name": city_config['name'],
                    "description": f"A beautiful destination in {city_config['country']}.",
                    "image": None,
                    "coordinates": {"lat": lat, "lng": lng},
                    "country": city_config['country']
                }
            else:
                logger.error(f"No fallback data available for {city_name}")
                return

        # 2. Enrich with LLM (Description & Vibes)
        logger.info(f"Enriching {city_name} with AI...")
        enrichment = self.llm.generate_destination_content(city_name, data.get('country', 'Thailand'))
        
        # Merge data
        destination = {
            "name": data['name'],
            "description": enrichment.get('description', data['description']),
            "short_description": enrichment.get('short_description'),
            "image_url": data['image'],
            "images": [data['image']] if data.get('image') else [],
            "coordinates": data['coordinates'],
            "country": data.get('country', 'Unknown'),
            
            # Rich fields from LLM
            "vibe_tags": enrichment.get('vibe_tags', []),
            "category_tags": enrichment.get('category_tags', []),
            "budget_range": enrichment.get('budget_range', 'moderate').lower(),
            "price_per_day_min": enrichment.get('price_per_day_min', 50),
            "price_per_day_max": enrichment.get('price_per_day_max', 150),
            "average_trip_duration": enrichment.get('average_trip_duration', 5),
            "best_time_to_visit": enrichment.get('best_time_to_visit'),
            "climate_type": enrichment.get('climate_type'),
            "language": enrichment.get('language'),
            "currency": enrichment.get('currency'),
            "time_zone": enrichment.get('time_zone'),
            
            "is_featured": False,
            "data_quality_score": 80 if data.get('image') else 50
        }
        
        # 3. Save to DB
        self.save_destination(destination)

    def save_destination(self, data: Dict):
        try:
            # Check if exists
            existing = self.db.client.table('destinations').select('id').eq('name', data['name']).execute()
            
            if existing.data:
                logger.info(f"Updating existing destination: {data['name']}")
                self.db.client.table('destinations').update(data).eq('name', data['name']).execute()
            else:
                logger.info(f"Creating new destination: {data['name']}")
                self.db.client.table('destinations').insert(data).execute()
                
            logger.info(f"✅ Saved {data['name']}")
        except Exception as e:
            logger.error(f"Failed to save {data['name']}: {e}")

if __name__ == "__main__":
    collector = DestinationCollector()
    collector.collect_all()
