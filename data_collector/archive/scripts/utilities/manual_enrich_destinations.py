"""
Manual Data Enrichment Script
Adds vibe_tags and best_time_to_visit to existing destinations in public schema
"""
import sys
sys.path.append('/Users/alokanand/AllInOne/BeyondEscapism/BeyondEscapism/data_collector')

from utils.database import Database

# Destination enrichment data
DESTINATION_DATA = {
    # Thailand
    "Bangkok": {
        "vibe_tags": ["vibrant", "cultural", "foodie", "urban", "nightlife"],
        "best_time_to_visit": "November to February",
        "category_tags": ["city", "culture", "food", "shopping"]
    },
    "Chiang Mai": {
        "vibe_tags": ["cultural", "peaceful", "nature", "spiritual", "adventure"],
        "best_time_to_visit": "November to February",
        "category_tags": ["culture", "temples", "nature", "wellness"]
    },
    "Phuket": {
        "vibe_tags": ["beach", "tropical", "relaxing", "adventure", "nightlife"],
        "best_time_to_visit": "November to April",
        "category_tags": ["beach", "island", "water-sports", "resort"]
    },
    "Pattaya": {
        "vibe_tags": ["beach", "nightlife", "urban", "entertainment"],
        "best_time_to_visit": "November to February",
        "category_tags": ["beach", "entertainment", "nightlife"]
    },
    "Krabi": {
        "vibe_tags": ["beach", "nature", "adventure", "scenic", "relaxing"],
        "best_time_to_visit": "November to March",
        "category_tags": ["beach", "nature", "island-hopping", "rock-climbing"]
    },
    "Ayutthaya": {
        "vibe_tags": ["historical", "cultural", "heritage", "peaceful"],
        "best_time_to_visit": "November to February",
        "category_tags": ["history", "temples", "unesco", "culture"]
    },
    
    # Vietnam
    "Ho Chi Minh City": {
        "vibe_tags": ["vibrant", "historical", "foodie", "urban", "cultural"],
        "best_time_to_visit": "December to April",
        "category_tags": ["city", "history", "food", "culture"]
    },
    "Hanoi": {
        "vibe_tags": ["cultural", "historical", "foodie", "charming", "traditional"],
        "best_time_to_visit": "October to April",
        "category_tags": ["city", "culture", "history", "food"]
    },
    "Da Nang": {
        "vibe_tags": ["beach", "modern", "scenic", "relaxing", "foodie"],
        "best_time_to_visit": "February to May",
        "category_tags": ["beach", "city", "nature", "food"]
    },
    "Hoi An": {
        "vibe_tags": ["charming", "historical", "romantic", "cultural", "peaceful"],
        "best_time_to_visit": "February to April",
        "category_tags": ["unesco", "history", "culture", "lanterns"]
    },
    "Nha Trang": {
        "vibe_tags": ["beach", "tropical", "adventure", "relaxing", "scenic"],
        "best_time_to_visit": "January to August",
        "category_tags": ["beach", "diving", "island", "resort"]
    },
    "Hue": {
        "vibe_tags": ["historical", "cultural", "imperial", "peaceful", "scenic"],
        "best_time_to_visit": "February to April",
        "category_tags": ["history", "unesco", "culture", "imperial"]
    },
    
    # India
    "Delhi": {
        "vibe_tags": ["historical", "vibrant", "cultural", "urban", "diverse"],
        "best_time_to_visit": "October to March",
        "category_tags": ["city", "history", "culture", "monuments"]
    },
    "Mumbai": {
        "vibe_tags": ["vibrant", "urban", "diverse", "entertainment", "coastal"],
        "best_time_to_visit": "November to February",
        "category_tags": ["city", "bollywood", "food", "nightlife"]
    },
    "Agra": {
        "vibe_tags": ["historical", "romantic", "iconic", "cultural"],
        "best_time_to_visit": "October to March",
        "category_tags": ["unesco", "monuments", "history", "taj-mahal"]
    },
    "Jaipur": {
        "vibe_tags": ["historical", "colorful", "royal", "cultural", "vibrant"],
        "best_time_to_visit": "November to February",
        "category_tags": ["history", "palaces", "culture", "heritage"]
    },
    "Goa": {
        "vibe_tags": ["beach", "relaxing", "nightlife", "tropical", "laid-back"],
        "best_time_to_visit": "November to February",
        "category_tags": ["beach", "party", "portuguese", "resort"]
    },
    "Varanasi": {
        "vibe_tags": ["spiritual", "ancient", "cultural", "mystical", "sacred"],
        "best_time_to_visit": "October to March",
        "category_tags": ["spiritual", "ganges", "temples", "culture"]
    },
    "Udaipur": {
        "vibe_tags": ["romantic", "royal", "scenic", "cultural", "luxurious"],
        "best_time_to_visit": "October to March",
        "category_tags": ["palaces", "lakes", "heritage", "luxury"]
    },
    "Amritsar": {
        "vibe_tags": ["spiritual", "cultural", "historical", "peaceful"],
        "best_time_to_visit": "October to March",
        "category_tags": ["spiritual", "golden-temple", "culture", "history"]
    },
    "Leh": {
        "vibe_tags": ["adventure", "scenic", "peaceful", "spiritual", "remote"],
        "best_time_to_visit": "May to September",
        "category_tags": ["mountains", "adventure", "buddhist", "trekking"]
    },
    "Jaisalmer": {
        "vibe_tags": ["desert", "historical", "romantic", "adventure", "unique"],
        "best_time_to_visit": "October to March",
        "category_tags": ["desert", "fort", "heritage", "camel-safari"]
    }
}

def enrich_destinations():
    """Update destinations in public schema with enriched data"""
    db = Database(schema='public')
    
    print("🔧 Starting manual data enrichment...\n")
    
    updated_count = 0
    not_found = []
    
    for dest_name, enrichment in DESTINATION_DATA.items():
        try:
            # Check if destination exists
            result = db.client.table('destinations').select('id, name').eq('name', dest_name).execute()
            
            if result.data:
                dest_id = result.data[0]['id']
                
                # Update with enriched data
                db.client.table('destinations').update({
                    'vibe_tags': enrichment['vibe_tags'],
                    'best_time_to_visit': enrichment['best_time_to_visit'],
                    'category_tags': enrichment['category_tags']
                }).eq('id', dest_id).execute()
                
                print(f"✅ Updated {dest_name}")
                updated_count += 1
            else:
                not_found.append(dest_name)
                print(f"⚠️  Not found: {dest_name}")
                
        except Exception as e:
            print(f"❌ Error updating {dest_name}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Updated: {updated_count}")
    print(f"   Not found: {len(not_found)}")
    if not_found:
        print(f"   Missing: {', '.join(not_found)}")

if __name__ == "__main__":
    enrich_destinations()
