#!/usr/bin/env python3
"""
POI Prioritization System
Scores and ranks POIs by tourism importance for intelligent enrichment
"""

import json
import logging
from pathlib import Path
from typing import List, Dict
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class POIPrioritizer:
    """Scores and prioritizes POIs for tourism/itinerary planning"""
    
    # POI Type Weights (out of 40 points)
    POI_TYPE_WEIGHTS = {
        'museum': 40,
        'historic': 38,
        'viewpoint': 35,
        'temple': 33,
        'park': 30,
        'market': 28,
        'monument': 25,
        'beach': 25,
        'attraction': 35,
        'castle': 38,
        'gallery': 35,
        'zoo': 30,
        'aquarium': 30,
        'theme_park': 28,
        'restaurant': 10,  # Generic restaurants
        'cafe': 8,
        'hotel': 15,
        'shop': 5,
        'service': 3,
    }
    
    # Special keywords that boost priority
    IMPORTANCE_KEYWORDS = {
        'unesco': 20,
        'world heritage': 20,
        'national': 15,
        'state': 15,
        'famous': 10,
        'popular': 10,
        'old': 8,
        'ancient': 8,
        'historic': 8,
        'museum': 5,
        'gallery': 5,
        'palace': 12,
        'tower': 10,
        'cathedral': 10,
        'mosque': 10,
        'synagogue': 10,
        'church': 8,
    }
    
    def __init__(self):
        self.stats = {
            'total_pois': 0,
            'essential': 0,
            'important': 0,
            'recommended': 0,
            'optional': 0,
            'low_priority': 0
        }
    
    def score_poi(self, poi: Dict) -> int:
        """Calculate priority score for a POI (0-100)"""
        score = 0
        
        # 1. POI Type Weight (40 points)
        poi_type = poi.get('poi_type', '').lower()
        score += self.POI_TYPE_WEIGHTS.get(poi_type, 5)
        
        # 2. Name Quality (20 points)
        name = poi.get('name', '')
        name_local = poi.get('name_local', '')
        
        if name and len(name) > 5:
            score += 10  # Has meaningful English name
        if name_local and name_local != name:
            score += 5  # Has local name
        if len(name) > 10:
            score += 5  # Longer names often indicate importance
        
        # 3. OSM Tags Richness (20 points)
        metadata = poi.get('metadata', {})
        osm_tags = metadata.get('osm_tags', {})
        
        if osm_tags.get('description'):
            score += 5
        if osm_tags.get('opening_hours'):
            score += 5
        if osm_tags.get('website') or osm_tags.get('contact:website'):
            score += 5
        if osm_tags.get('phone') or osm_tags.get('contact:phone'):
            score += 3
        if osm_tags.get('wikipedia') or osm_tags.get('wikidata'):
            score += 2
        
        # 4. Category Importance (20 points)
        # Check for special keywords in name and tags
        search_text = f"{name} {name_local} {str(osm_tags)}".lower()
        
        keyword_bonus = 0
        for keyword, bonus in self.IMPORTANCE_KEYWORDS.items():
            if keyword in search_text:
                keyword_bonus = max(keyword_bonus, bonus)  # Take highest match
        
        score += keyword_bonus
        
        # Cap at 100
        return min(score, 100)
    
    def get_priority_tier(self, score: int) -> str:
        """Determine priority tier based on score"""
        if score >= 80:
            return 'essential'
        elif score >= 60:
            return 'important'
        elif score >= 40:
            return 'recommended'
        elif score >= 20:
            return 'optional'
        else:
            return 'low_priority'
    
    def get_enrichment_priority(self, tier: str) -> int:
        """Get enrichment priority (1=highest, 5=lowest)"""
        tier_priority = {
            'essential': 1,
            'important': 2,
            'recommended': 3,
            'optional': 4,
            'low_priority': 5
        }
        return tier_priority.get(tier, 5)
    
    def prioritize_pois(self, pois: List[Dict]) -> List[Dict]:
        """Score and prioritize all POIs"""
        logger.info(f"Prioritizing {len(pois)} POIs...")
        
        self.stats['total_pois'] = len(pois)
        
        for poi in pois:
            # Calculate score
            score = self.score_poi(poi)
            tier = self.get_priority_tier(score)
            enrichment_priority = self.get_enrichment_priority(tier)
            
            # Add priority fields
            poi['priority_score'] = score
            poi['priority_tier'] = tier
            poi['enrichment_priority'] = enrichment_priority
            
            # Update stats
            self.stats[tier] = self.stats.get(tier, 0) + 1
        
        # Sort by priority score (highest first)
        pois_sorted = sorted(pois, key=lambda x: x['priority_score'], reverse=True)
        
        return pois_sorted
    
    def print_stats(self):
        """Print prioritization statistics"""
        logger.info("\n" + "="*70)
        logger.info("POI PRIORITIZATION STATISTICS")
        logger.info("="*70)
        logger.info(f"\nTotal POIs: {self.stats['total_pois']}")
        logger.info(f"\nBy Priority Tier:")
        logger.info(f"  Essential (80-100):    {self.stats['essential']:4} POIs - ENRICH ALL")
        logger.info(f"  Important (60-79):     {self.stats['important']:4} POIs - ENRICH TOP 50-100")
        logger.info(f"  Recommended (40-59):   {self.stats['recommended']:4} POIs - ENRICH TOP 50")
        logger.info(f"  Optional (20-39):      {self.stats['optional']:4} POIs - SKIP")
        logger.info(f"  Low Priority (0-19):   {self.stats['low_priority']:4} POIs - SKIP")
        logger.info("="*70)
    
    def print_top_pois(self, pois: List[Dict], count: int = 50):
        """Print top N POIs for verification"""
        logger.info(f"\n{'='*70}")
        logger.info(f"TOP {count} HIGHEST PRIORITY POIs")
        logger.info(f"{'='*70}\n")
        
        for i, poi in enumerate(pois[:count], 1):
            logger.info(f"{i:2}. [{poi['priority_score']:3}] {poi['name']:50} ({poi['poi_type']})")
            if poi['priority_tier'] == 'essential':
                logger.info(f"    ⭐ ESSENTIAL - Must enrich")

