"""
Data Quality Validator for Tourism POI Pipeline
Ensures only high-quality, English-language data reaches Gold layer
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger("DataQualityValidator")

class DataQualityValidator:
    """
    Validates POI data quality before enrichment.
    Filters out non-English names, invalid data, and low-quality entries.
    """
    
    def __init__(self):
        # English alphabet + common punctuation
        self.english_pattern = re.compile(r'^[A-Za-z0-9\s\-\'\.\,\&\(\)]+$')
        
        # Common non-English scripts to detect
        self.non_english_scripts = {
            'georgian': re.compile(r'[\u10A0-\u10FF]'),  # Georgian
            'cyrillic': re.compile(r'[\u0400-\u04FF]'),  # Russian/Cyrillic
            'arabic': re.compile(r'[\u0600-\u06FF]'),    # Arabic
            'chinese': re.compile(r'[\u4E00-\u9FFF]'),   # Chinese
            'japanese': re.compile(r'[\u3040-\u309F\u30A0-\u30FF]'),  # Japanese
            'korean': re.compile(r'[\uAC00-\uD7AF]'),    # Korean
        }
        
        # Minimum quality thresholds
        self.min_name_length = 2
        self.max_name_length = 100
        
    def validate_poi(self, poi: Dict) -> Tuple[bool, List[str]]:
        """
        Validates a single POI entry.
        
        Returns:
            (is_valid, reasons) - True if valid, False otherwise with rejection reasons
        """
        reasons = []
        
        # 1. Check if name exists
        name = poi.get('name', '').strip()
        if not name:
            reasons.append("Missing name")
            return False, reasons
        
        # 2. Check name length
        if len(name) < self.min_name_length:
            reasons.append(f"Name too short ({len(name)} chars)")
            return False, reasons
        
        if len(name) > self.max_name_length:
            reasons.append(f"Name too long ({len(name)} chars)")
            return False, reasons
        
        # 3. Check if name is in English
        if not self._is_english(name):
            detected_script = self._detect_script(name)
            reasons.append(f"Non-English name (detected: {detected_script})")
            return False, reasons
        
        # 4. Check coordinates validity
        if not self._has_valid_coordinates(poi):
            reasons.append("Invalid or missing coordinates")
            return False, reasons
        
        # 5. Check for required fields
        if not self._has_required_fields(poi):
            reasons.append("Missing required fields")
            return False, reasons
        
        # 6. Check for suspicious patterns
        if self._is_suspicious(name):
            reasons.append("Suspicious name pattern")
            return False, reasons
        
        return True, []
    
    def _is_english(self, text: str) -> bool:
        """Check if text is primarily English characters"""
        # Allow some special characters but text should be mostly English
        return bool(self.english_pattern.match(text))
    
    def _detect_script(self, text: str) -> str:
        """Detect which non-English script is present"""
        for script_name, pattern in self.non_english_scripts.items():
            if pattern.search(text):
                return script_name
        return "unknown"
    
    def _has_valid_coordinates(self, poi: Dict) -> bool:
        """Validate coordinate values"""
        try:
            lat = float(poi.get('lat', 0))
            lon = float(poi.get('lon', 0))
            
            # Check if coordinates are in valid range
            if not (-90 <= lat <= 90):
                return False
            if not (-180 <= lon <= 180):
                return False
            
            # Check if coordinates are not (0, 0) - likely invalid
            if lat == 0 and lon == 0:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    def _has_required_fields(self, poi: Dict) -> bool:
        """Check if POI has all required fields"""
        required_fields = ['name', 'lat', 'lon', 'poi_type']
        return all(field in poi and poi[field] for field in required_fields)
    
    def _is_suspicious(self, name: str) -> bool:
        """Detect suspicious patterns in names"""
        suspicious_patterns = [
            r'^\d+$',  # Only numbers
            r'^[A-Z\s]+$',  # Only uppercase (likely abbreviation or code)
            r'test',  # Test data
            r'unknown',  # Unknown/placeholder
            r'unnamed',  # Unnamed locations
            r'^[a-z]{1,2}$',  # Single/double letter codes
        ]
        
        name_lower = name.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, name_lower):
                return True
        
        return False
    
    def validate_batch(self, pois: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Validate a batch of POIs.
        
        Returns:
            (valid_pois, stats) - List of valid POIs and validation statistics
        """
        valid_pois = []
        stats = {
            'total': len(pois),
            'valid': 0,
            'rejected': 0,
            'rejection_reasons': {}
        }
        
        for poi in pois:
            is_valid, reasons = self.validate_poi(poi)
            
            if is_valid:
                valid_pois.append(poi)
                stats['valid'] += 1
            else:
                stats['rejected'] += 1
                # Track rejection reasons
                for reason in reasons:
                    stats['rejection_reasons'][reason] = stats['rejection_reasons'].get(reason, 0) + 1
                
                # Log rejected POI
                logger.debug(f"Rejected POI: {poi.get('name', 'N/A')} - Reasons: {', '.join(reasons)}")
        
        return valid_pois, stats
    
    def generate_report(self, stats: Dict) -> str:
        """Generate a human-readable validation report"""
        report = f"""
Data Quality Validation Report
{'='*50}

Total POIs Processed: {stats['total']}
Valid POIs: {stats['valid']} ({stats['valid']/stats['total']*100:.1f}%)
Rejected POIs: {stats['rejected']} ({stats['rejected']/stats['total']*100:.1f}%)

Rejection Breakdown:
"""
        for reason, count in sorted(stats['rejection_reasons'].items(), key=lambda x: x[1], reverse=True):
            percentage = count / stats['rejected'] * 100 if stats['rejected'] > 0 else 0
            report += f"  - {reason}: {count} ({percentage:.1f}%)\n"
        
        return report


