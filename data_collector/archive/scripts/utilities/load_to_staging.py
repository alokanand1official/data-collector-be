#!/usr/bin/env python3
"""
Enhanced POI Loader - Loads enriched POIs to byd_escapism.pois table
Maps our POI structure to the comprehensive byd_escapism schema
"""

import json
import logging
from pathlib import Path
from typing import List, Dict
import argparse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.database import Database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedPOILoader:
    """Loads enriched POIs to byd_escapism.pois with proper schema mapping"""
    
    def __init__(self):
        self.db = Database(schema='byd_escapism')
    
    def map_poi_to_schema(self, poi: Dict, city_name: str) -> Dict:
        """Map our POI structure to byd_escapism.pois schema"""
        
        # Extract coordinates
        coords = poi.get('coordinates', {})
        
        # Map to schema
        mapped = {
            # Basic Info
            'name': poi.get('name'),
            'name_local': poi.get('name_local'),
            'poi_type': poi.get('poi_type'),
            'poi_subtypes': [],
            'coordinates': coords,
            
            # Location
            'country_code': None,  # Set to NULL to avoid FK constraint
            
            # Descriptions (map our single description to general)
            'description_general': poi.get('description'),
            
            # Persona Scores (already in correct format)
            'persona_scores': poi.get('persona_scores', {}),
            
            # Tags
            'vibe_tags': poi.get('vibe_tags', []),
            'category_tags': poi.get('category_tags', []),
            
            # Quality & Metadata
            'data_quality_score': poi.get('priority_score', 50),
            'completeness_score': 100 if poi.get('description') and poi.get('persona_scores') else 50,
            'verification_status': 'unverified',
            'data_sources': ['osm', 'ollama'],
            
            # Source IDs
            'osm_id': poi.get('osm_id'),
            
            # Defaults for required fields
            'accessibility': {},
            'booking_required': False,
            'popularity_score': poi.get('priority_score', 50),
            'trending_score': 0,
            'rating': 0.0,
            'review_count': 0,
            'is_featured': poi.get('priority_tier') == 'essential',
            'is_hidden_gem': False,
            'featured_in': [],
            'nearby_pois': [],
            'typically_combined_with': [],
            'alternative_to': [],
            'images': [],
            'videos': [],
            
            # Store original metadata
            'metadata': {
                'city_name': city_name,
                'priority_tier': poi.get('priority_tier'),
                'enrichment_priority': poi.get('enrichment_priority'),
                'original_poi_type': poi.get('poi_type'),
            }
        }
        
        return mapped
    
    def load_pois(self, pois: List[Dict], city_name: str) -> int:
        """Load POIs to database"""
        logger.info(f"Loading {len(pois)} POIs for {city_name} to byd_escapism.pois...")
        
        # Map POIs to schema
        mapped_pois = [self.map_poi_to_schema(poi, city_name) for poi in pois]
        
        # Insert in batches
        batch_size = 50
        inserted_count = 0
        
        for i in range(0, len(mapped_pois), batch_size):
            batch = mapped_pois[i:i+batch_size]
            
            try:
                result = self.db.client.table('pois').insert(batch).execute()
                inserted_count += len(batch)
                logger.info(f"  Inserted batch {i//batch_size + 1}: {len(batch)} POIs")
            except Exception as e:
                logger.error(f"  Error inserting batch {i//batch_size + 1}: {e}")
                
                # Try one by one for this batch
                for poi in batch:
                    try:
                        self.db.client.table('pois').insert(poi).execute()
                        inserted_count += 1
                    except Exception as e2:
                        logger.error(f"    Failed to insert {poi.get('name')}: {e2}")
        
        return inserted_count
    
    def load_from_file(self, input_file: str, city_name: str):
        """Load POIs from JSON file"""
        logger.info(f"Loading POIs from {input_file}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            pois = json.load(f)
        
        logger.info(f"Found {len(pois)} POIs in file")
        
        # Load to database
        inserted = self.load_pois(pois, city_name)
        
        logger.info(f"\n✅ Successfully loaded {inserted}/{len(pois)} POIs to byd_escapism.pois")
        
        return inserted

def main():
    parser = argparse.ArgumentParser(description='Load enriched POIs to byd_escapism schema')
    parser.add_argument('--city', required=True, help='City name (e.g., Baku)')
    parser.add_argument('--input', help='Input file (default: processed_data/{city}_pois_enriched_only.json)')
    
    args = parser.parse_args()
    
    # Determine input file
    city_lower = args.city.lower().replace(' ', '_')
    input_file = args.input or f'processed_data/{city_lower}_pois_enriched_only.json'
    
    # Check if file exists
    if not Path(input_file).exists():
        logger.error(f"Input file not found: {input_file}")
        logger.info("Please run filter_enriched.py first to create enriched-only file")
        exit(1)
    
    # Load POIs
    loader = EnhancedPOILoader()
    loader.load_from_file(input_file, args.city)

if __name__ == "__main__":
    main()
