"""
Country-based Tourism Destination Discovery
Automatically identifies important tourism cities for any country.
"""

import requests
from typing import List, Dict
import json

class TourismDestinationDiscovery:
    """
    Discovers important tourism destinations for a given country.
    Uses multiple data sources to identify cities worth collecting data for.
    """
    
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        
    def discover_destinations(self, country: str, min_population: int = 50000) -> List[Dict]:
        """
        Discovers tourism destinations for a country.
        
        Args:
            country: Country name (e.g., "Azerbaijan", "Georgia")
            min_population: Minimum population for a city to be included
            
        Returns:
            List of destination dictionaries with name, coordinates, bbox
        """
        print(f"🔍 Discovering tourism destinations in {country}...")
        
        # Step 1: Get major cities from Overpass
        cities = self._get_major_cities(country, min_population)
        
        # Step 2: Get UNESCO sites
        unesco_sites = self._get_unesco_sites(country)
        
        # Step 3: Get popular tourist destinations from Wikidata
        tourist_destinations = self._get_tourist_destinations(country)
        
        # Step 4: Merge and deduplicate
        all_destinations = self._merge_destinations(cities, unesco_sites, tourist_destinations)
        
        # Step 5: Calculate bounding boxes
        destinations_with_bbox = self._add_bounding_boxes(all_destinations)
        
        print(f"✅ Found {len(destinations_with_bbox)} destinations in {country}")
        return destinations_with_bbox
        
    def _get_major_cities(self, country: str, min_population: int) -> List[Dict]:
        """Get major cities using Overpass API"""
        query = f"""
        [out:json];
        area["name:en"="{country}"]->.country;
        (
          node(area.country)["place"~"city|town"]["population"];
        );
        out body;
        """
        
        try:
            response = requests.post(self.overpass_url, data={"data": query}, timeout=60)
            data = response.json()
            
            cities = []
            for element in data.get('elements', []):
                tags = element.get('tags', {})
                population = int(tags.get('population', 0))
                
                if population >= min_population:
                    cities.append({
                        'name': tags.get('name:en', tags.get('name')),
                        'lat': element['lat'],
                        'lon': element['lon'],
                        'population': population,
                        'type': 'city'
                    })
            
            return sorted(cities, key=lambda x: x['population'], reverse=True)
        except Exception as e:
            print(f"⚠️ Error fetching cities: {e}")
            return []
            
    def _get_unesco_sites(self, country: str) -> List[Dict]:
        """Get UNESCO World Heritage sites"""
        query = f"""
        [out:json];
        area["name:en"="{country}"]->.country;
        (
          node(area.country)["heritage"="1"];
          way(area.country)["heritage"="1"];
        );
        out center;
        """
        
        try:
            response = requests.post(self.overpass_url, data={"data": query}, timeout=60)
            data = response.json()
            
            sites = []
            for element in data.get('elements', []):
                tags = element.get('tags', {})
                
                # Get coordinates
                if element['type'] == 'node':
                    lat, lon = element['lat'], element['lon']
                else:
                    center = element.get('center', {})
                    lat, lon = center.get('lat'), center.get('lon')
                
                if lat and lon:
                    sites.append({
                        'name': tags.get('name:en', tags.get('name')),
                        'lat': lat,
                        'lon': lon,
                        'type': 'unesco'
                    })
            
            return sites
        except Exception as e:
            print(f"⚠️ Error fetching UNESCO sites: {e}")
            return []
            
    def _get_tourist_destinations(self, country: str) -> List[Dict]:
        """Get popular tourist destinations from Wikidata"""
        # Simplified version - in production, use Wikidata SPARQL
        # For now, return empty list
        return []
        
    def _merge_destinations(self, *destination_lists) -> List[Dict]:
        """Merge and deduplicate destinations"""
        all_dests = []
        seen_names = set()
        
        for dest_list in destination_lists:
            for dest in dest_list:
                name = dest['name']
                if name and name not in seen_names:
                    seen_names.add(name)
                    all_dests.append(dest)
        
        return all_dests
        
    def _add_bounding_boxes(self, destinations: List[Dict]) -> List[Dict]:
        """Calculate bounding boxes for each destination"""
        for dest in destinations:
            lat, lon = dest['lat'], dest['lon']
            
            # Default bbox: ~20km radius
            offset = 0.2  # degrees (~20km)
            
            dest['bbox'] = {
                'north': lat + offset,
                'south': lat - offset,
                'east': lon + offset,
                'west': lon - offset
            }
            
        return destinations
        
    def save_to_config(self, destinations: List[Dict], country: str, output_file: str = "discovered_cities.py"):
        """Save discovered destinations to a Python config file"""
        config_code = f'''"""
Auto-discovered tourism destinations for {country}
Generated by TourismDestinationDiscovery
"""

DISCOVERED_CITIES = {{
'''
        
        for dest in destinations:
            city_key = dest['name'].lower().replace(' ', '_').replace('-', '_')
            config_code += f'''    "{city_key}": {{
        "name": "{dest['name']}",
        "country": "{country}",
        "bbox": {{
            "north": {dest['bbox']['north']},
            "south": {dest['bbox']['south']},
            "east": {dest['bbox']['east']},
            "west": {dest['bbox']['west']}
        }},
        "coordinates": {{"lat": {dest['lat']}, "lng": {dest['lon']}}},
        "type": "{dest.get('type', 'city')}"
    }},
'''
        
        config_code += "}\n"
        
        with open(output_file, 'w') as f:
            f.write(config_code)
            
        print(f"✅ Saved {len(destinations)} destinations to {output_file}")


# Example usage
if __name__ == "__main__":
    discovery = TourismDestinationDiscovery()
    
    # Discover destinations for Azerbaijan
    azerbaijan_dests = discovery.discover_destinations("Azerbaijan", min_population=30000)
    discovery.save_to_config(azerbaijan_dests, "Azerbaijan")
    
    # Print summary
    print("\nDiscovered Destinations:")
    for dest in azerbaijan_dests:
        print(f"  - {dest['name']} ({dest.get('type', 'city')})")
