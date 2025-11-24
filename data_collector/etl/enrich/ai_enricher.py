import json
import logging
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger("AIEnricher")

class AIEnricher:
    """
    Enriches Silver data with AI (Ollama) to create Gold data.
    """
    
    def __init__(self, silver_dir: Path, gold_dir: Path, model: str = "gemma3:12b"):
        self.silver_dir = silver_dir
        self.gold_dir = gold_dir
        self.model = model
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
        
    def process_city(self, city_name: str, limit: int = 10) -> bool:
        """
        Reads Silver data, prioritizes, enriches top POIs, and saves to Gold.
        """
        city_key = city_name.lower().replace(" ", "_")
        input_file = self.silver_dir / city_key / "pois.json"
        
        if not input_file.exists():
            logger.error(f"No Silver data found for {city_name}")
            return False
            
        with open(input_file, 'r') as f:
            pois = json.load(f)
            
        # Merge Manual POIs if they exist
        manual_file = self.silver_dir / city_key / "manual_pois.json"
        if manual_file.exists():
            try:
                with open(manual_file, 'r') as f:
                    manual_pois = json.load(f)
                    logger.info(f"Found {len(manual_pois)} manual POIs to merge")
                    # Ensure manual POIs have required fields
                    for p in manual_pois:
                        p['priority_score'] = 100 # Force high priority
                        p['is_manual'] = True
                    pois.extend(manual_pois)
            except Exception as e:
                logger.error(f"Failed to load manual POIs: {e}")

        # Merge CSV POIs if they exist
        csv_file = self.silver_dir / city_key / "csv_pois.json"
        if csv_file.exists():
            try:
                with open(csv_file, 'r') as f:
                    csv_pois = json.load(f)
                    logger.info(f"Found {len(csv_pois)} CSV POIs to merge")
                    # Ensure CSV POIs have required fields
                    for p in csv_pois:
                        p['priority_score'] = 100 # Force high priority
                        p['is_manual'] = True
                    pois.extend(csv_pois)
            except Exception as e:
                logger.error(f"Failed to load CSV POIs: {e}")
            
        logger.info(f"Loaded {len(pois)} POIs from Silver layer (including manual/csv)")
        
        # 1. Prioritize
        prioritized_pois = self._prioritize_pois(pois)
        
        # 2. Enrich Top POIs
        enriched_pois = []
        count = 0
        
        # Output directory
        output_dir = self.gold_dir / city_key
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing Gold data to avoid re-enriching
        existing_gold_file = output_dir / "pois.json"
        existing_ids = set()
        if existing_gold_file.exists():
            with open(existing_gold_file, 'r') as f:
                existing_data = json.load(f)
                enriched_pois = existing_data
                existing_ids = {p['osm_id'] for p in existing_data}
                logger.info(f"Loaded {len(existing_data)} existing Gold POIs")

        for poi in prioritized_pois:
            if count >= limit:
                break
                
            if poi['osm_id'] in existing_ids:
                continue
                
            # Skip low priority for enrichment
            if poi.get('priority_score', 0) < 0: # TEMPORARY: Allow all for testing
                continue
                
            logger.info(f"Enriching {poi['name']} (Score: {poi['priority_score']})...")
            enriched_data = self._enrich_poi(poi, city_name)
            if enriched_data:
                poi.update(enriched_data)
                enriched_pois.append(poi)
                count += 1
                
                # Save incrementally
                with open(existing_gold_file, 'w', encoding='utf-8') as f:
                    json.dump(enriched_pois, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Gold enrichment complete for {city_name}. Total Enriched: {len(enriched_pois)}")
        return True

    def _prioritize_pois(self, pois: List[Dict]) -> List[Dict]:
        """Scores POIs based on tourism relevance."""
        for poi in pois:
            score = 0
            cat = poi.get('category') or poi.get('poi_type', '')
            tags = poi.get('tags', {})
            
            # Base score by category
            if cat in ['museum', 'attraction', 'viewpoint']:
                score += 50
            elif cat in ['historic', 'castle', 'ruins']:
                score += 40
            elif cat in ['restaurant', 'cafe']:
                score += 10
            
            # Boosters
            if 'wikipedia' in tags: score += 20
            if 'website' in tags: score += 10
            if 'opening_hours' in tags: score += 5
            
            poi['priority_score'] = min(score, 100)
            
        return sorted(pois, key=lambda x: x['priority_score'], reverse=True)

    def _enrich_poi(self, poi: Dict, city_name: str) -> Optional[Dict]:
        """Calls Ollama to generate description and itinerary details."""
        prompt = f"""
        Analyze this tourism attraction in {city_name}:
        Name: {poi['name']}
        Type: {poi.get('category') or poi.get('poi_type', 'unknown')}
        Tags: {poi.get('tags')}
        Opening Hours: {poi.get('opening_hours', 'Not specified')}
        Address: {poi.get('address', 'Not specified')}

        Provide a JSON response with:
        1. "description": A 2-3 sentence engaging description for travelers (highlight what makes it special).
        2. "duration_min": Recommended visit duration in minutes (integer, realistic estimate).
        3. "best_time": Best time of day to visit (Morning/Afternoon/Evening/Anytime).
        4. "best_time_reason": One sentence explaining why (e.g., "Morning for fewer crowds and better lighting").
        5. "personas": Score 0-100 for Culture, Adventure, Food, Relax (be specific to this attraction).
        6. "price_level": Estimate cost level (0=Free, 1=Budget, 2=Mid-range, 3=Expensive).
        7. "tips": Array of 2-3 practical visitor tips (e.g., "Bring a camera", "Arrive early to avoid crowds").
        8. "what_to_expect": One sentence about the visitor experience.
        9. "is_popular": Boolean - is this a must-see attraction? (true/false)
        
        Return ONLY valid JSON. Be specific and helpful for travelers.
        """
        
        try:
            response = requests.post(
                self.ollama_url,
                json={"model": self.model, "prompt": prompt, "stream": False, "format": "json"},
                timeout=120
            )
            if response.status_code == 200:
                res_json = response.json()
                content = res_json['response']
                # Extract JSON from response (simple heuristic)
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != -1:
                    enriched_data = json.loads(content[start:end])
                    
                    # Ensure all expected fields are present
                    enriched_data.setdefault('best_time_reason', 'Good time to visit')
                    enriched_data.setdefault('price_level', 2)
                    enriched_data.setdefault('tips', [])
                    enriched_data.setdefault('what_to_expect', f"A memorable visit to {poi['name']}")
                    enriched_data.setdefault('is_popular', False)
                    
                    return enriched_data
            
            logger.warning(f"Ollama returned status {response.status_code}. Using FALLBACK.")
            return self._generate_fallback_enrichment(poi, city_name)
        except Exception as e:
            logger.error(f"Enrichment failed for {poi['name']}: {e}")
            logger.warning(f"Using FALLBACK enrichment for {poi['name']}")
            return self._generate_fallback_enrichment(poi, city_name)
    
    def _generate_fallback_enrichment(self, poi: Dict, city_name: str) -> Dict:
        """Generate fallback enrichment data when AI fails"""
        category = poi.get('category', 'place')
        
        # Infer price level from category
        price_map = {
            'museum': 1, 'gallery': 1, 'attraction': 2,
            'restaurant': 2, 'cafe': 1, 'bar': 2,
            'hotel': 3, 'viewpoint': 0, 'park': 0,
            'historic': 0, 'monument': 0, 'memorial': 0
        }
        price_level = price_map.get(category, 2)
        
        return {
            "description": f"A wonderful {category} in {city_name}.",
            "duration_min": 60,
            "best_time": "Morning",
            "best_time_reason": "Good time to visit",
            "personas": {"Culture": 80, "Relax": 50},
            "price_level": price_level,
            "tips": [f"Check opening hours before visiting"],
            "what_to_expect": f"An interesting {category} experience",
            "is_popular": False
        }
