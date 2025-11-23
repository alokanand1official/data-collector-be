import logging
import sys
import os
import time
from pathlib import Path

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import Orchestrator

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline_run.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PipelineRunner")

GEORGIA_CITIES = [
    "Tbilisi",
    "Batumi",
    "Kazbegi",
    "Mtskheta",
    "Sighnaghi",
    "Kutaisi"
]

def run_pipeline():
    orch = Orchestrator()
    
    logger.info("🚀 Starting Production Pipeline Run for Georgia")
    
    for city in GEORGIA_CITIES:
        logger.info(f"\n{'='*50}\nProcessing {city}...\n{'='*50}")
        
        try:
            # 1. Bronze Layer (Harvest)
            logger.info(f"Step 1: Bronze Layer (Harvest) for {city}")
            orch.run_bronze_layer(city)
            time.sleep(2) # Polite delay
            
            # 2. Silver Layer (Transform)
            logger.info(f"Step 2: Silver Layer (Transform) for {city}")
            orch.run_silver_layer(city)
            
            # 3. Gold Layer (Enrich)
            logger.info(f"Step 3: Gold Layer (Enrich) for {city}")
            orch.run_gold_layer(city)
            
            # 4. Load Layer (Supabase)
            logger.info(f"Step 4: Load Layer (Supabase) for {city}")
            orch.run_load_layer(city)
            
            logger.info(f"✅ Successfully processed {city}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process {city}: {e}")
            continue
            
    logger.info("\n🎉 Pipeline Run Complete!")

if __name__ == "__main__":
    run_pipeline()
