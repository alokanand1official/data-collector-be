import json
import logging
import time
import requests
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.cities_config import CITIES

logger = logging.getLogger("OSMExtractor")

class OSMExtractor:
    """
    Extracts raw data from OpenStreetMap and saves to Bronze Layer.
    """
    
    def __init__(self, bronze_dir: Path):
        self.bronze_dir = bronze_dir
        self.overpass_url = "http://overpass-api.de/api/interpreter"
        self.headers = {
            'User-Agent': 'TravelDataCollector/1.0 (contact@example.com)'
        }

    def extract_city(self, city_name: str) -> bool:
        """
        Harvests data for a city and saves to Bronze layer.
        """
        city_key = city_name.lower().replace(" ", "_")
        city_config = CITIES.get(city_key)
        
        if not city_config:
            logger.error(f"City configuration not found for: {city_name}")
            return False
            
        bbox = city_config['bbox']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.bronze_dir / city_key / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Starting harvest for {city_name}...")
        
        # Define grid for tiling (simple 4x4 grid for now)
        # In a real scenario, reuse the sophisticated tiling from original harvester
        tiles = self._generate_tiles(bbox)
        
        total_elements = 0
        for i, tile in enumerate(tiles):
            data = self._fetch_tile(tile)
            if data:
                elements = data.get('elements', [])
                count = len(elements)
                total_elements += count
                
                # Save raw tile
                tile_file = output_dir / f"tile_{i}.json"
                with open(tile_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False)
                
                logger.info(f"Saved tile {i} with {count} elements")
                time.sleep(1) # Respect rate limits
                
        # Save metadata
        metadata = {
            "city": city_name,
            "timestamp": timestamp,
            "total_elements": total_elements,
            "source": "OpenStreetMap",
            "bbox": bbox
        }
        with open(output_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"✅ Harvest complete for {city_name}. Total elements: {total_elements}")
        return True

    def _generate_tiles(self, bbox: Dict) -> List[Dict]:
        """Simple 2x2 grid for demonstration."""
        # TODO: Port the full tiling logic from original harvester
        lat_step = (bbox['north'] - bbox['south']) / 2
        lon_step = (bbox['east'] - bbox['west']) / 2
        
        tiles = []
        for i in range(2):
            for j in range(2):
                south = bbox['south'] + i * lat_step
                north = south + lat_step
                west = bbox['west'] + j * lon_step
                east = west + lon_step
                tiles.append({'north': north, 'south': south, 'east': east, 'west': west})
        return tiles

    def _fetch_tile(self, bbox: Dict) -> Optional[Dict]:
        """Fetches data for a single tile."""
        query = f"""
        [out:json][timeout:25];
        (
          node["tourism"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["tourism"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          relation["tourism"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          
          node["amenity"~"restaurant|cafe|bar|pub"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["amenity"~"restaurant|cafe|bar|pub"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          
          node["historic"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
          way["historic"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
        );
        out body;
        >;
        out skel qt;
        """
        try:
            response = requests.post(self.overpass_url, data=query, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("Rate limited. Sleeping...")
                time.sleep(5)
                return self._fetch_tile(bbox) # Retry
            else:
                logger.error(f"Error fetching tile: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Exception fetching tile: {e}")
            return None
