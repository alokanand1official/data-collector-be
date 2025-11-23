"""
Fetch real images from Wikimedia Commons for destinations without images
"""
import sys
sys.path.append('/Users/alokanand/AllInOne/BeyondEscapism/BeyondEscapism/data_collector')

from utils.database import Database
from sources.wikidata import WikidataCollector
import time

db = Database(schema='public')
wikidata = WikidataCollector()

# Destinations without images (from analysis)
MISSING_IMAGES = [
    # India
    "Agra", "Delhi", "Darjeeling", "Jaisalmer", "Leh", "Rishikesh", 
    "Udaipur", "Kochi", "Mysore", "Ooty", "Pondicherry",
    # Thailand
    "Ayutthaya", "Krabi", "Koh Samui", "Pai", "Kanchanaburi",
    "Koh Chang", "Koh Lanta", "Sukhothai", "Koh Phangan",
    # Vietnam
    "Ninh Binh", "Phu Quoc", "Hue", "Sapa",
]

print("🖼️  Fetching images from Wikimedia Commons...\n")

updated_count = 0
not_found = []

for dest_name in MISSING_IMAGES:
    print(f"📍 {dest_name}...", end=" ")
    
    try:
        # Get from Wikidata
        data = wikidata.get_city_details(dest_name)
        
        if data and data.get('image'):
            # Update database
            db.client.table('destinations').update({
                'image_url': data['image'],
                'images': [data['image']]
            }).eq('name', dest_name).execute()
            
            print(f"✅ Updated")
            updated_count += 1
        else:
            print(f"❌ No image found")
            not_found.append(dest_name)
        
        # Rate limiting - be nice to Wikidata
        time.sleep(0.5)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        not_found.append(dest_name)

print(f"\n📊 Summary:")
print(f"   Updated: {updated_count}/{len(MISSING_IMAGES)}")
print(f"   Not found: {len(not_found)}")

if not_found:
    print(f"\n⚠️  Still missing images:")
    for name in not_found:
        print(f"   - {name}")

print(f"\n✨ Refresh the Discover page to see unique images!")
