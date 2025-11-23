"""
Debug OSM Queries
"""

import overpy
from sources.osm import OSMCollector

# Test the actual collector
collector = OSMCollector()

# Thailand bbox from config
bbox = {'north': 20.4648, 'south': 5.6108, 'east': 105.6392, 'west': 97.3439}

print("Testing OSM Collector with Thailand bounding box")
print(f"BBox: {bbox}")
print("="*60)

# Try collecting temples
print("\n1. Collecting temples...")
temples = collector.collect_pois_in_bounding_box(bbox, 'temple', limit=5)
print(f"Found {len(temples)} temples")
if temples:
    for t in temples[:3]:
        print(f"  - {t.get('name')}")

# Try collecting beaches
print("\n2. Collecting beaches...")
beaches = collector.collect_pois_in_bounding_box(bbox, 'beach', limit=5)
print(f"Found {len(beaches)} beaches")
if beaches:
    for b in beaches[:3]:
        print(f"  - {b.get('name')}")

# Try direct query with same bbox
print("\n3. Direct query test...")
api = overpy.Overpass()
bbox_str = f"{bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']}"
query = f"""
[out:json][timeout:60];
(
  node["amenity"="place_of_worship"]["religion"="buddhist"]({bbox_str});
);
out center tags 5;
"""
print(f"Query: {query}")
result = api.query(query)
print(f"Found {len(result.nodes)} nodes")
if result.nodes:
    for node in result.nodes[:3]:
        print(f"  - {node.tags.get('name', 'Unknown')}")