def main():
    parser = argparse.ArgumentParser(description='Prioritize POIs by tourism importance')
    parser.add_argument('--city', required=True, help='City name (e.g., Baku)')
    parser.add_argument('--input', help='Input file (default: processed_data/{city}_pois.json)')
    parser.add_argument('--output', help='Output file (default: processed_data/{city}_pois_prioritized.json)')
    parser.add_argument('--top', type=int, default=50, help='Number of top POIs to display')
    
    args = parser.parse_args()
    
    # Determine file paths
    city_lower = args.city.lower().replace(' ', '_')
    input_file = args.input or f'processed_data/{city_lower}_pois.json'
    output_file = args.output or f'processed_data/{city_lower}_pois_prioritized.json'
    
    # Load POIs
    logger.info(f"Loading POIs from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        pois = json.load(f)
    
    # Prioritize
    prioritizer = POIPrioritizer()
    pois_prioritized = prioritizer.prioritize_pois(pois)
    
    # Save
    logger.info(f"\nSaving prioritized POIs to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pois_prioritized, f, ensure_ascii=False, indent=2)
    
    # Print statistics
    prioritizer.print_stats()
    prioritizer.print_top_pois(pois_prioritized, args.top)
    
    logger.info(f"\n✅ Prioritization complete!")
    logger.info(f"   Input: {len(pois)} POIs")
    logger.info(f"   Output: {len(pois_prioritized)} POIs (sorted by priority)")
    logger.info(f"   Essential POIs: {prioritizer.stats['essential']}")
    logger.info(f"   Ready for tiered enrichment!")

if __name__ == "__main__":
    main()
