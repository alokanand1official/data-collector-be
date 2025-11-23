"""
Thailand Cities Data Collection Script
Collects POIs from 8 key tourist destinations
Fast, focused, and avoids rate limits!
"""

import os
import sys
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from sources.osm import OSMCollector
from utils.database import db
from utils.llm import LocalLLM

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/cities_collection_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Key tourist cities with their bounding boxes
CITIES = [
    {
        'name': 'Bangkok',
        'name_local': 'กรุงเทพมหานคร',
        'province': 'Bangkok',
        'priority': 1,
        'bbox': {
            'north': 13.95,
            'south': 13.50,
            'east': 100.90,
            'west': 100.30
        },
        'description': 'Capital city, cultural hub, major tourist destination'
    },
    {
        'name': 'Chiang Mai',
        'name_local': 'เชียงใหม่',
        'province': 'Chiang Mai',
        'priority': 2,
        'bbox': {
            'north': 18.85,
            'south': 18.70,
            'east': 99.05,
            'west': 98.90
        },
        'description': 'Northern cultural capital, temples, mountains'
    },
    {
        'name': 'Phuket',
        'name_local': 'ภูเก็ต',
        'province': 'Phuket',
        'priority': 3,
        'bbox': {
            'north': 8.20,
            'south': 7.75,
            'east': 98.45,
            'west': 98.25
        },
        'description': 'Island paradise, beaches, resorts'
    },
    {
        'name': 'Pattaya',
        'name_local': 'พัทยา',
        'province': 'Chonburi',
        'priority': 4,
        'bbox': {
            'north': 13.00,
            'south': 12.85,
            'east': 100.95,
            'west': 100.85
        },
        'description': 'Beach resort city, nightlife, water sports'
    },
    {
        'name': 'Krabi',
        'name_local': 'กระบี่',
        'province': 'Krabi',
        'priority': 5,
        'bbox': {
            'north': 8.15,
            'south': 7.95,
            'east': 98.95,
            'west': 98.85
        },
        'description': 'Limestone cliffs, islands, beaches'
    },
    {
        'name': 'Ayutthaya',
        'name_local': 'พระนครศรีอยุธยา',
        'province': 'Phra Nakhon Si Ayutthaya',
        'priority': 6,
        'bbox': {
            'north': 14.40,
            'south': 14.30,
            'east': 100.60,
            'west': 100.50
        },
        'description': 'Ancient capital, UNESCO World Heritage, temples'
    },
    {
        'name': 'Koh Samui',
        'name_local': 'เกาะสมุย',
        'province': 'Surat Thani',
        'priority': 7,
        'bbox': {
            'north': 9.60,
            'south': 9.45,
            'east': 100.10,
            'west': 99.95
        },
        'description': 'Tropical island, luxury resorts, beaches'
    },
    {
        'name': 'Hua Hin',
        'name_local': 'หัวหิน',
        'province': 'Prachuap Khiri Khan',
        'priority': 8,
        'bbox': {
            'north': 12.65,
            'south': 12.50,
            'east': 99.98,
            'west': 99.90
        },
        'description': 'Royal beach resort, golf, seafood'
    },
]


def collect_city_pois(
    city: Dict,
    poi_types: List[str],
    osm_collector: OSMCollector,
    llm: LocalLLM = None
) -> int:
    """Collect all POIs for a city"""
    
    city_name = city['name']
    bbox = city['bbox']
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Collecting data for {city_name}")
    logger.info(f"Province: {city['province']}")
    logger.info(f"BBox: {bbox}")
    logger.info(f"{'='*60}")
    
    total_collected = 0
    
    for poi_type in poi_types:
        logger.info(f"\nCollecting {poi_type}s in {city_name}...")
        
        try:
            # Collect from OSM
            pois = osm_collector.collect_pois_in_bounding_box(
                bbox=bbox,
                poi_type=poi_type,
                limit=200  # Reasonable limit per city
            )
            
            if not pois:
                logger.info(f"  No {poi_type}s found")
                continue
            
            logger.info(f"  ✅ Found {len(pois)} {poi_type}s")
            
            # Add city and province info to each POI
            for poi in pois:
                poi['city_name'] = city_name
                poi['province_name'] = city['province']
                poi['country_code'] = 'TH'
            
            # Enrich with LLM if available
            if llm and len(pois) <= 50:  # Only enrich if reasonable number
                logger.info(f"  🤖 Enriching {len(pois)} POIs with AI...")
                enriched_count = 0
                
                for poi in pois:
                    try:
                        # Score for personas
                        personas = [
                            {'id': 'cultural_explorer', 'keywords': ['temple', 'museum', 'historical', 'cultural']},
                            {'id': 'adventure_seeker', 'keywords': ['hiking', 'adventure', 'mountain', 'sports']},
                            {'id': 'beach_lover', 'keywords': ['beach', 'ocean', 'island', 'coastal']},
                            {'id': 'luxury_traveler', 'keywords': ['luxury', 'spa', 'resort', 'fine dining']},
                            {'id': 'culinary_enthusiast', 'keywords': ['food', 'restaurant', 'market', 'cuisine']},
                            {'id': 'wellness_retreater', 'keywords': ['meditation', 'yoga', 'wellness', 'peaceful']},
                        ]
                        
                        scores = llm.score_poi_for_personas(poi, personas)
                        poi['persona_scores'] = scores
                        enriched_count += 1
                        
                    except Exception as e:
                        logger.debug(f"Error enriching POI {poi.get('name')}: {e}")
                        poi['persona_scores'] = {}
                
                logger.info(f"  ✅ Enriched {enriched_count}/{len(pois)} POIs")
            elif len(pois) > 50:
                logger.info(f"  ⏭️  Skipping AI enrichment (too many POIs, will do in batch later)")
                for poi in pois:
                    poi['persona_scores'] = {}
            
            # Save to database
            saved_count = db.save_pois(pois)
            total_collected += saved_count
            
            logger.info(f"  💾 Saved {saved_count} {poi_type}s to database")
            
            # Rate limiting - be nice to OSM!
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"  ❌ Error collecting {poi_type}s: {e}")
            continue
    
    logger.info(f"\n📊 Total POIs collected for {city_name}: {total_collected}")
    return total_collected


