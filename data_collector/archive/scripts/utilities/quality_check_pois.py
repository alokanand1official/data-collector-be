#!/usr/bin/env python3
"""
Data Quality Checker for POIs
Validates enriched POI data before database loading
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class POIQualityChecker:
    """Validates POI data quality before database loading"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.stats = {
            'total_pois': 0,
            'enriched_pois': 0,
            'valid_pois': 0,
            'invalid_pois': 0,
            'missing_descriptions': 0,
            'missing_persona_scores': 0,
            'invalid_coordinates': 0,
            'duplicate_osm_ids': 0,
        }
    
    def check_required_fields(self, poi: Dict) -> List[str]:
        """Check if POI has all required fields"""
        issues = []
        required_fields = ['name', 'poi_type', 'coordinates', 'osm_id', 'city_name']
        
        for field in required_fields:
            if not poi.get(field):
                issues.append(f"Missing required field: {field}")
        
        return issues
    
    def check_coordinates(self, poi: Dict) -> List[str]:
        """Validate coordinates"""
        issues = []
        coords = poi.get('coordinates', {})
        
        if not isinstance(coords, dict):
            issues.append("Coordinates is not a dictionary")
            return issues
        
        lat = coords.get('lat')
        lng = coords.get('lng')
        
        if lat is None or lng is None:
            issues.append("Missing lat or lng in coordinates")
        elif not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            issues.append("Lat/lng are not numbers")
        elif not (-90 <= lat <= 90):
            issues.append(f"Invalid latitude: {lat}")
        elif not (-180 <= lng <= 180):
            issues.append(f"Invalid longitude: {lng}")
        
        return issues
    
    def check_enrichment_quality(self, poi: Dict) -> List[str]:
        """Check quality of AI enrichment"""
        warnings = []
        
        # Check description
        description = poi.get('description', '')
        if not description:
            warnings.append("Missing description")
        elif len(description) < 20:
            warnings.append(f"Description too short ({len(description)} chars)")
        elif len(description) > 500:
            warnings.append(f"Description too long ({len(description)} chars)")
        
        # Check persona scores
        persona_scores = poi.get('persona_scores', {})
        if not persona_scores:
            warnings.append("Missing persona scores")
        else:
            # Check if scores are reasonable (0-100)
            for persona, score in persona_scores.items():
                if not isinstance(score, (int, float)):
                    warnings.append(f"Invalid persona score type for {persona}")
                elif not (0 <= score <= 100):
                    warnings.append(f"Persona score out of range for {persona}: {score}")
        
        return warnings
    
    def check_duplicates(self, pois: List[Dict]) -> List[str]:
        """Check for duplicate OSM IDs"""
        issues = []
        osm_ids = {}
        
        for i, poi in enumerate(pois):
            osm_id = poi.get('osm_id')
            if osm_id in osm_ids:
                issues.append(f"Duplicate OSM ID: {osm_id} (indices {osm_ids[osm_id]} and {i})")
            else:
                osm_ids[osm_id] = i
        
        return issues
    
    def validate_pois(self, pois: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Validate all POIs and return valid ones with quality report
        
        Returns:
            (valid_pois, quality_report)
        """
        logger.info(f"Validating {len(pois)} POIs...")
        
        self.stats['total_pois'] = len(pois)
        valid_pois = []
        
        # Check for duplicates
        duplicate_issues = self.check_duplicates(pois)
        if duplicate_issues:
            self.stats['duplicate_osm_ids'] = len(duplicate_issues)
            for issue in duplicate_issues:
                self.issues.append(f"DUPLICATE: {issue}")
        
        # Validate each POI
        for i, poi in enumerate(pois):
            poi_issues = []
            poi_warnings = []
            
            # Check required fields
            field_issues = self.check_required_fields(poi)
            poi_issues.extend(field_issues)
            
            # Check coordinates
            coord_issues = self.check_coordinates(poi)
            poi_issues.extend(coord_issues)
            if coord_issues:
                self.stats['invalid_coordinates'] += 1
            
            # Check enrichment quality
            enrichment_warnings = self.check_enrichment_quality(poi)
            poi_warnings.extend(enrichment_warnings)
            
            # Track enrichment status
            if poi.get('description') and poi.get('persona_scores'):
                self.stats['enriched_pois'] += 1
            else:
                if not poi.get('description'):
                    self.stats['missing_descriptions'] += 1
                if not poi.get('persona_scores'):
                    self.stats['missing_persona_scores'] += 1
            
            # Determine if POI is valid
            if poi_issues:
                self.stats['invalid_pois'] += 1
                for issue in poi_issues:
                    self.issues.append(f"POI #{i} ({poi.get('name', 'UNKNOWN')}): {issue}")
            else:
                self.stats['valid_pois'] += 1
                valid_pois.append(poi)
                
                # Log warnings for valid POIs
                for warning in poi_warnings:
                    self.warnings.append(f"POI #{i} ({poi.get('name', 'UNKNOWN')}): {warning}")
        
        return valid_pois, self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate quality report"""
        return {
            'stats': self.stats,
            'issues': self.issues,
            'warnings': self.warnings,
            'quality_score': self.calculate_quality_score()
        }
    
    def calculate_quality_score(self) -> int:
        """Calculate overall quality score (0-100)"""
        if self.stats['total_pois'] == 0:
            return 0
        
        # Base score from valid POIs
        valid_ratio = self.stats['valid_pois'] / self.stats['total_pois']
        score = valid_ratio * 50  # 50 points for validity
        
        # Bonus for enrichment
        if self.stats['valid_pois'] > 0:
            enriched_ratio = self.stats['enriched_pois'] / self.stats['valid_pois']
            score += enriched_ratio * 50  # 50 points for enrichment
        
        return int(score)
    
    def print_report(self, report: Dict):
        """Print quality report"""
        logger.info("\n" + "="*70)
        logger.info("POI QUALITY REPORT")
        logger.info("="*70)
        
        stats = report['stats']
        logger.info(f"\nTotal POIs: {stats['total_pois']}")
        logger.info(f"Valid POIs: {stats['valid_pois']} ({stats['valid_pois']/stats['total_pois']*100:.1f}%)")
        logger.info(f"Invalid POIs: {stats['invalid_pois']}")
        logger.info(f"Enriched POIs: {stats['enriched_pois']} ({stats['enriched_pois']/stats['total_pois']*100:.1f}%)")
        
        logger.info(f"\nQuality Issues:")
        logger.info(f"  Missing descriptions: {stats['missing_descriptions']}")
        logger.info(f"  Missing persona scores: {stats['missing_persona_scores']}")
        logger.info(f"  Invalid coordinates: {stats['invalid_coordinates']}")
        logger.info(f"  Duplicate OSM IDs: {stats['duplicate_osm_ids']}")
        
        logger.info(f"\n{'='*70}")
        logger.info(f"OVERALL QUALITY SCORE: {report['quality_score']}/100")
        logger.info(f"{'='*70}")
        
        if report['issues']:
            logger.warning(f"\n⚠️  {len(report['issues'])} CRITICAL ISSUES FOUND:")
            for issue in report['issues'][:10]:  # Show first 10
                logger.warning(f"  - {issue}")
            if len(report['issues']) > 10:
                logger.warning(f"  ... and {len(report['issues']) - 10} more")
        
        if report['warnings']:
            logger.info(f"\n⚠️  {len(report['warnings'])} WARNINGS:")
            for warning in report['warnings'][:10]:  # Show first 10
                logger.info(f"  - {warning}")
            if len(report['warnings']) > 10:
                logger.info(f"  ... and {len(report['warnings']) - 10} more")
        
        # Recommendation
        logger.info(f"\n{'='*70}")
        if report['quality_score'] >= 80:
            logger.info("✅ RECOMMENDATION: Data quality is GOOD. Safe to load to database.")
        elif report['quality_score'] >= 60:
            logger.info("⚠️  RECOMMENDATION: Data quality is ACCEPTABLE. Review warnings before loading.")
        else:
            logger.info("❌ RECOMMENDATION: Data quality is POOR. Fix issues before loading!")
        logger.info(f"{'='*70}\n")

def main():
    parser = argparse.ArgumentParser(description='Validate POI data quality')
    parser.add_argument('--city', required=True, help='City name (e.g., Baku)')
    parser.add_argument('--input', help='Input file (default: processed_data/{city}_pois_prioritized.json)')
    parser.add_argument('--output', help='Output file for valid POIs (default: same as input)')
    parser.add_argument('--min-score', type=int, default=60, help='Minimum quality score to pass (default: 60)')
    
    args = parser.parse_args()
    
    # Determine file paths
    city_lower = args.city.lower().replace(' ', '_')
    input_file = args.input or f'processed_data/{city_lower}_pois_prioritized.json'
    output_file = args.output or input_file
    
    # Load POIs
    logger.info(f"Loading POIs from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        pois = json.load(f)
    
    # Validate
    checker = POIQualityChecker()
    valid_pois, report = checker.validate_pois(pois)
    
    # Print report
    checker.print_report(report)
    
    # Save valid POIs if different from input
    if output_file != input_file:
        logger.info(f"\nSaving {len(valid_pois)} valid POIs to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(valid_pois, f, indent=2, ensure_ascii=False)
    
    # Exit with appropriate code
    if report['quality_score'] < args.min_score:
        logger.error(f"\n❌ Quality score {report['quality_score']} is below minimum {args.min_score}")
        logger.error("Fix issues before loading to database!")
        exit(1)
    else:
        logger.info(f"\n✅ Quality check passed! Score: {report['quality_score']}/100")
        logger.info(f"Ready to load {len(valid_pois)} POIs to database.")
        exit(0)

if __name__ == "__main__":
    main()
