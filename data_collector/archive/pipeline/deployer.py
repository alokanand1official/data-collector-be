import logging
import json
from pathlib import Path
from typing import Dict, List
from utils.database import Database
from config.cities_config import CITIES

logger = logging.getLogger(__name__)

class Deployer:
    """
    Deploys data from Staging (byd_escapism) to Production (public).
    """
    
    def __init__(self):
        # Source: Staging Schema
        self.staging_db = Database(schema="byd_escapism")
        # Target: Production Schema
        self.prod_db = Database(schema="public")
        
        self.processed_data_dir = Path("processed_data")

    def get_country_for_city(self, city_name: str) -> str:
        """Get country name from config."""
        # Try exact match
        for key, data in CITIES.items():
            if data['name'].lower() == city_name.lower():
                return data['country']
        return "Unknown"

    def deploy_all(self):
        """Deploy everything."""
        dest_map = self.deploy_destinations()
        
        for city_name, dest_id in dest_map.items():
            self.deploy_activities(city_name, dest_id)

    def deploy_destinations(self) -> Dict[str, str]:
        """
        Sync destinations from Staging to Production.
        Returns a map of {City Name: Production ID}
        """
        logger.info("🚀 Deploying Destinations...")
        
        # 1. Fetch from Staging
        staging_dests = self.staging_db.client.table('destinations').select('*').execute().data
        print(f"DEBUG: Fetched {len(staging_dests)} destinations from Staging")
        if staging_dests:
            print(f"DEBUG: Names: {[d['name'] for d in staging_dests]}")
        
        if not staging_dests:
            logger.warning("No destinations found in Staging!")
            return {}
            
        dest_map = {}
        
        # 2. Upsert to Production
        for dest in staging_dests:
            # Prepare payload (remove ID to let Prod generate it, OR keep it if we want sync)
            # Better to let Prod generate ID, but then we need to find it back.
            # Actually, we can lookup by name.
            
            country = self.get_country_for_city(dest['name'])
            
            payload = {
                "name": dest['name'],
                "description": dest['description'],
                "short_description": dest.get('short_description') or (dest['description'][:200] if dest.get('description') else None),
                "image_url": dest['image_url'],
                "images": dest.get('images', []),
                "coordinates": dest['coordinates'],
                "country": country,
                "continent": "Asia", # Hardcoded for now
                "best_time_to_visit": dest.get('best_time_to_visit'),
                "average_trip_duration": dest.get('average_trip_duration', 5),
                "budget_range": dest.get('budget_range', 'moderate'),
                "price_per_day_min": dest.get('price_per_day_min', 50),
                "price_per_day_max": dest.get('price_per_day_max', 150),
                "vibe_tags": dest.get('vibe_tags', []),
                "category_tags": dest.get('category_tags', []),
                "is_featured": dest.get('is_featured', False),
                "climate_type": dest.get('climate_type'),
                "language": dest.get('language'),
                "currency": dest.get('currency'),
                "time_zone": dest.get('time_zone'),
                "popularity_score": dest.get('data_quality_score', 0)
            }
            
            try:
                # Check if exists in Prod
                existing = self.prod_db.client.table('destinations').select('id').eq('name', dest['name']).execute()
                
                if existing.data:
                    prod_id = existing.data[0]['id']
                    logger.info(f"Updating {dest['name']} (ID: {prod_id})")
                    self.prod_db.client.table('destinations').update(payload).eq('id', prod_id).execute()
                else:
                    logger.info(f"Creating {dest['name']}")
                    res_insert = self.prod_db.client.table('destinations').insert(payload).execute()
                    prod_id = res_insert.data[0]['id']
                    
                dest_map[dest['name']] = prod_id
                
            except Exception as e:
                logger.error(f"Failed to deploy {dest['name']}: {e}")
                
        return dest_map

    def deploy_activities(self, city_name: str, destination_id: str):
        """Deploy activities for a city."""
        logger.info(f"🚀 Deploying Activities for {city_name}...")
        
        # 1. Read Processed Data (Source of Truth for POIs)
        # Prefer prioritized/enriched file if it exists
        prioritized_file = self.processed_data_dir / f"{city_name.lower().replace(' ', '_')}_pois_prioritized.json"
        raw_file = self.processed_data_dir / f"{city_name.lower().replace(' ', '_')}_pois.json"
        
        if prioritized_file.exists():
            input_file = prioritized_file
            logger.info(f"Reading from prioritized file: {input_file}")
        elif raw_file.exists():
            input_file = raw_file
            logger.info(f"Reading from raw file: {input_file}")
        else:
            logger.warning(f"No POI data found for {city_name}")
            return
            
        logger.info(f"Reading from {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            pois = json.load(f)
            
        logger.info(f"Loaded {len(pois)} POIs from file")
            
        activities_to_insert = []
        
        for poi in pois:
            # Quality Gate
            if not poi.get('description'):
                continue
                
            # Transform
            lat = poi['coordinates']['lat']
            lng = poi['coordinates']['lng']
            
            activity = {
                "name": poi['name'],
                "category": poi['poi_type'],
                "destination_id": destination_id,
                "description": poi['description'],
                "image_url": None, # Future: Add images
                "rating": 4.5, # Placeholder
                "is_popular": False,
                "location": f"POINT({lng} {lat})",
                "price_range": "medium"
            }
            activities_to_insert.append(activity)
            
        logger.info(f"Found {len(activities_to_insert)} valid activities (with description) for {city_name} (ID: {destination_id})")

        # 2. Insert into Production
        if activities_to_insert:
            batch_size = 100
            logger.info(f"Pushing {len(activities_to_insert)} activities to Production...")
            
            for i in range(0, len(activities_to_insert), batch_size):
                batch = activities_to_insert[i:i+batch_size]
                try:
                    self.prod_db.client.table('activities').insert(batch).execute()
                    logger.info(f"Deployed batch {i}-{i+len(batch)}")
                except Exception as e:
                    logger.error(f"Failed to deploy batch: {e}")
        
        logger.info(f"✅ Deployed {city_name}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    deployer = Deployer()
    deployer.deploy_all()
