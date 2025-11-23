"""
Curated Tourism Seed Data
High-quality, must-visit places for priority cities
"""
import sys
sys.path.append('/Users/alokanand/AllInOne/BeyondEscapism/BeyondEscapism/data_collector')

from utils.database import Database
import uuid

# Curated tourism activities
SEED_ACTIVITIES = {
    "Bangkok": {
        "destination_name": "Bangkok",
        "activities": [
            {
                "name": "Grand Palace & Wat Phra Kaew",
                "category": "temple",
                "description": "Bangkok's most iconic landmark, the Grand Palace complex houses the sacred Emerald Buddha. A must-visit for its stunning Thai architecture, intricate details, and cultural significance. Allow 2-3 hours to explore fully.",
                "location": {"lat": 13.7500, "lng": 100.4917},
                "tags": ["cultural", "iconic", "historical", "instagram-worthy"],
                "best_time": "morning",
                "duration": 3,
                "entry_fee": "500 THB",
                "dress_code": "Modest clothing required (shoulders and knees covered)"
            },
            {
                "name": "Wat Arun (Temple of Dawn)",
                "category": "temple",
                "description": "Stunning riverside temple famous for its towering spire decorated with colorful porcelain. Climb to the top for panoramic views of the Chao Phraya River. Most beautiful at sunset.",
                "location": {"lat": 13.7437, "lng": 100.4887},
                "tags": ["scenic", "cultural", "instagram-worthy", "peaceful"],
                "best_time": "sunset",
                "duration": 2,
                "entry_fee": "100 THB"
            },
            {
                "name": "Chatuchak Weekend Market",
                "category": "market",
                "description": "One of the world's largest weekend markets with over 15,000 stalls. Find everything from clothes and handicrafts to street food and antiques. A shopper's paradise and cultural experience.",
                "location": {"lat": 13.7998, "lng": 100.5501},
                "tags": ["vibrant", "shopping", "foodie", "local", "crowded"],
                "best_time": "morning",
                "duration": 3,
                "entry_fee": "Free",
                "open_days": "Saturday and Sunday"
            },
            {
                "name": "Khao San Road",
                "category": "nightlife",
                "description": "Famous backpacker street known for its vibrant nightlife, street food, bars, and budget shopping. Great for meeting travelers and experiencing Bangkok's party scene.",
                "location": {"lat": 13.7589, "lng": 100.4977},
                "tags": ["nightlife", "social", "budget", "vibrant"],
                "best_time": "evening",
                "duration": 2,
                "entry_fee": "Free"
            },
            {
                "name": "Jim Thompson House",
                "category": "museum",
                "description": "Beautiful traditional Thai house museum showcasing Southeast Asian art collection. Learn about Thai silk and the mysterious disappearance of Jim Thompson. Guided tours only.",
                "location": {"lat": 13.7467, "lng": 100.5345},
                "tags": ["cultural", "historical", "peaceful", "educational"],
                "best_time": "afternoon",
                "duration": 2,
                "entry_fee": "200 THB"
            },
            {
                "name": "Asiatique The Riverfront",
                "category": "entertainment",
                "description": "Open-air night market and entertainment complex along the Chao Phraya River. Combines shopping, dining, and riverside views. Take the free shuttle boat from Saphan Taksin BTS.",
                "location": {"lat": 13.7044, "lng": 100.5069},
                "tags": ["shopping", "dining", "scenic", "family-friendly"],
                "best_time": "evening",
                "duration": 3,
                "entry_fee": "Free"
            },
            {
                "name": "Lumpini Park",
                "category": "park",
                "description": "Bangkok's largest public park, perfect for morning jogs, paddle boating, or escaping the city chaos. Watch for monitor lizards! Free outdoor aerobics classes in the evening.",
                "location": {"lat": 13.7307, "lng": 100.5418},
                "tags": ["peaceful", "nature", "wellness", "free"],
                "best_time": "morning",
                "duration": 1,
                "entry_fee": "Free"
            },
            {
                "name": "Thip Samai (Pad Thai Restaurant)",
                "category": "restaurant",
                "description": "Legendary pad thai restaurant, often called the best in Bangkok. Famous for their pad thai wrapped in egg omelet. Always busy but worth the wait. Cash only.",
                "location": {"lat": 13.7548, "lng": 100.5026},
                "tags": ["foodie", "authentic", "local", "budget"],
                "best_time": "lunch_or_dinner",
                "price_range": "budget",
                "cuisine": "Thai"
            }
        ]
    },
    "Delhi": {
        "destination_name": "Delhi",
        "activities": [
            {
                "name": "Red Fort (Lal Qila)",
                "category": "historical_site",
                "description": "Iconic 17th-century Mughal fort and UNESCO World Heritage Site. Massive red sandstone walls enclose palaces, museums, and gardens. Sound and light show in the evening. A must-visit for history enthusiasts.",
                "location": {"lat": 28.6562, "lng": 77.2410},
                "tags": ["historical", "cultural", "iconic", "unesco"],
                "best_time": "morning",
                "duration": 2,
                "entry_fee": "₹50 (Indians), ₹600 (Foreigners)"
            },
            {
                "name": "India Gate",
                "category": "monument",
                "description": "42-meter tall war memorial arch honoring Indian soldiers. Beautiful gardens surround the monument, making it perfect for evening strolls. Popular spot for picnics and ice cream.",
                "location": {"lat": 28.6129, "lng": 77.2295},
                "tags": ["iconic", "peaceful", "instagram-worthy", "free"],
                "best_time": "evening",
                "duration": 1,
                "entry_fee": "Free"
            },
            {
                "name": "Qutub Minar",
                "category": "historical_site",
                "description": "UNESCO World Heritage Site featuring the world's tallest brick minaret at 73 meters. Beautiful Indo-Islamic architecture dating back to 1193. Explore the complex with ancient ruins and iron pillar.",
                "location": {"lat": 28.5244, "lng": 77.1855},
                "tags": ["historical", "unesco", "architectural", "peaceful"],
                "best_time": "morning",
                "duration": 2,
                "entry_fee": "₹40 (Indians), ₹600 (Foreigners)"
            },
            {
                "name": "Humayun's Tomb",
                "category": "historical_site",
                "description": "Magnificent Mughal garden tomb and UNESCO site, inspiration for the Taj Mahal. Beautiful Persian-style gardens and stunning architecture. Best visited in late afternoon for photography.",
                "location": {"lat": 28.5933, "lng": 77.2507},
                "tags": ["historical", "unesco", "romantic", "scenic"],
                "best_time": "afternoon",
                "duration": 2,
                "entry_fee": "₹40 (Indians), ₹600 (Foreigners)"
            },
            {
                "name": "Chandni Chowk Market",
                "category": "market",
                "description": "Old Delhi's chaotic and colorful market, one of India's oldest and busiest. Narrow lanes filled with street food, spices, jewelry, and textiles. A sensory overload and authentic Delhi experience.",
                "location": {"lat": 28.6506, "lng": 77.2303},
                "tags": ["vibrant", "chaotic", "foodie", "shopping", "authentic"],
                "best_time": "morning",
                "duration": 2,
                "entry_fee": "Free"
            },
            {
                "name": "Lotus Temple",
                "category": "temple",
                "description": "Stunning modern Bahá'í House of Worship shaped like a lotus flower. Open to all religions, it's a peaceful place for meditation. Beautiful architecture and serene gardens.",
                "location": {"lat": 28.5535, "lng": 77.2588},
                "tags": ["peaceful", "spiritual", "architectural", "instagram-worthy"],
                "best_time": "afternoon",
                "duration": 1,
                "entry_fee": "Free"
            },
            {
                "name": "Karim's Restaurant",
                "category": "restaurant",
                "description": "Legendary Mughlai restaurant since 1913 near Jama Masjid. Famous for kebabs, nihari, and authentic Old Delhi flavors. Always crowded but worth it. Cash only, basic seating.",
                "location": {"lat": 28.6506, "lng": 77.2340},
                "tags": ["foodie", "authentic", "historic", "local"],
                "best_time": "lunch_or_dinner",
                "price_range": "budget",
                "cuisine": "Mughlai, North Indian"
            },
            {
                "name": "Lodhi Garden",
                "category": "park",
                "description": "Beautiful 90-acre park with 15th-century tombs and monuments. Popular for morning walks, yoga, and picnics. Peaceful escape from Delhi's chaos with well-maintained gardens.",
                "location": {"lat": 28.5932, "lng": 77.2197},
                "tags": ["peaceful", "nature", "historical", "free"],
                "best_time": "morning",
                "duration": 2,
                "entry_fee": "Free"
            }
        ]
    },
    "Ho Chi Minh City": {
        "destination_name": "Ho Chi Minh City",
        "activities": [
            {
                "name": "War Remnants Museum",
                "category": "museum",
                "description": "Powerful museum documenting the Vietnam War from Vietnamese perspective. Displays military equipment, photographs, and artifacts. Emotional and educational experience.",
                "location": {"lat": 10.7797, "lng": 106.6919},
                "tags": ["historical", "educational", "emotional", "important"],
                "best_time": "morning",
                "duration": 2,
                "entry_fee": "40,000 VND"
            },
            {
                "name": "Ben Thanh Market",
                "category": "market",
                "description": "Iconic central market selling everything from souvenirs to street food. Great for shopping and trying local snacks. Night market outside opens after 6 PM with food stalls.",
                "location": {"lat": 10.7724, "lng": 106.6980},
                "tags": ["vibrant", "shopping", "foodie", "touristy"],
                "best_time": "afternoon",
                "duration": 2,
                "entry_fee": "Free"
            },
            {
                "name": "Notre-Dame Cathedral Basilica",
                "category": "historical_site",
                "description": "French colonial cathedral built in late 1800s with materials imported from France. Beautiful architecture and peaceful atmosphere. Currently under renovation but worth seeing from outside.",
                "location": {"lat": 10.7798, "lng": 106.6990},
                "tags": ["historical", "architectural", "peaceful", "instagram-worthy"],
                "best_time": "morning",
                "duration": 1,
                "entry_fee": "Free"
            },
            {
                "name": "Cu Chi Tunnels",
                "category": "historical_site",
                "description": "Extensive underground tunnel network used during Vietnam War. Crawl through tunnels, see booby traps, and learn about guerrilla warfare. Half-day trip from city center.",
                "location": {"lat": 11.0511, "lng": 106.4943},
                "tags": ["historical", "adventure", "educational", "unique"],
                "best_time": "morning",
                "duration": 4,
                "entry_fee": "110,000 VND + transport"
            },
            {
                "name": "Bui Vien Walking Street",
                "category": "nightlife",
                "description": "Backpacker street famous for nightlife, bars, street food, and people-watching. Vibrant atmosphere with live music and cheap beer. Best experienced on weekend nights.",
                "location": {"lat": 10.7677, "lng": 106.6918},
                "tags": ["nightlife", "social", "vibrant", "budget"],
                "best_time": "evening",
                "duration": 2,
                "entry_fee": "Free"
            },
            {
                "name": "Saigon Central Post Office",
                "category": "historical_site",
                "description": "Beautiful French colonial post office designed by Gustave Eiffel. Still functioning post office with stunning interior. Perfect for sending postcards and photos.",
                "location": {"lat": 10.7799, "lng": 106.6999},
                "tags": ["historical", "architectural", "instagram-worthy", "free"],
                "best_time": "morning",
                "duration": 1,
                "entry_fee": "Free"
            },
            {
                "name": "Pho 2000",
                "category": "restaurant",
                "description": "Famous pho restaurant where Bill Clinton ate in 2000. Authentic Vietnamese pho with fresh herbs and flavorful broth. Always busy but service is quick.",
                "location": {"lat": 10.7730, "lng": 106.6990},
                "tags": ["foodie", "authentic", "local", "budget"],
                "best_time": "lunch",
                "price_range": "budget",
                "cuisine": "Vietnamese"
            }
        ]
    },
    "Phuket": {
        "destination_name": "Phuket",
        "activities": [
            {
                "name": "Patong Beach",
                "category": "beach",
                "description": "Phuket's most famous beach with 3km of white sand. Great for swimming, water sports, and people-watching. Lively atmosphere with nearby restaurants and nightlife.",
                "location": {"lat": 7.8965, "lng": 98.2963},
                "tags": ["beach", "vibrant", "social", "water-sports"],
                "best_time": "afternoon",
                "duration": 3,
                "entry_fee": "Free"
            },
            {
                "name": "Big Buddha",
                "category": "temple",
                "description": "45-meter tall white marble Buddha statue visible from much of southern Phuket. Panoramic views of the island. Peaceful atmosphere and free entry. Dress modestly.",
                "location": {"lat": 7.8911, "lng": 98.3078},
                "tags": ["cultural", "scenic", "peaceful", "instagram-worthy"],
                "best_time": "sunset",
                "duration": 1,
                "entry_fee": "Free"
            },
            {
                "name": "Phi Phi Islands Day Trip",
                "category": "island_hopping",
                "description": "Stunning limestone islands with crystal-clear waters. Snorkel, swim, and visit Maya Bay (The Beach movie location). Full-day tour includes lunch and snorkeling gear.",
                "location": {"lat": 7.7407, "lng": 98.7784},
                "tags": ["scenic", "adventure", "instagram-worthy", "tropical"],
                "best_time": "full_day",
                "duration": 8,
                "entry_fee": "1,500-2,500 THB (tour)"
            },
            {
                "name": "Old Phuket Town",
                "category": "cultural_area",
                "description": "Charming historic district with colorful Sino-Portuguese buildings, street art, cafes, and boutiques. Perfect for walking, photography, and trying local food.",
                "location": {"lat": 7.8804, "lng": 98.3923},
                "tags": ["cultural", "charming", "instagram-worthy", "foodie"],
                "best_time": "afternoon",
                "duration": 2,
                "entry_fee": "Free"
            },
            {
                "name": "Bangla Road",
                "category": "nightlife",
                "description": "Phuket's famous nightlife street in Patong. Neon lights, bars, clubs, and entertainment. Pedestrian-only street comes alive after dark. Family-friendly during early evening.",
                "location": {"lat": 7.8946, "lng": 98.2968},
                "tags": ["nightlife", "vibrant", "entertainment", "social"],
                "best_time": "evening",
                "duration": 2,
                "entry_fee": "Free"
            },
            {
                "name": "Kata Beach",
                "category": "beach",
                "description": "Beautiful beach with softer sand and calmer waters than Patong. Great for families and swimming. Less crowded with good restaurants nearby. Surfing in low season.",
                "location": {"lat": 7.8145, "lng": 98.2929},
                "tags": ["beach", "peaceful", "family-friendly", "scenic"],
                "best_time": "morning",
                "duration": 3,
                "entry_fee": "Free"
            }
        ]
    },
    "Agra": {
        "destination_name": "Agra",
        "activities": [
            {
                "name": "Taj Mahal",
                "category": "monument",
                "description": "One of the Seven Wonders of the World and UNESCO site. Stunning white marble mausoleum built by Shah Jahan for his wife. Visit at sunrise for magical light and fewer crowds. Allow 2-3 hours.",
                "location": {"lat": 27.1751, "lng": 78.0421},
                "tags": ["iconic", "romantic", "unesco", "instagram-worthy"],
                "best_time": "sunrise",
                "duration": 3,
                "entry_fee": "₹50 (Indians), ₹1,100 (Foreigners)",
                "closed": "Friday"
            },
            {
                "name": "Agra Fort",
                "category": "historical_site",
                "description": "Massive red sandstone fort and UNESCO site. Former Mughal residence with palaces, mosques, and gardens. Great views of Taj Mahal from certain points. Rich history and architecture.",
                "location": {"lat": 27.1795, "lng": 78.0211},
                "tags": ["historical", "unesco", "architectural", "cultural"],
                "best_time": "afternoon",
                "duration": 2,
                "entry_fee": "₹50 (Indians), ₹650 (Foreigners)"
            },
            {
                "name": "Mehtab Bagh (Moonlight Garden)",
                "category": "park",
                "description": "Charbagh garden complex across the Yamuna River from Taj Mahal. Perfect for sunset views and photos of the Taj without crowds. Peaceful atmosphere and well-maintained gardens.",
                "location": {"lat": 27.1833, "lng": 78.0433},
                "tags": ["scenic", "peaceful", "romantic", "photography"],
                "best_time": "sunset",
                "duration": 1,
                "entry_fee": "₹25 (Indians), ₹300 (Foreigners)"
            },
            {
                "name": "Tomb of Itimad-ud-Daulah (Baby Taj)",
                "category": "historical_site",
                "description": "Beautiful Mughal tomb often called 'Baby Taj'. First tomb in India made entirely of marble with intricate inlay work. Less crowded than Taj Mahal but equally beautiful.",
                "location": {"lat": 27.1858, "lng": 78.0261},
                "tags": ["historical", "peaceful", "architectural", "hidden-gem"],
                "best_time": "morning",
                "duration": 1,
                "entry_fee": "₹30 (Indians), ₹310 (Foreigners)"
            },
            {
                "name": "Fatehpur Sikri",
                "category": "historical_site",
                "description": "Abandoned Mughal city 40km from Agra, UNESCO World Heritage Site. Stunning red sandstone buildings and palaces. Half-day trip from Agra. Hire a guide for full historical context.",
                "location": {"lat": 27.0945, "lng": 77.6661},
                "tags": ["historical", "unesco", "architectural", "off-beaten-path"],
                "best_time": "morning",
                "duration": 3,
                "entry_fee": "₹50 (Indians), ₹610 (Foreigners) + transport"
            },
            {
                "name": "Pind Balluchi Restaurant",
                "category": "restaurant",
                "description": "Popular restaurant serving authentic North Indian and Mughlai cuisine. Traditional village-style decor and live music in evenings. Good vegetarian and non-vegetarian options.",
                "location": {"lat": 27.1767, "lng": 78.0081},
                "tags": ["foodie", "cultural", "family-friendly"],
                "best_time": "dinner",
                "price_range": "moderate",
                "cuisine": "North Indian, Mughlai"
            }
        ]
    }
}

