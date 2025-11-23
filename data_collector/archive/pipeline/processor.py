import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)

class Processor:
    """
    Processes raw OSM JSON files into clean, deduplicated POI data.
    """
    
    def __init__(self, raw_data_dir: str = "raw_data", processed_data_dir: str = "processed_data"):
        self.raw_data_dir = Path(raw_data_dir)
        self.processed_data_dir = Path(processed_data_dir)
        self.processed_data_dir.mkdir(exist_ok=True)

    def _get_poi_type(self, tags: Dict[str, str]) -> str:
        """Determines the POI type from OSM tags."""
        if 'amenity' in tags:
            if tags['amenity'] == 'place_of_worship': return 'temple' # Simplified
            if tags['amenity'] in ['restaurant', 'cafe', 'food_court']: return 'restaurant'
            if tags['amenity'] == 'marketplace': return 'market'
        
        if 'tourism' in tags:
            if tags['tourism'] == 'hotel': return 'hotel'
            if tags['tourism'] == 'museum': return 'museum'
            if tags['tourism'] == 'viewpoint': return 'viewpoint'
        
        if 'natural' in tags:
            if tags['natural'] == 'beach': return 'beach'
            if tags['natural'] == 'waterfall': return 'waterfall'
            
        if 'place' in tags:
            if tags['place'] == 'island': return 'island'

        if 'historic' in tags:
            return 'historic'
            
        if 'tourism' in tags and tags['tourism'] == 'attraction':
            return 'historic'
            
        return 'other' # Fallback

    def _parse_element(self, element: Dict[str, Any]) -> Dict[str, Any]:
        """Parses a single OSM element into our schema."""
        tags = element.get('tags', {})
        
        # Skip if no name (low quality)
        if 'name' not in tags and 'name:en' not in tags:
            return None
            
        poi_type = self._get_poi_type(tags)
        if poi_type == 'other':
            return None # Skip uninteresting items for now

        lat = element.get('lat')
        lon = element.get('lon')
        
        # Handle ways (polygons) - simplified center
        if 'center' in element:
            lat = element['center']['lat']
            lon = element['center']['lon']
        elif element['type'] == 'way' and 'nodes' in element:
             # We don't have node coords here unless we resolve them. 
             # Overpass 'out center;' gives us 'center' key for ways.
             pass

        if lat is None or lon is None:
            return None

        return {
            'name': tags.get('name:en', tags.get('name')), # Prefer English
            'name_local': tags.get('name'),
            'poi_type': poi_type,
            'coordinates': {'lat': lat, 'lng': lon},
            'osm_id': f"{element['type']}/{element['id']}",
            'description': tags.get('description', tags.get('description:en')),
            'metadata': {
                'osm_tags': tags
            }
        }

    def process_city(self, city_name: str):
        """Processes all raw files for a city."""
        logger.info(f"Processing data for {city_name}...")
        
        city_raw_dir = self.raw_data_dir / city_name.lower().replace(" ", "_")
        if not city_raw_dir.exists():
            logger.error(f"No raw data found for {city_name}")
            return

        seen_ids: Set[str] = set()
        clean_pois: List[Dict[str, Any]] = []
        
        files = list(city_raw_dir.glob("*.json"))
        logger.info(f"Found {len(files)} raw files")

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if 'elements' not in data:
                    continue
                    
                for element in data['elements']:
                    osm_id = f"{element['type']}/{element['id']}"
                    
                    if osm_id in seen_ids:
                        continue
                    
                    poi = self._parse_element(element)
                    if poi:
                        poi['city_name'] = city_name
                        # Lookup country from config if possible, else default
                        from config.cities_config import CITIES
                        country = "Unknown"
                        for key, cdata in CITIES.items():
                            if cdata['name'].lower() == city_name.lower():
                                country = cdata['country']
                                break
                        poi['country_code'] = country
                        
                        clean_pois.append(poi)
                        seen_ids.add(osm_id)
                        
            except json.JSONDecodeError:
                logger.warning(f"Corrupt file: {file_path}")
            except Exception as e:
                logger.warning(f"Error processing file {file_path}: {e}")

        # Save processed data
        output_file = self.processed_data_dir / f"{city_name.lower().replace(' ', '_')}_pois.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(clean_pois, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Processed {len(clean_pois)} unique POIs for {city_name}")
        logger.info(f"Saved to {output_file}")
        return clean_pois
