import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any, List
from config.cities_config import CITIES

logger = logging.getLogger("DestinationEnricher")

class DestinationEnricher:
    """
    Enriches Destination entities with deep metadata using AI.
    Generates: Monthly Insights, Safety, Budget, Recommendations.
    """
    
    def __init__(self, gold_dir: Path = Path("layers/gold"), model: str = "gemma3:12b"):
        self.gold_dir = gold_dir
        self.model = model
        self.api_url = "http://localhost:11434/api/generate"
        
    def enrich_destination(self, city_name: str) -> bool:
        """
        Generates deep content for a city and saves to Gold Layer.
        """
        city_key = city_name.lower().replace(" ", "_")
        city_config = CITIES.get(city_key)
        
        if not city_config:
            logger.error(f"City {city_name} not found in config")
            return False
            
        logger.info(f"🌍 Enriching Destination: {city_name}...")
        
        # 1. Base Structure
        destination_data = {
            "slug": city_key,
            "name": city_config['name'],
            "country_code": "GE" if city_config['country'] == "Georgia" else "XX", # Simplified for now
            "coordinates": self._get_center_from_bbox(city_config.get('bbox')),
            "timezone": "Asia/Tbilisi" if city_config['country'] == "Georgia" else "UTC"
        }
        
        # 2. AI Enrichment
        try:
            ai_content = self._generate_ai_content(city_name, city_config['country'])
            destination_data.update(ai_content)
        except Exception as e:
            logger.error(f"AI Enrichment failed: {e}")
            # Fallback to minimal data
            destination_data.update({
                "summary": f"A beautiful city in {city_config['country']}.",
                "why_go": ["Culture", "History"],
                "safety": {"score": 0.8, "notes": "Generally safe."}
            })
            
        # 3. Save to Gold Layer
        output_dir = self.gold_dir / city_key
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "destination_details.json"
        with open(output_file, 'w') as f:
            json.dump(destination_data, f, indent=2)
            
        logger.info(f"✅ Saved destination details to {output_file}")
        return True

    def _get_center_from_bbox(self, bbox: Dict) -> Dict:
        if not bbox:
            return {"lat": 0.0, "lng": 0.0}
        lat = (bbox['north'] + bbox['south']) / 2
        lng = (bbox['east'] + bbox['west']) / 2
        return {"lat": lat, "lng": lng}

    def _generate_ai_content(self, city: str, country: str) -> Dict:
        """
        Calls Ollama to generate the deep JSON object.
        """
        prompt = f"""
        You are a travel expert. Generate a JSON object for {city}, {country} with this EXACT structure:
        {{
            "summary": "Short catchy description",
            "why_go": ["Reason 1", "Reason 2", "Reason 3"],
            "tags": ["tag1", "tag2"],
            "best_months": [5, 6, 9, 10],
            "monthly_insights": {{
                "1": {{ "verdict": "Cold", "temp": {{ "avg": 5 }}, "crowdLevel": "Low" }}
                // ... just do month 1 and 7 for brevity in this demo
            }},
            "personality_fit": {{ "HistoryBuff": 0.9, "Foodie": 0.8 }},
            "budget": {{ "level": "Mid-Range", "daily_cost": {{ "backpacker": 50, "luxury": 300 }} }},
            "safety": {{ "score": 0.85, "notes": "Safety notes" }},
            "connectivity": {{ "wifi": "Good", "mobile": "Good" }}
        }}
        Return ONLY valid JSON. No markdown.
        """
        
        try:
            response = requests.post(
                self.api_url,
                json={"model": self.model, "prompt": prompt, "stream": False, "format": "json"},
                timeout=120
            )
            if response.status_code == 200:
                res_json = response.json()
                content = res_json.get('response', '{}')
                # Parse JSON from string response
                if isinstance(content, str):
                    import json as json_lib
                    return json_lib.loads(content)
                return content
            else:
                logger.warning(f"Ollama error: {response.status_code}")
                raise Exception("Ollama API failed")
        except Exception as e:
            logger.warning(f"Ollama connection failed: {e}. Using Mock Data.")
            return self._get_mock_data(city)

    def _get_mock_data(self, city: str) -> Dict:
        return {
            "summary": f"{city} is a vibrant destination known for its rich history and culture.",
            "why_go": ["Ancient Architecture", "Delicious Cuisine", "Scenic Views"],
            "tags": ["heritage", "culture", "food"],
            "best_months": [4, 5, 9, 10],
            "monthly_insights": {
                "1": { "verdict": "Winter chill", "temp": { "avg": 5 }, "crowdLevel": "Low" },
                "7": { "verdict": "Hot summer", "temp": { "avg": 30 }, "crowdLevel": "High" }
            },
            "personality_fit": { "HistoryBuff": 0.9, "Foodie": 0.85 },
            "budget": { "level": "Mid-Range", "daily_cost": { "backpacker": 40, "luxury": 200 } },
            "safety": { "score": 0.9, "notes": "Very safe for tourists." },
            "connectivity": { "wifi": "Excellent", "mobile": "4G/5G available" }
        }
