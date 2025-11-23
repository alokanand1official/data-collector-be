"""
Name Translation and Transliteration System
Converts non-English POI names to English using OSM tags and transliteration
"""

import re
import logging
from typing import Optional, Dict

logger = logging.getLogger("NameTranslator")

class NameTranslator:
    """
    Translates and transliterates POI names to English.
    
    Strategy:
    1. Check OSM name:en tag (preferred)
    2. Transliterate if Georgian/Cyrillic
    3. Return None if translation fails
    """
    
    def __init__(self):
        # Georgian to Latin transliteration map
        self.georgian_map = {
            'ა': 'a', 'ბ': 'b', 'გ': 'g', 'დ': 'd', 'ე': 'e', 'ვ': 'v',
            'ზ': 'z', 'თ': 't', 'ი': 'i', 'კ': 'k', 'ლ': 'l', 'მ': 'm',
            'ნ': 'n', 'ო': 'o', 'პ': 'p', 'ჟ': 'zh', 'რ': 'r', 'ს': 's',
            'ტ': 't', 'უ': 'u', 'ფ': 'p', 'ქ': 'k', 'ღ': 'gh', 'ყ': 'q',
            'შ': 'sh', 'ჩ': 'ch', 'ც': 'ts', 'ძ': 'dz', 'წ': 'ts', 'ჭ': 'ch',
            'ხ': 'kh', 'ჯ': 'j', 'ჰ': 'h'
        }
        
        # Cyrillic to Latin transliteration map (Russian)
        self.cyrillic_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e',
            'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
            'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
            'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
            'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
            'э': 'e', 'ю': 'yu', 'я': 'ya',
            # Uppercase
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E',
            'Ё': 'Yo', 'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K',
            'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
            'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts',
            'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '', 'Ы': 'Y', 'Ь': '',
            'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
        }
        
        # Script detection patterns
        self.georgian_pattern = re.compile(r'[\u10A0-\u10FF]')
        self.cyrillic_pattern = re.compile(r'[\u0400-\u04FF]')
        
    def translate_poi_name(self, poi: Dict) -> Optional[str]:
        """
        Translate POI name to English.
        
        Priority:
        1. name:en tag from OSM
        2. Transliteration
        3. None (will be rejected)
        
        Args:
            poi: POI dictionary with 'name' and 'tags'
        
        Returns:
            English name or None if translation fails
        """
        original_name = poi.get('name', '').strip()
        tags = poi.get('tags', {})
        
        if not original_name:
            return None
        
        # 1. Check for OSM English name tag
        english_name = self._get_osm_english_name(tags)
        if english_name:
            logger.debug(f"Using OSM name:en: {original_name} → {english_name}")
            return english_name
        
        # 2. Try transliteration
        transliterated = self._transliterate(original_name)
        if transliterated and transliterated != original_name:
            logger.debug(f"Transliterated: {original_name} → {transliterated}")
            return transliterated
        
        # 3. Translation failed
        logger.debug(f"Translation failed for: {original_name}")
        return None
    
    def _get_osm_english_name(self, tags: Dict) -> Optional[str]:
        """Extract English name from OSM tags"""
        # Try various English name tags
        english_tags = ['name:en', 'int_name', 'name_en', 'official_name:en']
        
        for tag in english_tags:
            if tag in tags and tags[tag].strip():
                return tags[tag].strip()
        
        return None
    
    def _transliterate(self, text: str) -> Optional[str]:
        """
        Transliterate text from Georgian or Cyrillic to Latin.
        
        Returns:
            Transliterated text or None if script not supported
        """
        # Detect script
        if self.georgian_pattern.search(text):
            return self._transliterate_georgian(text)
        elif self.cyrillic_pattern.search(text):
            return self._transliterate_cyrillic(text)
        
        # Already in Latin or unsupported script
        return None
    
    def _transliterate_georgian(self, text: str) -> str:
        """Transliterate Georgian to Latin"""
        result = []
        for char in text:
            if char in self.georgian_map:
                result.append(self.georgian_map[char])
            else:
                result.append(char)
        
        transliterated = ''.join(result)
        # Capitalize first letter
        return transliterated.capitalize() if transliterated else transliterated
    
    def _transliterate_cyrillic(self, text: str) -> str:
        """Transliterate Cyrillic to Latin"""
        result = []
        for char in text:
            if char in self.cyrillic_map:
                result.append(self.cyrillic_map[char])
            else:
                result.append(char)
        
        return ''.join(result)
    
    def get_translation_stats(self, pois: list) -> Dict:
        """
        Get translation statistics for a list of POIs.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'total': len(pois),
            'osm_english': 0,
            'transliterated': 0,
            'failed': 0,
            'already_english': 0
        }
        
        for poi in pois:
            original_name = poi.get('name', '')
            tags = poi.get('tags', {})
            
            # Check if already English
            if re.match(r'^[A-Za-z0-9\s\-\'\.\,\&\(\)]+$', original_name):
                stats['already_english'] += 1
                continue
            
            # Try OSM English name
            if self._get_osm_english_name(tags):
                stats['osm_english'] += 1
                continue
            
            # Try transliteration
            transliterated = self._transliterate(original_name)
            if transliterated and transliterated != original_name:
                stats['transliterated'] += 1
            else:
                stats['failed'] += 1
        
        return stats


# Convenience function
def translate_poi_names(pois: list) -> tuple:
    """
    Translate POI names to English.
    
    Args:
        pois: List of POI dictionaries
    
    Returns:
        (translated_pois, stats) - POIs with English names and translation stats
    """
    translator = NameTranslator()
    translated_pois = []
    
    for poi in pois:
        # Try to get English name
        english_name = translator.translate_poi_name(poi)
        
        if english_name:
            # Update POI with English name
            poi_copy = poi.copy()
            poi_copy['name'] = english_name
            poi_copy['original_name'] = poi.get('name')  # Preserve original
            translated_pois.append(poi_copy)
        else:
            # Keep original if already English or translation succeeded
            original_name = poi.get('name', '')
            if re.match(r'^[A-Za-z0-9\s\-\'\.\,\&\(\)]+$', original_name):
                translated_pois.append(poi)
            # Otherwise, POI will be filtered out by validation
    
    stats = translator.get_translation_stats(pois)
    return translated_pois, stats
