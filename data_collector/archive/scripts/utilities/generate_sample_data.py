"""
Generate Sample POI Data for Thailand
Creates realistic sample data for immediate testing and development
"""

import random
import json
from datetime import datetime
from typing import List, Dict, Any
from utils.database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data for 8 key cities
CITIES_DATA = {
    'Bangkok': {
        'province': 'Bangkok',
        'coords': {'lat': 13.7563, 'lng': 100.5018},
        'temples': ['Wat Phra Kaew', 'Wat Arun', 'Wat Pho', 'Wat Saket', 'Wat Benchamabophit'],
        'markets': ['Chatuchak Weekend Market', 'Damnoen Saduak Floating Market', 'Khlong Lat Mayom', 'Or Tor Kor Market'],
        'museums': ['Grand Palace', 'National Museum', 'Jim Thompson House', 'Museum of Siam'],
        'restaurants': ['Nahm', 'Gaggan', 'Bo.Lan', 'Paste Bangkok', 'Sorn'],
        'hotels': ['Mandarin Oriental', 'The Peninsula', 'Shangri-La', 'Anantara Siam'],
    },
    'Chiang Mai': {
        'province': 'Chiang Mai',
        'coords': {'lat': 18.7883, 'lng': 98.9853},
        'temples': ['Wat Phra That Doi Suthep', 'Wat Chedi Luang', 'Wat Phra Singh', 'Wat Umong'],
        'markets': ['Night Bazaar', 'Sunday Walking Street', 'Warorot Market'],
        'museums': ['Chiang Mai National Museum', 'Lanna Folklife Museum'],
        'restaurants': ['Khao Soi Khun Yai', 'Huen Phen', 'SP Chicken', 'Tong Tem Toh'],
        'viewpoints': ['Doi Suthep Viewpoint', 'Huay Tung Tao Lake'],
        'waterfalls': ['Huay Kaew Waterfall', 'Bua Thong Sticky Waterfall'],
    },
    'Phuket': {
        'province': 'Phuket',
        'coords': {'lat': 7.8804, 'lng': 98.3923},
        'beaches': ['Patong Beach', 'Kata Beach', 'Karon Beach', 'Kamala Beach', 'Surin Beach'],
        'viewpoints': ['Promthep Cape', 'Karon Viewpoint', 'Big Buddha'],
        'temples': ['Wat Chalong', 'Big Buddha Temple'],
        'restaurants': ['Mom Tri\'s Kitchen', 'Baan Rim Pa', 'La Gritta'],
        'hotels': ['Amanpuri', 'The Surin', 'Trisara', 'Sri Panwa'],
        'islands': ['Phi Phi Islands', 'James Bond Island', 'Coral Island'],
    },
    'Pattaya': {
        'province': 'Chonburi',
        'coords': {'lat': 12.9236, 'lng': 100.8825},
        'beaches': ['Pattaya Beach', 'Jomtien Beach', 'Naklua Beach'],
        'viewpoints': ['Pattaya Viewpoint', 'Khao Pattaya View Point'],
        'temples': ['Sanctuary of Truth', 'Wat Phra Yai (Big Buddha)'],
        'restaurants': ['Mantra Restaurant', 'The Glass House', 'Cabbages & Condoms'],
        'hotels': ['Hilton Pattaya', 'InterContinental Pattaya', 'Royal Cliff'],
    },
    'Krabi': {
        'province': 'Krabi',
        'coords': {'lat': 8.0863, 'lng': 98.9063},
        'beaches': ['Railay Beach', 'Ao Nang Beach', 'Phra Nang Beach'],
        'viewpoints': ['Tiger Cave Temple Viewpoint', 'Tab Kak Hang Nak Hill'],
        'temples': ['Tiger Cave Temple', 'Wat Tham Sua'],
        'islands': ['Koh Phi Phi', 'Koh Lanta', 'Hong Islands', 'Four Islands'],
        'restaurants': ['Lae Lay Grill', 'Krua Thara', 'Carnivore Steak'],
    },
    'Ayutthaya': {
        'province': 'Phra Nakhon Si Ayutthaya',
        'coords': {'lat': 14.3532, 'lng': 100.5676},
        'temples': ['Wat Mahathat', 'Wat Phra Si Sanphet', 'Wat Chaiwatthanaram', 'Wat Ratchaburana'],
        'museums': ['Ayutthaya Historical Study Centre', 'Chao Sam Phraya National Museum'],
        'markets': ['Ayutthaya Floating Market', 'Night Market'],
        'restaurants': ['Baan Kao Nhom', 'Pae Krung Kao', 'Roti Sai Mai Stalls'],
    },
    'Koh Samui': {
        'province': 'Surat Thani',
        'coords': {'lat': 9.5004, 'lng': 100.0004},
        'beaches': ['Chaweng Beach', 'Lamai Beach', 'Bophut Beach', 'Maenam Beach'],
        'viewpoints': ['Lad Koh Viewpoint', 'Khao Hua Jook Viewpoint'],
        'temples': ['Big Buddha Temple', 'Wat Plai Laem'],
        'waterfalls': ['Na Muang Waterfall', 'Hin Lad Waterfall'],
        'hotels': ['Six Senses Samui', 'Four Seasons', 'Conrad Koh Samui'],
        'restaurants': ['The Cliff Bar & Grill', 'Zazen Restaurant', 'Prego'],
    },
    'Hua Hin': {
        'province': 'Prachuap Khiri Khan',
        'coords': {'lat': 12.5683, 'lng': 99.9578},
        'beaches': ['Hua Hin Beach', 'Khao Takiab Beach', 'Suan Son Beach'],
        'viewpoints': ['Khao Hin Lek Fai Viewpoint', 'Phraya Nakhon Cave'],
        'temples': ['Wat Huay Mongkol', 'Wat Khao Takiab'],
        'markets': ['Cicada Market', 'Hua Hin Night Market'],
        'restaurants': ['Baan Itsara', 'Hua Hin Koti', 'Oceanside Beach Club'],
        'hotels': ['Centara Grand', 'InterContinental Hua Hin', 'Anantara Hua Hin'],
    },
}

