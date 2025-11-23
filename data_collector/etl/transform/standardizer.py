import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Set
import pandas as pd
from datetime import datetime
from etl.transform.data_quality_validator import validate_pois
from etl.transform.name_translator import translate_poi_names

logger = logging.getLogger("Standardizer")

class Standardizer:
    """
    Transforms Bronze data into Silver (Cleaned & Normalized).
    """
    
    def __init__(self, bronze_dir: Path, silver_dir: Path):
        self.bronze_dir = bronze_dir
        self.silver_dir = silver_dir
        
    def process_city(self, city_name: str) -> bool:
        """
        Reads latest Bronze data, cleans it, and saves to Silver.
        """
        city_key = city_name.lower().replace(" ", "_")
        city_bronze_path = self.bronze_dir / city_key
        
        if not city_bronze_path.exists():
            logger.error(f"No Bronze data found for {city_name}")
            return False
            
        # Find latest harvest
        timestamps = sorted([d.name for d in city_bronze_path.iterdir() if d.is_dir()], reverse=True)
        if not timestamps:
            logger.error(f"No harvest directories found for {city_name}")
            return False
            
        latest_harvest = city_bronze_path / timestamps[0]
        logger.info(f"Processing latest harvest: {latest_harvest}")
        
        # Load all tiles
        raw_elements = []
        for tile_file in latest_harvest.glob("tile_*.json"):
            with open(tile_file, 'r') as f:
                data = json.load(f)
                raw_elements.extend(data.get('elements', []))
                
        logger.info(f"Loaded {len(raw_elements)} raw elements")
        
        # Transform
        cleaned_pois = self._process_elements(raw_elements)
        
        # Deduplicate
        unique_pois = self._deduplicate(cleaned_pois)
        
        # ✨ NEW: Name Translation
        translated_pois, translation_stats = translate_poi_names(unique_pois)
        
        logger.info(f"🌍 Translation Results:")
        logger.info(f"  Total: {translation_stats['total']}")
        logger.info(f"  Already English: {translation_stats['already_english']}")
        logger.info(f"  OSM English tags: {translation_stats['osm_english']}")
        logger.info(f"  Transliterated: {translation_stats['transliterated']}")
        logger.info(f"  Failed: {translation_stats['failed']}")
        
        # ✨ Data Quality Validation
        validated_pois, validation_stats = validate_pois(translated_pois, enhanced=True)
        
        logger.info(f"📊 Validation Results:")
        logger.info(f"  Total: {validation_stats['total']}")
        logger.info(f"  Valid: {validation_stats['valid']} ({validation_stats['valid']/validation_stats['total']*100:.1f}%)")
        logger.info(f"  Rejected: {validation_stats['rejected']} ({validation_stats['rejected']/validation_stats['total']*100:.1f}%)")
        
        if validation_stats['rejection_reasons']:
            logger.info(f"  Top rejection reasons:")
            for reason, count in sorted(validation_stats['rejection_reasons'].items(), key=lambda x: x[1], reverse=True)[:3]:
                logger.info(f"    - {reason}: {count}")
        
        # Save to Silver
        output_dir = self.silver_dir / city_key
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "pois.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(validated_pois, f, indent=2, ensure_ascii=False)
            
        # Save metadata
        metadata = {
            "city": city_name,
            "source_harvest": timestamps[0],
            "processed_at": datetime.now().isoformat(),
            "raw_count": len(raw_elements),
            "clean_count": len(unique_pois),
            "translated_count": len(translated_pois),
            "translation_stats": translation_stats,
            "validated_count": len(validated_pois),
            "validation_stats": validation_stats
        }
        with open(output_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"✅ Silver transformation complete for {city_name}. Saved {len(validated_pois)} validated POIs.")
        return True

    def _process_elements(self, elements: List[Dict]) -> List[Dict]:
        """Converts OSM elements to internal POI schema."""
        pois = []
        for el in elements:
            tags = el.get('tags', {})
            name = tags.get('name') or tags.get('name:en')
            
            if not name:
                continue
                
            # Determine category
            category = "unknown"
            if 'tourism' in tags:
                category = tags['tourism']
            elif 'amenity' in tags:
                category = tags['amenity']
            elif 'historic' in tags:
                category = "historic"
                
            # Coordinates
            lat = el.get('lat') or el.get('center', {}).get('lat')
            lon = el.get('lon') or el.get('center', {}).get('lon')
            
            if not lat or not lon:
                continue
                
            poi = {
                "osm_id": f"{el['type']}/{el['id']}",
                "name": name,
                "category": category,
                "poi_type": category,  # Required for validation
                "lat": lat,  # Required for validation
                "lon": lon,  # Required for validation
                "coordinates": {"lat": lat, "lon": lon},
                "tags": tags
            }
            pois.append(poi)
        return pois

    def _deduplicate(self, pois: List[Dict]) -> List[Dict]:
        """Simple deduplication by name and proximity (simplified)."""
        # For now, just dedup by name + category to keep it fast
        # In production, use spatial deduplication
        seen = set()
        unique = []
        for p in pois:
            key = (p['name'].lower(), p['category'])
            if key not in seen:
                seen.add(key)
                unique.append(p)
        return unique
