"""
LLM Utilities for Data Collection
Uses Ollama for local LLM inference (FREE!)
"""

import json
import re
import os
from typing import Dict, Any, List, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


class LocalLLM:
    """
    Interface to local LLM via Ollama
    Supports Llama 3.1 8B and 70B models
    """

    def __init__(
        self,
        model: str = None,
        temperature: float = 0.0,
        base_url: str = None
    ):
        """
        Initialize local LLM

        Args:
            model: Model name (llama-3.1-8b, llama-3.1-70b, mistral, etc.)
                   If None, uses OLLAMA_MODEL env var or defaults to llama-3.1-8b
            temperature: 0 = deterministic, 1 = creative
            base_url: Ollama server URL
                      If None, uses OLLAMA_BASE_URL env var or defaults to http://localhost:11434
        """
        # Use environment variables if parameters not provided
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        ollama_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        self.llm = ChatOllama(
            model=self.model,
            temperature=temperature,
            base_url=ollama_url,
        )

    def score_poi_for_personas(
        self,
        poi_data: Dict[str, Any],
        personas: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Score a POI for each travel persona (0-100)

        Args:
            poi_data: POI information
            personas: List of persona definitions

        Returns:
            Dict of persona scores {persona_id: score}
        """
        persona_descriptions = "\n".join([
            f"- {p['id']}: {', '.join(p.get('keywords', []))}"
            for p in personas
        ])

        prompt = f"""You are a travel data analyst. Score this point of interest for each travel persona.

POI Information:
- Name: {poi_data.get('name', 'Unknown')}
- Type: {poi_data.get('poi_type', 'Unknown')}
- Description: {poi_data.get('description', 'No description')}

Travel Personas:
{persona_descriptions}

Score each persona from 0-100 based on how well this POI matches their interests.
- 90-100: Perfect match, must-visit for this persona
- 70-89: Great match, highly recommended
- 50-69: Good match, worth considering
- 30-49: Moderate match, might interest some
- 0-29: Poor match, unlikely to interest

Return ONLY a valid JSON object with scores:
{{
  "cultural_explorer": 85,
  "adventure_seeker": 40,
  "luxury_connoisseur": 50,
  "culinary_wanderer": 30,
  "wellness_retreater": 70,
  "social_nomad": 45
}}
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            scores = self._extract_json(response.content)

            # Validate scores
            validated_scores = {}
            for persona in personas:
                score = scores.get(persona['id'], 50)  # Default to 50
                validated_scores[persona['id']] = max(0, min(100, int(score)))

            return validated_scores

        except Exception as e:
            print(f"Error scoring POI: {e}")
            # Return default scores
            return {p['id']: 50 for p in personas}

    def generate_poi_description(
        self,
        poi_data: Dict[str, Any],
        persona_id: Optional[str] = None,
        min_words: int = 20,
        max_words: int = 100
    ) -> str:
        """
        Generate a compelling description for a POI

        Args:
            poi_data: POI information
            persona_id: Optional persona to tailor description for
            min_words: Minimum words
            max_words: Maximum words

        Returns:
            Generated description
        """
        persona_context = ""
        if persona_id:
            persona_context = f"\nWrite this description for {persona_id} travelers specifically."

        prompt = f"""You are a professional travel writer. Write a compelling, informative description for this point of interest.

POI Information:
- Name: {poi_data.get('name', 'Unknown')}
- Type: {poi_data.get('poi_type', 'Unknown')}
- Location: {poi_data.get('province', '')}, {poi_data.get('country', '')}
- Existing description: {poi_data.get('description', 'None')}{persona_context}

Guidelines:
- Length: {min_words}-{max_words} words
- Focus on what makes it special and worth visiting
- Include practical details if known (what to see, when to visit)
- Be engaging and informative
- Don't use clichés or overly promotional language

Write only the description, no introductory text:"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()

            # Remove common prefixes
            description = re.sub(r'^(Here\'s|This is|The description is)[:\s]+', '', description, flags=re.IGNORECASE)

            return description

        except Exception as e:
            print(f"Error generating description: {e}")
            return poi_data.get('description', '')

    def categorize_poi(
        self,
        poi_data: Dict[str, Any],
        vibe_tags_options: List[str],
        category_tags_options: List[str]
    ) -> Dict[str, List[str]]:
        """
        Categorize POI with vibe and category tags

        Args:
            poi_data: POI information
            vibe_tags_options: Available vibe tags
            category_tags_options: Available category tags

        Returns:
            Dict with {vibe_tags: [], category_tags: []}
        """
        prompt = f"""You are a travel categorization expert. Analyze this POI and assign appropriate tags.

POI Information:
- Name: {poi_data.get('name', 'Unknown')}
- Type: {poi_data.get('poi_type', 'Unknown')}
- Description: {poi_data.get('description', 'No description')}

Available Vibe Tags:
{', '.join(vibe_tags_options)}

Available Category Tags:
{', '.join(category_tags_options)}

Select 3-5 most relevant tags from each category.

Return ONLY a valid JSON object:
{{
  "vibe_tags": ["spiritual", "peaceful", "historical"],
  "category_tags": ["solo-friendly", "budget", "outdoor"]
}}
"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            tags = self._extract_json(response.content)

            return {
                'vibe_tags': tags.get('vibe_tags', [])[:5],
                'category_tags': tags.get('category_tags', [])[:5]
            }

        except Exception as e:
            print(f"Error categorizing POI: {e}")
            return {'vibe_tags': [], 'category_tags': []}

    def batch_score_pois(
        self,
        pois: List[Dict[str, Any]],
        personas: List[Dict[str, Any]],
        batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Score multiple POIs in batches for efficiency

        Args:
            pois: List of POI data
            personas: Persona definitions
            batch_size: Number of POIs to process at once

        Returns:
            List of POIs with added persona_scores
        """
        enriched_pois = []

        for i in range(0, len(pois), batch_size):
            batch = pois[i:i + batch_size]

            for poi in batch:
                scores = self.score_poi_for_personas(poi, personas)
                poi['persona_scores'] = scores
                enriched_pois.append(poi)

            print(f"Scored {min(i + batch_size, len(pois))}/{len(pois)} POIs")

        return enriched_pois

    def generate_destination_content(self, city: str, country: str) -> Dict:
        """Generate rich content for a destination."""
        prompt = f"""
        Generate comprehensive travel content for {city}, {country}.
        Return ONLY valid JSON with these fields:
        - description: A captivating 2-sentence travel description.
        - short_description: A punchy 1-sentence summary (max 150 chars).
        - vibe_tags: A list of 3-5 vibe tags (e.g., "Nightlife", "Culture", "Beach", "Adventure").
        - category_tags: A list of 3-5 category tags (e.g., "Solo-friendly", "Family", "Romantic", "Budget").
        - budget_range: One of "budget", "moderate", "luxury".
        - price_per_day_min: Minimum estimated daily cost in USD (integer).
        - price_per_day_max: Maximum estimated daily cost in USD (integer).
        - average_trip_duration: Recommended number of days to visit (integer).
        - best_time_to_visit: Short string (e.g., "Nov-Feb").
        - climate_type: One of "Tropical", "Temperate", "Arid", "Cold", "Continental".
        - language: Main language spoken.
        - currency: Local currency name.
        - time_zone: Time zone string (e.g., "GMT+7").
        
        JSON:
        """
        try:
            response = self.llm.invoke(prompt)
            # Handle LangChain AIMessage object
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Clean markdown
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            print(f"Error generating destination content: {e}")
            return {}

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        # Find JSON block in response
        json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Try to extract from code block
        code_match = re.search(r'```(?:json)?\s*(\{.+?\})\s*```', text, re.DOTALL)
        if code_match:
            json_str = code_match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Could not extract valid JSON from response: {text}")


# MacBook Pro performance estimates
class PerformanceEstimates:
    """
    Performance estimates for different Mac models
    """

    CONFIGS = {
        "m1_8gb": {
            "model": "llama-3.1-8b",
            "tokens_per_sec": 20,
            "pois_per_hour": 150,
        },
        "m1_16gb": {
            "model": "llama-3.1-8b",
            "tokens_per_sec": 30,
            "pois_per_hour": 200,
        },
        "m1_pro_16gb": {
            "model": "llama-3.1-8b",
            "tokens_per_sec": 40,
            "pois_per_hour": 250,
        },
        "m1_max_32gb": {
            "model": "llama-3.1-70b",
            "tokens_per_sec": 15,
            "pois_per_hour": 100,
        },
        "m2_16gb": {
            "model": "llama-3.1-8b",
            "tokens_per_sec": 35,
            "pois_per_hour": 220,
        },
        "m2_pro_16gb": {
            "model": "llama-3.1-8b",
            "tokens_per_sec": 45,
            "pois_per_hour": 280,
        },
        "m3_24gb": {
            "model": "llama-3.1-8b",
            "tokens_per_sec": 50,
            "pois_per_hour": 300,
        },
        "m3_pro_36gb": {
            "model": "llama-3.1-70b",
            "tokens_per_sec": 20,
            "pois_per_hour": 120,
        },
    }

    @classmethod
    def estimate_time(cls, config_name: str, num_pois: int) -> Dict[str, float]:
        """
        Estimate processing time

        Args:
            config_name: Mac configuration
            num_pois: Number of POIs to process

        Returns:
            Dict with time estimates
        """
        config = cls.CONFIGS.get(config_name, cls.CONFIGS["m1_16gb"])
        pois_per_hour = config["pois_per_hour"]

        hours = num_pois / pois_per_hour
        days = hours / 24

        return {
            "total_hours": round(hours, 2),
            "total_days": round(days, 2),
            "pois_per_hour": pois_per_hour,
            "recommended_model": config["model"],
        }
