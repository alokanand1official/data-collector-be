import requests
import json
import time
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)

class Harvester:
    """
    Robust Data Harvester for OpenStreetMap.
    Splits areas into tiles and downloads them one by one, saving to disk.
    """
    
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    
    def __init__(self, raw_data_dir: str = "raw_data"):
        self.raw_data_dir = Path(raw_data_dir)
        self.raw_data_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "BeyondEscapismDataCollector/1.0 (contact@beyondescapism.com)"
        })

    def generate_tiles(self, bbox: Dict[str, float], step: float = 0.05) -> List[Dict[str, float]]:
        """
        Splits a large bounding box into smaller tiles.
        bbox: {north, south, east, west}
        step: size of tile in degrees (default 0.05 deg ~ 5.5km)
        """
        tiles = []
        lat = bbox['south']
        while lat < bbox['north']:
            lon = bbox['west']
            while lon < bbox['east']:
                # Calculate tile boundaries
                north = min(lat + step, bbox['north'])
                east = min(lon + step, bbox['east'])
                
                tiles.append({
                    'south': lat,
                    'west': lon,
                    'north': north,
                    'east': east
                })
                lon += step
            lat += step
        return tiles

    def build_query(self, bbox: Dict[str, float], poi_types: List[str]) -> str:
        """Builds an Overpass QL query for a specific bbox."""
        bbox_str = f"{bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']}"
        
        # Common tourism/amenity tags
        # We can expand this list or make it configurable
        query_parts = []
        
        # Add specific filters based on config if needed, for now generic high-value tags
        tags = [
            'node["tourism"]', 'way["tourism"]',
            'node["amenity"="restaurant"]', 'way["amenity"="restaurant"]',
            'node["amenity"="cafe"]', 'way["amenity"="cafe"]',
            'node["amenity"="marketplace"]', 'way["amenity"="marketplace"]',
            'node["natural"="beach"]', 'way["natural"="beach"]',
            'node["leisure"="park"]', 'way["leisure"="park"]',
            'node["historic"]', 'way["historic"]',
            'node["religion"="buddhist"]', 'way["religion"="buddhist"]'
        ]
        
        for tag in tags:
            query_parts.append(f'{tag}({bbox_str});')
            
        query = f"""
        [out:json][timeout:25];
        (
          {''.join(query_parts)}
        );
        out body;
        >;
        out skel qt;
        """
        return query

    def fetch_tile(self, tile: Dict[str, float], tile_id: str, city_dir: Path) -> bool:
        """
        Downloads a single tile.
        Returns True if successful, False if failed (after retries).
        """
        file_path = city_dir / f"{tile_id}.json"
        
        if file_path.exists():
            logger.info(f"Tile {tile_id} already exists. Skipping.")
            return True

        query = self.build_query(tile, [])
        
        retries = 0
        max_retries = 5
        backoff = 5 # Start with 5 seconds
        
        while retries < max_retries:
            try:
                response = self.session.post(self.OVERPASS_URL, data={'data': query}, timeout=30)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # Check if we got valid data structure
                        if 'elements' in data:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(data, f)
                            logger.info(f"✅ Downloaded tile {tile_id} ({len(data['elements'])} elements)")
                            time.sleep(2) # Be nice to the API
                            return True
                        else:
                            logger.warning(f"Invalid JSON response for tile {tile_id}")
                    except json.JSONDecodeError:
                        logger.warning(f"JSON Decode Error for tile {tile_id}")
                
                elif response.status_code == 429:
                    logger.warning(f"⚠️ Rate limited (429). Sleeping {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2 # Exponential backoff
                    retries += 1
                    continue
                    
                elif response.status_code >= 500:
                    logger.warning(f"Server error {response.status_code}. Sleeping {backoff}s...")
                    time.sleep(backoff)
                    retries += 1
                    continue
                    
                else:
                    logger.error(f"HTTP {response.status_code} for tile {tile_id}")
                    return False

            except requests.RequestException as e:
                logger.error(f"Network error for tile {tile_id}: {e}")
                time.sleep(backoff)
                retries += 1
        
        logger.error(f"❌ Failed to download tile {tile_id} after {max_retries} retries")
        return False

    def harvest_city(self, city_name: str, bbox: Dict[str, float]):
        """Main entry point to harvest a city."""
        logger.info(f"Starting harvest for {city_name}...")
        
        city_dir = self.raw_data_dir / city_name.lower().replace(" ", "_")
        city_dir.mkdir(exist_ok=True)
        
        tiles = self.generate_tiles(bbox)
        logger.info(f"Generated {len(tiles)} tiles for {city_name}")
        
        success_count = 0
        for i, tile in enumerate(tiles):
            tile_id = f"tile_{i}"
            if self.fetch_tile(tile, tile_id, city_dir):
                success_count += 1
            
            # Progress log
            if i % 5 == 0:
                logger.info(f"Progress: {i+1}/{len(tiles)} tiles checked/downloaded")
                
        logger.info(f"Harvest complete for {city_name}. Success: {success_count}/{len(tiles)}")
