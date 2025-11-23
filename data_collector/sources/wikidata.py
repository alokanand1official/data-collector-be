import logging
from SPARQLWrapper import SPARQLWrapper, JSON
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class WikidataCollector:
    """Collects city data from Wikidata using SPARQL."""

    def __init__(self, user_agent: str = "BeyondEscapismBot/1.0 (contact@beyondescapism.com)"):
        self.sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        self.sparql.setReturnFormat(JSON)
        self.sparql.addCustomHttpHeader("User-Agent", user_agent)
        
        # Bypass SSL verification (Fix for macOS Python)
        import ssl
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context

    def get_city_details(self, city_name: str) -> Optional[Dict]:
        """
        Fetches details for a city: Image, Population, Currency, Description, Coordinates.
        """
        logger.info(f"Fetching Wikidata for: {city_name}")
        
        # SPARQL Query
        # ?cityLabel: Name
        # ?countryLabel: Country
        # ?population: Population
        # ?image: Image URL
        # ?currencyLabel: Currency
        # ?coords: Coordinates
        # ?desc: Description
        query = f"""
        SELECT ?city ?cityLabel ?countryLabel ?population ?image ?currencyLabel ?coords ?desc WHERE {{
          ?city rdfs:label "{city_name}"@en.
          ?city wdt:P31/wdt:P279* wd:Q515.  # Instance of city or subclass
          
          OPTIONAL {{ ?city wdt:P17 ?country. }}
          OPTIONAL {{ ?city wdt:P1082 ?population. }}
          OPTIONAL {{ ?city wdt:P18 ?image. }}
          OPTIONAL {{ ?city wdt:P38 ?currency. }}
          OPTIONAL {{ ?city wdt:P625 ?coords. }}
          OPTIONAL {{ ?city schema:description ?desc. FILTER(LANG(?desc) = "en") }}
          
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 1
        """
        
        try:
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            
            bindings = results["results"]["bindings"]
            if not bindings:
                logger.warning(f"No Wikidata found for {city_name}")
                return None
                
            data = bindings[0]
            
            # Extract and clean data
            result = {
                "name": city_name,
                "country": data.get("countryLabel", {}).get("value"),
                "population": int(data.get("population", {}).get("value", 0)),
                "image": data.get("image", {}).get("value"),
                "currency": data.get("currencyLabel", {}).get("value"),
                "description": data.get("desc", {}).get("value"),
                "wikidata_id": data.get("city", {}).get("value").split("/")[-1]
            }
            
            # Parse coordinates "Point(100.5 13.75)" -> {lat: 13.75, lng: 100.5}
            if "coords" in data:
                wkt = data["coords"]["value"]
                # WKT format: Point(LNG LAT)
                try:
                    clean_wkt = wkt.replace("Point(", "").replace(")", "")
                    lng, lat = map(float, clean_wkt.split())
                    result["coordinates"] = {"lat": lat, "lng": lng}
                except Exception as e:
                    logger.warning(f"Failed to parse coords for {city_name}: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Wikidata query failed for {city_name}: {e}")
            return None

if __name__ == "__main__":
    # Test run
    logging.basicConfig(level=logging.INFO)
    collector = WikidataCollector()
    details = collector.get_city_details("Bangkok")
    import json
    print(json.dumps(details, indent=2))
