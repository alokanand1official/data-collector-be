#!/usr/bin/env python3
"""Filter to enriched POIs only"""
import json
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Filter to enriched POIs only')
    parser.add_argument('--city', required=True, help='City name (e.g., Baku)')
    parser.add_argument('--input', help='Input file (default: processed_data/{city}_pois_prioritized.json)')
    parser.add_argument('--output', help='Output file (default: processed_data/{city}_pois_enriched_only.json)')
    
    args = parser.parse_args()
    
    city_lower = args.city.lower().replace(' ', '_')
    input_file = args.input or f'processed_data/{city_lower}_pois_prioritized.json'
    output_file = args.output or f'processed_data/{city_lower}_pois_enriched_only.json'
    
    # Check if input exists
    if not Path(input_file).exists():
        print(f'❌ Input file not found: {input_file}')
        exit(1)
    
    # Load POIs
    with open(input_file, 'r', encoding='utf-8') as f:
        pois = json.load(f)
    
    # Filter to enriched only
    enriched = [p for p in pois if p.get('description') and p.get('persona_scores')]
    
    # Save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    
    print(f'✅ Filtered {len(enriched)} enriched POIs from {len(pois)} total')
    print(f'   Saved to: {output_file}')
    
    # Show breakdown by tier
    by_tier = {}
    for poi in enriched:
        tier = poi.get('priority_tier', 'unknown')
        by_tier[tier] = by_tier.get(tier, 0) + 1
    
    print(f'\nBreakdown by tier:')
    for tier, count in sorted(by_tier.items()):
        print(f'  {tier}: {count}')

if __name__ == "__main__":
    main()
