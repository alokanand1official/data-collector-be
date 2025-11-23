import pandas as pd
import json
import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger("CSVStandardizer")

class CSVStandardizer:
    """
    Standardizes CSV uploads into the Silver Layer schema.
    """
    
    def __init__(self, silver_dir: Path):
        self.silver_dir = silver_dir
        
    def process_csv(self, file_path: Path, city_name: str) -> bool:
        """
        Reads a CSV file, maps columns, and saves to Silver Layer.
        """
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded CSV with {len(df)} rows")
            
            # Normalize columns
            df.columns = [c.lower().strip() for c in df.columns]
            
            pois = []
            for _, row in df.iterrows():
                # Flexible column mapping
                name = row.get('name') or row.get('title') or row.get('place_name')
                if not name:
                    continue
                    
                lat = row.get('lat') or row.get('latitude') or row.get('y')
                lon = row.get('lon') or row.get('lng') or row.get('longitude') or row.get('x')
                
                if pd.isna(lat) or pd.isna(lon):
                    continue
                    
                category = row.get('category') or row.get('type') or 'unknown'
                description = row.get('description') or row.get('desc') or None
                
                poi = {
                    "name": name,
                    "category": category,
                    "coordinates": {"lat": float(lat), "lng": float(lon)},
                    "description": description,
                    "tags": {"source": "csv_upload"},
                    "osm_id": f"csv_{pd.Timestamp.now().strftime('%Y%m%d')}_{_}",
                    "priority_score": 100, # Assume uploaded data is important
                    "is_manual": True
                }
                pois.append(poi)
                
            if not pois:
                logger.warning("No valid POIs found in CSV")
                return False
                
            # Save to Silver Layer (merge with manual_pois.json or create new csv_pois.json)
            # We'll use a separate file 'csv_pois.json' and update AIEnricher to read it too
            city_key = city_name.lower().replace(" ", "_")
            output_dir = self.silver_dir / city_key
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / "csv_pois.json"
            
            # Merge with existing CSV POIs if any
            if output_file.exists():
                with open(output_file, 'r') as f:
                    existing = json.load(f)
                pois.extend(existing)
                
            with open(output_file, 'w') as f:
                json.dump(pois, f, indent=2)
                
            logger.info(f"✅ Saved {len(pois)} POIs from CSV to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process CSV: {e}")
            return False
