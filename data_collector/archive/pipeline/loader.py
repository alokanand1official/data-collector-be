import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import db

logger = logging.getLogger(__name__)

class Loader:
    """
    Loads processed POI data into Supabase.
    """
    
    def __init__(self, processed_data_dir: str = "processed_data"):
        self.processed_data_dir = Path(processed_data_dir)

    def load_city(self, city_name: str):
        """Loads processed data for a city into the database."""
        logger.info(f"Loading data for {city_name}...")
        
        input_file = self.processed_data_dir / f"{city_name.lower().replace(' ', '_')}_pois.json"
        
        if not input_file.exists():
            logger.error(f"No processed data found for {city_name}")
            return

        with open(input_file, 'r', encoding='utf-8') as f:
            pois = json.load(f)
            
        if not pois:
            logger.warning("No POIs to load.")
            return

        logger.info(f"Found {len(pois)} POIs to load.")
        
        # Use the existing db utility which handles batching
        # But we might need to map fields if the schema is strict
        
        # Check if we need to adapt to 'trip_pois' or 'pois'
        # For now, we assume the db utility handles the 'pois' table or we use 'trip_pois'
        # The previous error showed 'pois' table missing, so we might need to use 'trip_pois'
        # But 'trip_pois' requires 'trip_id'.
        # We really should have a 'destinations' or 'places' table for global data.
        # If the user wants to collect data for the APP, it should go into a 'pois' table in 'byd_escapism' schema.
        
        # Clean POIs to match schema
        cleaned_pois = []
        for poi in pois:
            clean_poi = poi.copy()
            
            # Move fields to metadata if they exist
            if 'city_name' in clean_poi:
                clean_poi['metadata']['city_name'] = clean_poi['city_name']
                del clean_poi['city_name']
                
            if 'country_code' in clean_poi:
                clean_poi['metadata']['country_code'] = clean_poi['country_code']
                del clean_poi['country_code']
            
            if 'description' in clean_poi:
                clean_poi['metadata']['description'] = clean_poi['description']
                del clean_poi['description']
                
            if 'persona_scores' in clean_poi:
                clean_poi['metadata']['persona_scores'] = clean_poi['persona_scores']
                del clean_poi['persona_scores']
                
            if 'name_local' in clean_poi:
                clean_poi['metadata']['name_local'] = clean_poi['name_local']
                del clean_poi['name_local']

            cleaned_pois.append(clean_poi)

        # Let's try to use the db.save_pois method which we saw earlier
        try:
            count = db.save_pois(cleaned_pois)
            logger.info(f"✅ Successfully loaded {count} POIs for {city_name}")
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            # Fallback: Try to insert into trip_pois if pois fails? 
            # No, that's for user trips. We need the global catalog.
            # If save_pois fails, it's likely a schema issue that needs fixing in DB.