class EnhancedDataQualityValidator(DataQualityValidator):
    """
    Extended validator with additional quality checks
    """
    
    def __init__(self):
        super().__init__()
        
        # Common English stop words for name validation
        self.common_words = {
            'restaurant', 'cafe', 'hotel', 'museum', 'park', 'church',
            'cathedral', 'mosque', 'temple', 'square', 'street', 'avenue',
            'market', 'shop', 'store', 'center', 'theatre', 'cinema',
            'bar', 'pub', 'club', 'gallery', 'library', 'station'
        }
        
    def validate_poi(self, poi: Dict) -> Tuple[bool, List[str]]:
        """Enhanced validation with additional checks"""
        # Run base validation first
        is_valid, reasons = super().validate_poi(poi)
        
        if not is_valid:
            return False, reasons
        
        # Additional checks
        name = poi.get('name', '').strip()
        
        # 7. Check for meaningful content
        if not self._has_meaningful_content(name):
            reasons.append("Name lacks meaningful content")
            return False, reasons
        
        # 8. Check category validity
        if not self._has_valid_category(poi):
            reasons.append("Invalid or missing category")
            return False, reasons
        
        # 9. Check for duplicate markers
        if self._is_likely_duplicate(poi):
            reasons.append("Likely duplicate entry")
            return False, reasons
        
        return True, []
    
    def _has_meaningful_content(self, name: str) -> bool:
        """Check if name has meaningful content (not just generic terms)"""
        # Name should have at least one word that's not just a common term
        words = name.lower().split()
        
        # If name is just one common word, it's probably not specific enough
        if len(words) == 1 and words[0] in self.common_words:
            return False
        
        return True
    
    def _has_valid_category(self, poi: Dict) -> bool:
        """Validate POI category/type"""
        poi_type = poi.get('poi_type', '').strip()
        
        if not poi_type:
            return False
        
        # Category should be in English
        if not self._is_english(poi_type):
            return False
        
        return True
    
    def _is_likely_duplicate(self, poi: Dict) -> bool:
        """Detect likely duplicate entries"""
        # Check for duplicate indicators in name
        name = poi.get('name', '').lower()
        
        duplicate_indicators = [
            r'\(duplicate\)',
            r'\(copy\)',
            r'\(2\)',
            r'\(old\)',
        ]
        
        for pattern in duplicate_indicators:
            if re.search(pattern, name):
                return True
        
        return False


# Convenience function for quick validation
def validate_pois(pois: List[Dict], enhanced: bool = True) -> Tuple[List[Dict], Dict]:
    """
    Validate a list of POIs.
    
    Args:
        pois: List of POI dictionaries
        enhanced: Use enhanced validator (default: True)
    
    Returns:
        (valid_pois, stats) - Filtered POIs and validation statistics
    """
    validator = EnhancedDataQualityValidator() if enhanced else DataQualityValidator()
    return validator.validate_batch(pois)