def seed_activities():
    """Load curated tourism activities into database"""
    db = Database(schema='public')
    
    print("🌟 Loading curated tourism seed data...\n")
    
    total_added = 0
    
    for city_name, city_data in SEED_ACTIVITIES.items():
        print(f"📍 Processing {city_name}...")
        
        # Get destination ID
        dest_result = db.client.table('destinations').select('id').eq('name', city_data['destination_name']).execute()
        
        if not dest_result.data:
            print(f"   ⚠️  Destination '{city_data['destination_name']}' not found. Skipping.")
            continue
        
        destination_id = dest_result.data[0]['id']
        city_count = 0
        
        for activity in city_data['activities']:
            try:
                # Check if activity already exists
                existing = db.client.table('activities').select('id').eq('name', activity['name']).eq('destination_id', destination_id).execute()
                
                if existing.data:
                    print(f"   ⏭️  {activity['name']} already exists")
                    continue
                
                # Prepare activity data
                activity_data = {
                    'id': str(uuid.uuid4()),
                    'destination_id': destination_id,
                    'name': activity['name'],
                    'description': activity['description'],
                    'category': activity.get('category', activity.get('activity_type')),
                    'location': activity.get('location', activity.get('coordinates')),
                    'tags': activity.get('tags', activity.get('vibe_tags', [])),
                    'best_time': activity.get('best_time'),
                    'duration': activity.get('duration', activity.get('duration_hours')),
                    'price_range': activity.get('price_range'),
                }
                
                # Insert
                db.client.table('activities').insert(activity_data).execute()
                print(f"   ✅ Added: {activity['name']}")
                city_count += 1
                total_added += 1
                
            except Exception as e:
                print(f"   ❌ Error adding {activity['name']}: {e}")
        
        print(f"   📊 Added {city_count} activities for {city_name}\n")
    
    print(f"🎉 Complete! Added {total_added} total activities across {len(SEED_ACTIVITIES)} cities")
    print(f"\n✨ Test the API:")
    print(f"   curl http://localhost:8000/destinations/{{destination_id}}/activities")

if __name__ == "__main__":
    seed_activities()
