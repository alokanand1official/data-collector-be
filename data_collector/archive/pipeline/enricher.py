import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import time
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class Enricher:
    """
    Enriches POI data using Local LLM (Ollama).
    Generates descriptions and persona scores.
    """
    
    def __init__(self, processed_data_dir: str = "processed_data", model: str = "llama3.1:8b"):
        self.processed_data_dir = Path(processed_data_dir)
        self.llm = OllamaLLM(model=model, temperature=0.7)
        
        # Prompt for description generation
        self.desc_prompt = PromptTemplate.from_template(
            """
            Generate a short, inviting travel description (max 2 sentences) for this place:
            Name: {name}
            Type: {poi_type}
            City: {city}
            Tags: {tags}
            
            Description:
            """
        )
        
        # Prompt for persona scoring
        self.score_prompt = PromptTemplate.from_template(
            """
            Rate this place for these traveler personas (0-100). Return ONLY JSON.
            Place: {name} ({poi_type}) in {city}
            Tags: {tags}
            
            Personas:
            - cultural_explorer (history, art, local life)
            - adventure_seeker (active, nature, thrill)
            - beach_lover (sun, sand, sea)
            - luxury_traveler (comfort, high-end, pampering)
            - culinary_enthusiast (food, drink, markets)
            - wellness_retreater (peace, yoga, spa)
            
            JSON Format:
            {{
                "cultural_explorer": <score>,
                "adventure_seeker": <score>,
                "beach_lover": <score>,
                "luxury_traveler": <score>,
                "culinary_enthusiast": <score>,
                "wellness_retreater": <score>
            }}
            """
        )

    def enrich_poi(self, poi: Dict[str, Any]) -> Dict[str, Any]:
        """Enriches a single POI."""
        
        # Skip if already enriched
        if poi.get('description') and poi.get('persona_scores'):
            return poi
            
        tags_str = ", ".join([f"{k}={v}" for k, v in poi['metadata']['osm_tags'].items() if k in ['amenity', 'tourism', 'cuisine', 'historic', 'religion']])
        
        try:
            # 1. Generate Description
            if not poi.get('description'):
                desc = self.llm.invoke(self.desc_prompt.format(
                    name=poi['name'],
                    poi_type=poi['poi_type'],
                    city=poi['city_name'],
                    tags=tags_str
                ))
                poi['description'] = desc.strip().replace('"', '')
                
            # 2. Generate Scores
            if not poi.get('persona_scores'):
                scores_json = self.llm.invoke(self.score_prompt.format(
                    name=poi['name'],
                    poi_type=poi['poi_type'],
                    city=poi['city_name'],
                    tags=tags_str
                ))
                # Clean up JSON string (sometimes LLM adds markdown)
                scores_json = scores_json.replace("```json", "").replace("```", "").strip()
                poi['persona_scores'] = json.loads(scores_json)
                
            return poi
            
        except Exception as e:
            logger.warning(f"Failed to enrich {poi['name']}: {e}")
            return poi

    def enrich_city(self, city_name: str, limit: int = 10, tier: str = None, use_prioritized: bool = False):
        """
        Enriches POIs for a city. Limit to test first.
        
        Args:
            city_name: Name of the city
            limit: Maximum number of POIs to enrich
            tier: Priority tier to enrich ('essential', 'important', 'recommended', or None for all)
            use_prioritized: If True, use prioritized file instead of regular processed file
        """
        print(f"DEBUG: Inside enrich_city for {city_name}")
        logger.info(f"Enriching data for {city_name} (Limit: {limit}, Tier: {tier})...")
        
        # Determine input file
        city_lower = city_name.lower().replace(' ', '_')
        if use_prioritized or tier:
            input_file = self.processed_data_dir / f"{city_lower}_pois_prioritized.json"
        else:
            input_file = self.processed_data_dir / f"{city_lower}_pois.json"
            
        if not input_file.exists():
            print(f"DEBUG: File not found: {input_file}")
            logger.error(f"No processed data found for {city_name}")
            return

        with open(input_file, 'r', encoding='utf-8') as f:
            pois = json.load(f)
            
        print(f"DEBUG: Loaded {len(pois)} POIs")
        
        # Filter by tier if specified
        if tier:
            original_count = len(pois)
            pois_to_enrich = [p for p in pois if p.get('priority_tier') == tier]
            logger.info(f"Filtered to {len(pois_to_enrich)} POIs in tier '{tier}' (from {original_count} total)")
            print(f"DEBUG: Filtered to {len(pois_to_enrich)} POIs in tier '{tier}'")
        else:
            pois_to_enrich = pois
            
        # Apply limit
        if limit and limit < len(pois_to_enrich):
            pois_to_enrich = pois_to_enrich[:limit]
            logger.info(f"Limited to {limit} POIs")
            
        enriched_count = 0
        for i, poi in enumerate(pois_to_enrich):
            print(f"DEBUG: Processing {i}: {poi['name']}")
            logger.info(f"Enriching {i+1}/{len(pois_to_enrich)}: {poi['name']}")
            start = time.time()
            
            # Find the POI in the original list and enrich it
            poi_index = next((idx for idx, p in enumerate(pois) if p.get('osm_id') == poi.get('osm_id')), None)
            if poi_index is not None:
                pois[poi_index] = self.enrich_poi(poi)
            
            duration = time.time() - start
            logger.info(f"  Done in {duration:.2f}s")
            enriched_count += 1
            
        # Save back to the same file
        print("DEBUG: Saving back to file...")
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(pois, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Enriched {enriched_count} POIs for {city_name}")
        print("DEBUG: Done saving")
