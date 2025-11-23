import logging
import sys
import os
import time

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import Orchestrator

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline_enrichment_run.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EnrichmentRunner")

GEORGIA_CITIES = [
    "Tbilisi",
    "Batumi",
    "Kazbegi",
    "Mtskheta",
    "Sighnaghi",
    "Kutaisi"
]

def run_enrichment_load():
    orch = Orchestrator()
    
    logger.info("🚀 Starting Enrichment & Load Pipeline for Georgia (Remaining Cities)")
    
    for city in GEORGIA_CITIES:
        logger.info(f"\n{'='*50}\nProcessing {city}...\n{'='*50}")
        
        try:
            # 3. Gold Layer (Enrich)
            logger.info(f"Step 1: Gold Layer (Enrich) for {city}")
            orch.run_gold_layer(city)
            
            # 4. Load Layer (Supabase)
            logger.info(f"Step 2: Load Layer (Supabase) for {city}")
            orch.run_load_layer(city)
            
            logger.info(f"✅ Successfully processed {city}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process {city}: {e}")
            continue
            
    logger.info("\n🎉 Enrichment & Load Run Complete!")

if __name__ == "__main__":
    run_enrichment_load()