POI_TYPE_MAPPING = {
    'temples': 'temple',
    'beaches': 'beach',
    'markets': 'market',
    'restaurants': 'restaurant',
    'museums': 'museum',
    'viewpoints': 'viewpoint',
    'waterfalls': 'waterfall',
    'hotels': 'hotel',
    'islands': 'island',
}

def generate_persona_scores(poi_type: str) -> Dict[str, int]:
    """Generate realistic persona scores based on POI type"""
    base_scores = {
        'temple': {'cultural_explorer': 95, 'adventure_seeker': 40, 'beach_lover': 30, 'luxury_traveler': 50, 'culinary_enthusiast': 35, 'wellness_retreater': 75},
        'beach': {'cultural_explorer': 35, 'adventure_seeker': 70, 'beach_lover': 95, 'luxury_traveler': 80, 'culinary_enthusiast': 40, 'wellness_retreater': 85},
        'market': {'cultural_explorer': 80, 'adventure_seeker': 50, 'beach_lover': 40, 'luxury_traveler': 45, 'culinary_enthusiast': 90, 'wellness_retreater': 35},
        'restaurant': {'cultural_explorer': 60, 'adventure_seeker': 45, 'beach_lover': 50, 'luxury_traveler': 85, 'culinary_enthusiast': 95, 'wellness_retreater': 55},
        'museum': {'cultural_explorer': 95, 'adventure_seeker': 35, 'beach_lover': 25, 'luxury_traveler': 60, 'culinary_enthusiast': 40, 'wellness_retreater': 45},
        'viewpoint': {'cultural_explorer': 70, 'adventure_seeker': 85, 'beach_lover': 75, 'luxury_traveler': 65, 'culinary_enthusiast': 45, 'wellness_retreater': 80},
        'waterfall': {'cultural_explorer': 55, 'adventure_seeker': 90, 'beach_lover': 60, 'luxury_traveler': 50, 'culinary_enthusiast': 35, 'wellness_retreater': 75},
        'hotel': {'cultural_explorer': 45, 'adventure_seeker': 40, 'beach_lover': 70, 'luxury_traveler': 95, 'culinary_enthusiast': 60, 'wellness_retreater': 80},
        'island': {'cultural_explorer': 50, 'adventure_seeker': 80, 'beach_lover': 95, 'luxury_traveler': 85, 'culinary_enthusiast': 55, 'wellness_retreater': 90},
    }
    
    scores = base_scores.get(poi_type, {k: 50 for k in base_scores['temple'].keys()})
    # Add some randomness
    return {k: max(0, min(100, v + random.randint(-10, 10))) for k, v in scores.items()}

