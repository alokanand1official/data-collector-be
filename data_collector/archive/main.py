import argparse
import logging
import sys
from typing import Dict

from pipeline.harvester import Harvester
from pipeline.processor import Processor
from pipeline.enricher import Enricher
from pipeline.loader import Loader

from config.cities_config import CITIES

# City Configurations are now imported from config.cities_config

def get_city_config(city_key: str) -> Dict:
    key = city_key.lower().replace(" ", "_")
    if key in CITIES:
        return CITIES[key]
    
    # Try to find by name
    for k, v in CITIES.items():
        if v['name'].lower() == city_key.lower():
            return v
    return None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Robust Data Collection Pipeline")
    parser.add_argument('action', choices=['harvest', 'process', 'enrich', 'load', 'promote', 'destinations', 'all'], help='Action to perform')
    parser.add_argument('--city', required=True, help='City name (e.g., Bangkok) or "all"')
    parser.add_argument('--country', help='Country filter (e.g., India) - only used with --city "all"')
    parser.add_argument('--limit', type=int, default=10, help='Limit for enrichment (default 10)')
    parser.add_argument('--tier', choices=['essential', 'important', 'recommended'], help='Priority tier to enrich (requires prioritized POIs)')
    
    args = parser.parse_args()
    
    # Special handling for 'destinations' and 'promote' which have their own 'all' logic
    if args.action == 'destinations':
        from collect_destinations import DestinationCollector
        collector = DestinationCollector()
        if args.city.lower() == 'all':
            collector.collect_all()
        else:
            city_config = get_city_config(args.city)
            if not city_config:
                logger.error(f"City '{args.city}' not found.")
                sys.exit(1)
            collector.collect_city(city_config['name'])
        return

    if args.action == 'promote':
        from pipeline.deployer import Deployer
        deployer = Deployer()
        deployer.deploy_all() # Deployer handles everything
        return

    # For other actions (harvest, process, enrich, load), handle batching
    target_cities = []
    if args.city.lower() == 'all':
        for key, config in CITIES.items():
            if args.country and config['country'].lower() != args.country.lower():
                continue
            # For harvest, skip if no bbox
            if args.action in ['harvest', 'all'] and not config['bbox']:
                logger.warning(f"Skipping {config['name']} (No BBox)")
                continue
            target_cities.append(config)
    else:
        city_config = get_city_config(args.city)
        if not city_config:
            logger.error(f"City '{args.city}' not found in configuration.")
            logger.info("Available cities: " + ", ".join([c['name'] for c in CITIES.values()]))
            sys.exit(1)
        target_cities.append(city_config)

    logger.info(f"Targeting {len(target_cities)} cities: {[c['name'] for c in target_cities]}")

    for config in target_cities:
        city_name = config['name']
        logger.info(f"--- Processing {city_name} ---")

        if args.action in ['harvest', 'all']:
            harvester = Harvester()
            harvester.harvest_city(city_name, config['bbox'])
            
        if args.action in ['process', 'all']:
            processor = Processor()
            processor.process_city(city_name)

        if args.action in ['enrich', 'all']:
            print(f"DEBUG: Initializing Enricher for {city_name}...")
            try:
                enricher = Enricher()
                enricher.enrich_city(city_name, limit=args.limit, tier=args.tier)
            except Exception as e:
                print(f"DEBUG: Error in enrichment for {city_name}: {e}")
                import traceback
                traceback.print_exc()
            
        if args.action in ['load', 'all']:
            loader = Loader()
            loader.load_city(city_name)

if __name__ == "__main__":
    main()
