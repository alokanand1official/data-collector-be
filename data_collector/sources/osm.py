"""
OpenStreetMap Data Collector
FREE, comprehensive data source for POIs, destinations, and more
"""

import overpy
import time
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class OSMCollector:
    """
    Collects data from OpenStreetMap using Overpass API
    100% FREE - no API key required!
    """

    def __init__(
        self,
        rate_limit_delay: float = 1.0,
        timeout: int = 60
    ):
        """
        Initialize OSM collector

        Args:
            rate_limit_delay: Seconds to wait between requests (be nice to OSM!)
            timeout: Query timeout in seconds
        """
        self.api = overpy.Overpass()
        self.rate_limit_delay = rate_limit_delay
        self.timeout = timeout
        self.last_request_time = 0

    def collect_pois_in_province(
        self,
        province_name: str,
        poi_type: str,
        country_code: str = "TH",
        admin_level: int = 6,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect all POIs of a specific type in a province

        Args:
            province_name: Name of province
            poi_type: Type of POI (temple, beach, market, etc.)
            country_code: ISO country code
            admin_level: OSM admin level (6 for provinces)
            limit: Optional limit on results

        Returns:
            List of POI data dicts
        """
        logger.info(f"Collecting {poi_type}s in {province_name}, {country_code}")

        # Get OSM query tags for this POI type
        tags = self._get_poi_tags(poi_type)

        if not tags:
            logger.warning(f"No OSM tags defined for POI type: {poi_type}")
            return []

        # Build Overpass query
        query = self._build_province_query(
            province_name,
            tags,
            admin_level,
            limit
        )

        # Execute query with rate limiting
        self._rate_limit()

        try:
            result = self.api.query(query)
            pois = self._parse_overpass_result(result, poi_type)

            logger.info(f"Found {len(pois)} {poi_type}s in {province_name}")
            return pois

        except Exception as e:
            logger.error(f"Error querying OSM: {e}")
            return []

    def collect_pois_in_bounding_box(
        self,
        bbox: Dict[str, float],
        poi_type: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect POIs within a bounding box

        Args:
            bbox: {north, south, east, west}
            poi_type: Type of POI
            limit: Optional limit

        Returns:
            List of POI data
        """
        tags = self._get_poi_tags(poi_type)
        if not tags:
            return []

        query = self._build_bbox_query(bbox, tags, limit)

        self._rate_limit()

        try:
            result = self.api.query(query)
            return self._parse_overpass_result(result, poi_type)
        except Exception as e:
            logger.error(f"Error querying OSM bbox: {e}")
            return []

    def collect_destinations_in_country(
        self,
        country_code: str,
        destination_types: List[str] = ["city", "town", "village"]
    ) -> List[Dict[str, Any]]:
        """
        Collect all destinations (cities, towns) in a country

        Args:
            country_code: ISO country code
            destination_types: Types to collect

        Returns:
            List of destination data
        """
        logger.info(f"Collecting destinations in {country_code}")

        destinations = []

        for dest_type in destination_types:
            query = f"""
            [out:json][timeout:{self.timeout}];
            area["ISO3166-1"="{country_code}"]->.country;
            (
              node["place"="{dest_type}"](area.country);
              way["place"="{dest_type}"](area.country);
            );
            out center tags;
            """

            self._rate_limit()

            try:
                result = self.api.query(query)
                parsed = self._parse_destinations(result, dest_type, country_code)
                destinations.extend(parsed)
                logger.info(f"Found {len(parsed)} {dest_type}s")
            except Exception as e:
                logger.error(f"Error collecting {dest_type}s: {e}")

        logger.info(f"Total destinations collected: {len(destinations)}")
        return destinations

    def _build_province_query(
        self,
        province_name: str,
        tags: List[str],
        admin_level: int,
        limit: Optional[int]
    ) -> str:
        """Build Overpass query for province"""

        # Build tag filters
        tag_filters = []
        for tag in tags:
            parts = tag.split(" AND ")
            filter_str = "".join([f'["{p.split("=")[0]}"="{p.split("=")[1]}"]' for p in parts])
            tag_filters.append(filter_str)

        limit_str = f"({limit})" if limit else ""

        query = f"""
        [out:json][timeout:{self.timeout}];
        area["name"="{province_name}"]["admin_level"="{admin_level}"]->.province;
        (
        """

        for tag_filter in tag_filters:
            query += f'  node{tag_filter}(area.province){limit_str};\n'
            query += f'  way{tag_filter}(area.province){limit_str};\n'

        query += """
        );
        out center tags;
        """

        return query

    def _build_bbox_query(
        self,
        bbox: Dict[str, float],
        tags: List[str],
        limit: Optional[int]
    ) -> str:
        """Build Overpass query for bounding box"""

        bbox_str = f"{bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']}"
        limit_str = f"({limit})" if limit else ""

        tag_filters = []
        for tag in tags:
            parts = tag.split(" AND ")
            filter_str = "".join([f'["{p.split("=")[0]}"="{p.split("=")[1]}"]' for p in parts])
            tag_filters.append(filter_str)

        query = f"""
        [out:json][timeout:{self.timeout}];
        (
        """

        for tag_filter in tag_filters:
            query += f'  node{tag_filter}({bbox_str}){limit_str};\n'
            query += f'  way{tag_filter}({bbox_str}){limit_str};\n'

        query += """
        );
        out center tags;
        """

        return query

    def _parse_overpass_result(
        self,
        result: overpy.Result,
        poi_type: str
    ) -> List[Dict[str, Any]]:
        """Parse Overpass API result into POI data"""

        pois = []

        for element in result.nodes + result.ways + result.relations:
            try:
                # Get coordinates
                if hasattr(element, 'lat'):
                    lat, lon = element.lat, element.lon
                elif hasattr(element, 'center_lat'):
                    lat, lon = element.center_lat, element.center_lon
                else:
                    continue  # Skip if no coordinates

                # Extract data
                poi = {
                    'name': element.tags.get('name', 'Unknown'),
                    'name_local': element.tags.get('name:th') or element.tags.get('name:local'),
                    'poi_type': poi_type,
                    'coordinates': {'lat': float(lat), 'lng': float(lon)},

                    # Practical info
                    'opening_hours': element.tags.get('opening_hours'),
                    'phone': element.tags.get('phone'),
                    'website': element.tags.get('website'),
                    'address': element.tags.get('addr:full') or self._build_address(element.tags),

                    # External IDs
                    'osm_id': f"{element.id}",
                    'osm_type': 'node' if hasattr(element, 'lat') else 'way',
                    'wikidata_id': element.tags.get('wikidata'),
                    'wikipedia_url': self._parse_wikipedia(element.tags.get('wikipedia')),

                    # Description from OSM
                    'description': element.tags.get('description'),

                    # All OSM tags for reference
                    'metadata': {
                        'osm_tags': dict(element.tags)
                    },

                    # Data source
                    'data_sources': ['osm']
                }

                pois.append(poi)

            except Exception as e:
                logger.warning(f"Error parsing element: {e}")
                continue

        return pois

    def _parse_destinations(
        self,
        result: overpy.Result,
        dest_type: str,
        country_code: str
    ) -> List[Dict[str, Any]]:
        """Parse destinations from Overpass result"""

        destinations = []

        for element in result.nodes + result.ways:
            try:
                if hasattr(element, 'lat'):
                    lat, lon = element.lat, element.lon
                elif hasattr(element, 'center_lat'):
                    lat, lon = element.center_lat, element.center_lon
                else:
                    continue

                dest = {
                    'name': element.tags.get('name', 'Unknown'),
                    'name_local': element.tags.get('name:th') or element.tags.get('name:local'),
                    'destination_type': dest_type,
                    'country': country_code,

                    'coordinates': {'lat': float(lat), 'lng': float(lon)},

                    'population': element.tags.get('population'),
                    'wikidata_id': element.tags.get('wikidata'),
                    'wikipedia_url': self._parse_wikipedia(element.tags.get('wikipedia')),

                    'osm_id': f"{element.id}",

                    'metadata': {
                        'osm_tags': dict(element.tags)
                    },

                    'data_sources': ['osm']
                }

                destinations.append(dest)

            except Exception as e:
                logger.warning(f"Error parsing destination: {e}")
                continue

        return destinations

    def _get_poi_tags(self, poi_type: str) -> List[str]:
        """Get OSM tags for POI type"""

        # Mapping of POI types to OSM tags
        POI_TAGS = {
            'temple': [
                'amenity=place_of_worship', # Broadened for all religions
                'building=temple',
                'historic=temple',
                'religion=buddhist',
                'religion=hindu',
                'religion=sikh',
                'religion=muslim',
                'religion=christian'
            ],
            'historic': [ # New category for landmarks
                'historic=monument',
                'historic=memorial',
                'historic=fort',
                'historic=castle',
                'historic=ruins',
                'tourism=attraction',
                'historic=tomb'
            ],
            'beach': [
                'natural=beach',
                'natural=coastline'
            ],
            'market': [
                'amenity=marketplace',
                'amenity=market'
            ],
            'viewpoint': [
                'tourism=viewpoint'
            ],
            'museum': [
                'tourism=museum',
                'amenity=arts_centre'
            ],
            'national_park': [
                'boundary=national_park',
                'leisure=nature_reserve'
            ],
            'waterfall': [
                'waterway=waterfall',
                'natural=waterfall'
            ],
            'palace': [
                'historic=palace',
                'historic=castle',
                'building=palace'
            ],
            'island': [
                'place=island'
            ],
            'restaurant': [
                'amenity=restaurant'
            ],
            'hotel': [
                'tourism=hotel',
                'tourism=guest_house'
            ]
        }

        return POI_TAGS.get(poi_type, [])

    def _build_address(self, tags: Dict[str, str]) -> Optional[str]:
        """Build address from OSM tags"""
        parts = []

        if 'addr:housenumber' in tags:
            parts.append(tags['addr:housenumber'])
        if 'addr:street' in tags:
            parts.append(tags['addr:street'])
        if 'addr:city' in tags:
            parts.append(tags['addr:city'])
        if 'addr:province' in tags:
            parts.append(tags['addr:province'])

        return ', '.join(parts) if parts else None

    def _parse_wikipedia(self, wikipedia_tag: Optional[str]) -> Optional[str]:
        """Parse Wikipedia tag to URL"""
        if not wikipedia_tag:
            return None

        # Format: "en:Article Name" or "th:ชื่อบทความ"
        if ':' in wikipedia_tag:
            lang, article = wikipedia_tag.split(':', 1)
            article = article.replace(' ', '_')
            return f"https://{lang}.wikipedia.org/wiki/{article}"

        return None

    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
