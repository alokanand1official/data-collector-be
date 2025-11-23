import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

logger = logging.getLogger("ParallelAIEnricher")

class ParallelAIEnricher:
    """
    Parallel version of AIEnricher for faster processing.
    Uses ThreadPoolExecutor to enrich multiple POIs simultaneously.
    """
    
    def __init__(self, silver_dir: Path, gold_dir: Path, model: str = "llama3.1", max_workers: int = 5):
        self.silver_dir = silver_dir
        self.gold_dir = gold_dir
        self.model = model
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
        self.max_workers = max_workers
        
    def process_city(self, city_name: str, tier: str = "all", limit: int = None) -> bool:
        """
        Enriches POIs for a city using parallel processing.
        """
        city_key = city_name.lower().replace(" ", "_")
        
        # Load Silver data
        silver_file = self.silver_dir / city_key / "pois.json"
        if not silver_file.exists():
            logger.error(f"Silver file not found: {silver_file}")
            return False
            
        with open(silver_file, 'r') as f:
            pois = json.load(f)
            
        # Load existing Gold data
        gold_file = self.gold_dir / city_key / "pois.json"
        existing_pois = []
        if gold_file.exists():
            with open(gold_file, 'r') as f:
                existing_pois = json.load(f)
                
        existing_ids = {poi.get('osm_id') for poi in existing_pois}
        
        # Filter POIs to enrich
        to_enrich = [poi for poi in pois if poi.get('osm_id') not in existing_ids]
        
        if tier != "all":
            to_enrich = [poi for poi in to_enrich if poi.get('priority_tier') == tier]
            
        if limit:
            to_enrich = to_enrich[:limit]
            
        logger.info(f"Enriching {len(to_enrich)} POIs for {city_name} using {self.max_workers} workers...")
        
        # Parallel enrichment
        enriched_pois = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_poi = {executor.submit(self._enrich_poi, poi): poi for poi in to_enrich}
            
            for future in tqdm(as_completed(future_to_poi), total=len(to_enrich), desc=f"Enriching {city_name}"):
                try:
                    enriched_poi = future.result()
                    if enriched_poi:
                        enriched_pois.append(enriched_poi)
                except Exception as e:
                    poi = future_to_poi[future]
                    logger.error(f"Failed to enrich {poi.get('name')}: {e}")
                    
        # Merge with existing
        all_pois = existing_pois + enriched_pois
        
        # Save to Gold
        gold_file.parent.mkdir(parents=True, exist_ok=True)
        with open(gold_file, 'w') as f:
            json.dump(all_pois, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Enriched {len(enriched_pois)} POIs. Total: {len(all_pois)}")
        return True
        
    def _enrich_poi(self, poi: Dict) -> Dict:
        """
        Enriches a single POI using Ollama.
        """
        prompt = f"""
        Analyze this tourism POI and provide enrichment data:
        Name: {poi.get('name')}
        Type: {poi.get('poi_type')}
        
        Return ONLY valid JSON with:
        1. "description": Engaging 2-sentence description
        2. "duration_min": Recommended visit duration in minutes
        3. "best_time": Best time to visit (Morning/Afternoon/Evening/Anytime)
        4. "personas": Score 0-100 for [Culture, Adventure, Food, Relax]
        
        Return ONLY valid JSON.
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
                # Extract JSON from response
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end > start:
                    enrichment = json.loads(content[start:end])
                    
                    # Merge enrichment with original POI
                    poi['description'] = enrichment.get('description', poi.get('description', ''))
                    poi['duration_min'] = enrichment.get('duration_min', 60)
                    poi['best_time'] = enrichment.get('best_time', 'Anytime')
                    poi['personas'] = enrichment.get('personas', {"Culture": 50, "Relax": 50})
                    
                    return poi
            else:
                logger.warning(f"Ollama returned status {response.status_code}")
                return self._mock_enrich(poi)
        except Exception as e:
            logger.warning(f"Enrichment failed for {poi.get('name')}: {e}")
            return self._mock_enrich(poi)
            
    def _mock_enrich(self, poi: Dict) -> Dict:
        """Fallback enrichment"""
        poi['description'] = poi.get('description', f"A wonderful place in {poi.get('city_name', 'the city')}.")
        poi['duration_min'] = 60
        poi['best_time'] = "Morning"
        poi['personas'] = {"Culture": 80, "Relax": 50}
        return poi
