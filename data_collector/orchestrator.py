import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Orchestrator")

class Orchestrator:
    """
    Manages the ETL pipeline execution and state.
    """
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.layers_dir = self.base_dir / "layers"
        self.bronze_dir = self.layers_dir / "bronze"
        self.silver_dir = self.layers_dir / "silver"
        self.gold_dir = self.layers_dir / "gold"
        
        # Ensure directories exist
        for d in [self.bronze_dir, self.silver_dir, self.gold_dir]:
            d.mkdir(parents=True, exist_ok=True)
            
    def get_pipeline_status(self) -> Dict:
        """Returns the current status of the pipeline layers."""
        status = {
            "bronze": self._count_files(self.bronze_dir),
            "silver": self._count_files(self.silver_dir),
            "gold": self._count_files(self.gold_dir),
            "last_run": datetime.now().isoformat() # Placeholder
        }
        return status

    def _count_files(self, directory: Path) -> int:
        """Counts files in a directory recursively."""
        return sum(1 for _ in directory.rglob('*') if _.is_file())

    def run_bronze_layer(self, city: str):
        """Trigger Bronze Layer extraction."""
        logger.info(f"Starting Bronze Layer extraction for {city}...")
        from etl.extract.osm_extractor import OSMExtractor
        extractor = OSMExtractor(self.bronze_dir)
        extractor.extract_city(city)

    def run_silver_layer(self, city: str):
        """Trigger Silver Layer transformation."""
        logger.info(f"Starting Silver Layer transformation for {city}...")
        from etl.transform.standardizer import Standardizer
        standardizer = Standardizer(self.bronze_dir, self.silver_dir)
        standardizer.process_city(city)

    def run_gold_layer(self, city_name: str):
        """
        Runs Gold Layer:
        1. POI Enrichment (AIEnricher)
        2. Destination Enrichment (DestinationEnricher)
        """
        logger.info(f"Starting Gold Layer enrichment for {city_name}...")
        
        # 1. POI Enrichment
        from etl.enrich.ai_enricher import AIEnricher
        poi_enricher = AIEnricher(self.silver_dir, self.gold_dir)
        poi_enricher.process_city(city_name)
        
        # 2. Destination Enrichment
        from etl.enrich.destination_enricher import DestinationEnricher
        dest_enricher = DestinationEnricher(self.gold_dir)
        dest_enricher.enrich_destination(city_name)
        
        logger.info(f"✅ Gold Layer (POI + Destination) complete for {city_name}")

    def run_load_layer(self, city_name: str):
        """Trigger Loading to Supabase."""
        logger.info(f"Starting Load Layer for {city_name}...") # Changed `city` to `city_name`
        from etl.load.supabase_loader import SupabaseLoader
        loader = SupabaseLoader(self.gold_dir)
        loader.load_gold_layer(city_name)
