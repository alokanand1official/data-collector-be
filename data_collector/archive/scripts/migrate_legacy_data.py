import os
import json
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Migration")

BASE_DIR = Path(".")
PROCESSED_DIR = BASE_DIR / "processed_data"
SILVER_DIR = BASE_DIR / "layers" / "silver"

def migrate_legacy_data():
    """
    Migrates legacy processed JSONs to Silver Layer.
    """
    if not PROCESSED_DIR.exists():
        logger.error("No processed_data directory found.")
        return

    for file_path in PROCESSED_DIR.glob("*_pois.json"):
        city_name = file_path.stem.replace("_pois", "")
        logger.info(f"Migrating {city_name}...")
        
        # Create Silver directory
        city_silver_dir = SILVER_DIR / city_name
        city_silver_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        dest_file = city_silver_dir / "pois.json"
        shutil.copy2(file_path, dest_file)
        
        # Create dummy metadata
        metadata = {
            "city": city_name,
            "source": "legacy_migration",
            "migrated_at": "2025-11-23T22:00:00"
        }
        with open(city_silver_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"✅ Migrated {city_name} to Silver Layer")

if __name__ == "__main__":
    migrate_legacy_data()
