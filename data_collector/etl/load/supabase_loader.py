import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add parent dir to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.database import Database
from config.cities_config import CITIES

logger = logging.getLogger("SupabaseLoader")

class SupabaseLoader:
    """
    Loads Gold data into Supabase (Production Database).
    """
    
    def __init__(self, gold_dir: Path):
        self.gold_dir = gold_dir
        # Initialize with new schema 'byd_esp'
        self.db = Database(schema='byd_esp')
        self.client = self.db.client
        self.db = Database(schema='byd_esp')
        
    def load_gold_layer(self, city_name: str):
        """
        Loads enriched data (Destinations & Activities) into 'byd_esp' schema.
        """
        city_key = city_name.lower().replace(" ", "_")
        city_gold_dir = self.gold_dir / city_key
        
        if not city_gold_dir.exists():
            logger.warning(f"Gold layer not found for {city_name} at {city_gold_dir}")
            return

        # 1. Load Destination Details
        dest_file = city_gold_dir / "destination_details.json"
        destination_id = None
        
        if dest_file.exists():
            with open(dest_file, 'r') as f:
                dest_data = json.load(f)
                
            # Upsert Destination Core
            core_data = {
                "slug": dest_data['slug'],
                "name": dest_data['name'],
                "country_code": dest_data.get('country_code', 'XX'),
                "coordinates": dest_data.get('coordinates', {}),
                "timezone": dest_data.get('timezone'),
                "is_active": True
            }
            
            try:
                # Upsert into byd_esp.destinations
                self.db.client.table('destinations').upsert(core_data, on_conflict='slug').execute()
                
                # Fetch ID separately to be safe
                res = self.db.client.table('destinations').select('id').eq('slug', core_data['slug']).single().execute()
                
                if res.data:
                    destination_id = res.data['id']
                    logger.info(f"✅ Loaded Destination: {dest_data['name']} (ID: {destination_id})")
                    
                    # Upsert Destination Details
                    details_data = {
                        "destination_id": destination_id,
                        "summary": dest_data.get('summary'),
                        "why_go": dest_data.get('why_go'),
                        "tags": dest_data.get('tags'),
                        "best_months": dest_data.get('best_months'),
                        "monthly_insights": dest_data.get('monthly_insights'),
                        "personality_fit": dest_data.get('personality_fit'),
                        "budget": dest_data.get('budget'),
                        "safety": dest_data.get('safety'),
                        "connectivity": dest_data.get('connectivity')
                    }
                    self.db.client.table('destination_details').upsert(details_data, on_conflict='destination_id').execute()
                    logger.info("✅ Loaded Destination Details")
            except Exception as e:
                logger.error(f"Failed to load destination: {e}")
                return

        if not destination_id:
            logger.error("Cannot load activities without destination ID")
            return

        # 2. Load Activities
        pois_file = city_gold_dir / "pois.json"
        if pois_file.exists():
            try:
                with open(pois_file, 'r') as f:
                    pois = json.load(f)
                
                activities = []
                for poi in pois:
                    # Extract contact info
                    contact_info = poi.get('contact', {})
                    
                    activity = {
                        "destination_id": destination_id,
                        "name": poi['name'],
                        "category": poi.get('category', 'unknown'),
                        "coordinates": poi['coordinates'],
                        "description": poi.get('description'),
                        "tags": [k for k,v in poi.get('tags', {}).items()],
                        "personas": poi.get('personas', {}),
                        "is_popular": poi.get('is_popular', False),
                        "duration_min": poi.get('duration_min', 60),
                        "price_level": poi.get('price_level', 2),
                        # New fields from Phase 1 & 2
                        "opening_hours": poi.get('opening_hours'),
                        "address": poi.get('address'),
                        "phone": contact_info.get('phone') if contact_info else None,
                        "email": contact_info.get('email') if contact_info else None,
                        "website": contact_info.get('website') if contact_info else None,
                        "best_time": poi.get('best_time'),
                        "best_time_reason": poi.get('best_time_reason'),
                        "tips": poi.get('tips', []),
                        "what_to_expect": poi.get('what_to_expect'),
                        "wikidata": poi.get('wikidata'),
                        "wikimedia_commons": poi.get('wikimedia_commons'),
                        "wikipedia": poi.get('wikipedia')
                    }
                    activities.append(activity)
                
                # Batch Insert
                batch_size = 50
                for i in range(0, len(activities), batch_size):
                    batch = activities[i:i+batch_size]
                    try:
                        self.db.client.table('activities').insert(batch).execute()
                        logger.info(f"Loaded batch {i//batch_size + 1} ({len(batch)} activities)")
                    except Exception as e:
                        logger.error(f"Error loading batch {i}: {e}")
                        
                logger.info(f"✅ Successfully loaded {len(activities)} activities for {city_name}")
            except Exception as e:
                logger.error(f"Error managing activities for {city_name}: {e}")
                return
