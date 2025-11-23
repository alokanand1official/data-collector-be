"""
Thailand Data Collection Script
Collects POIs from all 77 provinces in Thailand
"""

import os
import sys
import logging
import time
import yaml
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
        logging.FileHandler(f'logs/thailand_collection_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config() -> Dict:
    """Load Thailand configuration"""
    config_path = Path('config/countries/thailand.yaml')
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        full_config = yaml.safe_load(f)
    
    # Extract country config
    config = full_config.get('country', {})
    
    # Add other top-level configs
    config['data_types'] = full_config.get('data_types', {})
    config['data_sources'] = full_config.get('data_sources', {})
    config['quality'] = full_config.get('quality', {})
    config['llm'] = full_config.get('llm', {})
    config['personas'] = full_config.get('personas', [])
    
    logger.info(f"Loaded config for {config.get('name', 'Unknown')}")
    return config


def collect_province_pois(
    province: Dict,
    poi_types: List[str],
    osm_collector: OSMCollector,
    country_bbox: Dict,
    llm: LocalLLM = None
) -> int:
    """Collect all POIs for a province using bounding box"""
    
    province_name = province['name']
    logger.info(f"\n{'='*60}")
    logger.info(f"Collecting data for {province_name}")
    logger.info(f"{'='*60}")
    
    # For now, use a smaller bbox around the province
    # TODO: Add province-specific bounding boxes to config
    logger.warning(f"Using country-wide bounding box for {province_name}")
    logger.warning("For better results, add province-specific bounding boxes to config")
    
    total_collected = 0
    
    for poi_type in poi_types:
        logger.info(f"Collecting {poi_type}s in {province_name}...")
        
        try:
            # Collect from OSM using bounding box
            pois = osm_collector.collect_pois_in_bounding_box(
                bbox=country_bbox,
                poi_type=poi_type,
                limit=100  # Limit to avoid overwhelming the system
            )
            
            if not pois:
                logger.info(f"No {poi_type}s found")
                continue
            
            logger.info(f"Found {len(pois)} {poi_type}s")
            
            # Add province info to each POI
            for poi in pois:
                poi['province_name'] = province_name
                poi['country_code'] = 'TH'
            
            # Enrich with LLM if available
            if llm:
                logger.info("Enriching POIs with AI...")
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
                        
                    except Exception as e:
                        logger.warning(f"Error enriching POI {poi.get('name')}: {e}")
                        poi['persona_scores'] = {}
            
            # Save to database
            saved_count = db.save_pois(pois)
            total_collected += saved_count
            
            logger.info(f"Saved {saved_count} {poi_type}s to database")
            
            # Rate limiting
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error collecting {poi_type}s: {e}")
            continue
    
    logger.info(f"Total POIs collected for {province_name}: {total_collected}")
    return total_collected


def main():
    """Main collection process"""
    
    logger.info("\n" + "="*60)
    logger.info("Thailand Data Collection - Starting")
    logger.info("="*60 + "\n")
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)
    
    # Initialize collectors
    logger.info("Initializing collectors...")
    osm_collector = OSMCollector(rate_limit_delay=2.0)
    
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
        'national_park',
        'island',
        'hotel'
    ]
    
    logger.info(f"Will collect {len(poi_types)} POI types: {', '.join(poi_types)}")
    
    # Get provinces from config
    provinces = []
    for region in config.get('regions', []):
        provinces.extend(region.get('provinces', []))
    
    logger.info(f"Found {len(provinces)} provinces to process")
    
    # Get bounding box from config
    country_bbox = config.get('bounding_box', {})
    logger.info(f"Using bounding box: {country_bbox}")
    
    # Statistics
    total_provinces = len(provinces)
    processed_provinces = 0
    total_pois = 0
    start_time = datetime.now()
    
    # Process each province
    for i, province in enumerate(provinces, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"Province {i}/{total_provinces}: {province['name']}")
        logger.info(f"{'='*60}")
        
        try:
            pois_collected = collect_province_pois(
                province=province,
                poi_types=poi_types,
                osm_collector=osm_collector,
                country_bbox=country_bbox,
                llm=llm
            )
            
            total_pois += pois_collected
            processed_provinces += 1
            
            # Progress update
            elapsed = (datetime.now() - start_time).total_seconds()
            avg_time_per_province = elapsed / processed_provinces
            remaining_provinces = total_provinces - processed_provinces
            estimated_remaining = avg_time_per_province * remaining_provinces
            
            logger.info(f"\n📊 Progress Update:")
            logger.info(f"  Provinces: {processed_provinces}/{total_provinces} ({processed_provinces/total_provinces*100:.1f}%)")
            logger.info(f"  Total POIs: {total_pois}")
            logger.info(f"  Avg POIs/province: {total_pois/processed_provinces:.1f}")
            logger.info(f"  Estimated time remaining: {estimated_remaining/3600:.1f} hours")
            
        except Exception as e:
            logger.error(f"Failed to process province {province['name']}: {e}")
            continue
    
    # Final summary
    duration = (datetime.now() - start_time).total_seconds()
    
    logger.info("\n" + "="*60)
    logger.info("Thailand Data Collection - Complete!")
    logger.info("="*60)
    logger.info(f"Provinces processed: {processed_provinces}/{total_provinces}")
    logger.info(f"Total POIs collected: {total_pois}")
    logger.info(f"Duration: {duration/3600:.2f} hours")
    logger.info(f"Average: {total_pois/duration*3600:.1f} POIs/hour")
    logger.info("="*60 + "\n")


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