def main():
    """Main collection process"""
    
    logger.info("\n" + "="*60)
    logger.info("🇹🇭 Thailand Cities Data Collection - Starting")
    logger.info("="*60 + "\n")
    
    logger.info(f"Will collect from {len(CITIES)} key tourist cities:")
    for city in CITIES:
        logger.info(f"  {city['priority']}. {city['name']} ({city['name_local']}) - {city['description']}")
    
    # Initialize collectors
    logger.info("\n🔧 Initializing collectors...")
    osm_collector = OSMCollector(rate_limit_delay=3.0)  # 3 seconds between requests
    
    # Initialize LLM (optional)
    llm = None
    try:
        llm = LocalLLM(model="llama3.1:8b")
        logger.info("✅ LLM initialized for AI enrichment")
    except Exception as e:
        logger.warning(f"⚠️  LLM not available: {e}")
        logger.warning("Continuing without AI enrichment...")
    
    # POI types to collect
    poi_types = [
        'temple',
        'beach',
        'market',
        'restaurant',
        'museum',
        'viewpoint',
        'waterfall',
        'hotel',
        'island',
    ]
    
    logger.info(f"\n📍 Will collect {len(poi_types)} POI types:")
    logger.info(f"   {', '.join(poi_types)}")
    
    # Statistics
    total_cities = len(CITIES)
    processed_cities = 0
    total_pois = 0
    start_time = datetime.now()
    
    # Process each city
    for i, city in enumerate(CITIES, 1):
        logger.info(f"\n\n{'='*60}")
        logger.info(f"🏙️  City {i}/{total_cities}: {city['name']}")
        logger.info(f"{'='*60}")
        
        try:
            pois_collected = collect_city_pois(
                city=city,
                poi_types=poi_types,
                osm_collector=osm_collector,
                llm=llm
            )
            
            total_pois += pois_collected
            processed_cities += 1
            
            # Progress update
            elapsed = (datetime.now() - start_time).total_seconds()
            avg_time_per_city = elapsed / processed_cities
            remaining_cities = total_cities - processed_cities
            estimated_remaining = avg_time_per_city * remaining_cities
            
            logger.info(f"\n📊 Overall Progress:")
            logger.info(f"  Cities: {processed_cities}/{total_cities} ({processed_cities/total_cities*100:.1f}%)")
            logger.info(f"  Total POIs: {total_pois:,}")
            logger.info(f"  Avg POIs/city: {total_pois/processed_cities:.0f}")
            logger.info(f"  Time elapsed: {elapsed/3600:.2f} hours")
            logger.info(f"  Estimated remaining: {estimated_remaining/3600:.2f} hours")
            logger.info(f"  Collection rate: {total_pois/elapsed*3600:.0f} POIs/hour")
            
        except Exception as e:
            logger.error(f"❌ Failed to process city {city['name']}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Final summary
    duration = (datetime.now() - start_time).total_seconds()
    
    logger.info("\n\n" + "="*60)
    logger.info("🎉 Thailand Cities Data Collection - Complete!")
    logger.info("="*60)
    logger.info(f"Cities processed: {processed_cities}/{total_cities}")
    logger.info(f"Total POIs collected: {total_pois:,}")
    logger.info(f"Duration: {duration/3600:.2f} hours")
    logger.info(f"Average: {total_pois/duration*3600:.0f} POIs/hour")
    logger.info(f"Avg POIs per city: {total_pois/processed_cities:.0f}")
    logger.info("="*60 + "\n")
    
    logger.info("✅ Data is now available in your Supabase database!")
    logger.info("   Check the 'pois' table to see your collected data.")


if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    Path('logs').mkdir(exist_ok=True)
    
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Collection interrupted by user")
        logger.info("Progress has been saved to database")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