def generate_sample_pois() -> List[Dict[str, Any]]:
    """Generate sample POIs for all cities"""
    pois = []
    poi_id = 1
    
    for city_name, city_data in CITIES_DATA.items():
        logger.info(f"Generating POIs for {city_name}...")
        
        base_lat = city_data['coords']['lat']
        base_lng = city_data['coords']['lng']
        
        for category, poi_names in city_data.items():
            if category in ['province', 'coords']:
                continue
            
            poi_type = POI_TYPE_MAPPING.get(category)
            if not poi_type:
                continue
            
            for poi_name in poi_names:
                # Generate slightly randomized coordinates around the city center
                lat = base_lat + random.uniform(-0.05, 0.05)
                lng = base_lng + random.uniform(-0.05, 0.05)
                
                poi = {
                    'name': poi_name,
                    'name_local': None,  # Would need Thai translation
                    'poi_type': poi_type,
                    'coordinates': {'lat': lat, 'lng': lng},
                    'city_name': city_name,
                    'province_name': city_data['province'],
                    'country_code': 'TH',
                    'description': f"A popular {poi_type} in {city_name}, Thailand.",
                    'persona_scores': generate_persona_scores(poi_type),
                    'osm_id': f"sample_{poi_id}",
                    'osm_type': 'node',
                    'data_sources': ['sample_data'],
                    'metadata': {
                        'generated': True,
                        'generated_at': datetime.now().isoformat()
                    }
                }
                
                pois.append(poi)
                poi_id += 1
        
        logger.info(f"  Generated {len([p for p in pois if p['city_name'] == city_name])} POIs for {city_name}")
    
    return pois

def main():
    """Generate and save sample data"""
    logger.info("="*60)
    logger.info("Generating Sample POI Data for Thailand")
    logger.info("="*60)
    
    # Generate POIs
    pois = generate_sample_pois()
    
    logger.info(f"\n✅ Generated {len(pois)} sample POIs")
    logger.info(f"   Cities: {len(CITIES_DATA)}")
    logger.info(f"   POI Types: {len(set(p['poi_type'] for p in pois))}")
    
    # Save to database
    logger.info("\n💾 Saving to database...")
    
    # Save to JSON file first (backup)
    logger.info("📄 Creating JSON backup...")
    with open('sample_pois.json', 'w', encoding='utf-8') as f:
        json.dump(pois, f, indent=2, ensure_ascii=False)
    logger.info("✅ Saved to sample_pois.json")
    
    # Try to save to database
    try:
        # Try trip_pois table first (your existing table)
        logger.info("Attempting to save to trip_pois table...")
        result = db.client.table('trip_pois').insert([{
            'name': poi['name'],
            'poi_type': poi['poi_type'],
            'coordinates': poi['coordinates'],
            'description': poi.get('description'),
            'metadata': poi.get('metadata', {})
        } for poi in pois]).execute()
        
        saved_count = len(result.data) if result.data else 0
        logger.info(f"✅ Saved {saved_count} POIs to trip_pois table!")
        
    except Exception as e:
        logger.warning(f"⚠️  Could not save to database: {e}")
        logger.info("💡 No problem! Use the JSON file (sample_pois.json) instead")
        logger.info("   You can import it manually or use it for testing")
        saved_count = 0
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("Summary by City:")
    logger.info("="*60)
    for city_name in CITIES_DATA.keys():
        city_pois = [p for p in pois if p['city_name'] == city_name]
        logger.info(f"{city_name:15} {len(city_pois):3} POIs")
    
    logger.info("\n" + "="*60)
    logger.info("Summary by Type:")
    logger.info("="*60)
    for poi_type in set(p['poi_type'] for p in pois):
        type_pois = [p for p in pois if p['poi_type'] == poi_type]
        logger.info(f"{poi_type:15} {len(type_pois):3} POIs")
    
    logger.info("\n" + "="*60)
    logger.info("🎉 Sample data generation complete!")
    logger.info("="*60)
    logger.info("\nYou can now:")
    logger.info("  1. Test your frontend with real-looking data")
    logger.info("  2. Develop features without waiting for OSM")
    logger.info("  3. Replace with real data later when OSM is available")

if __name__ == "__main__":
    main()
