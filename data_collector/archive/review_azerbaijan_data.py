#!/usr/bin/env python3
"""
Review current Azerbaijan destination data
"""
from utils.database import Database
import json

db = Database(schema='byd_escapism')
result = db.client.table('destinations').select('*').eq('country', 'Azerbaijan').order('name').execute()

print('='*70)
print('CURRENT AZERBAIJAN DESTINATION DATA REVIEW')
print('='*70)
print(f'\nTotal Destinations: {len(result.data)}\n')

for dest in result.data:
    print(f'\n📍 {dest["name"].upper()}')
    print(f'   Coordinates: {dest.get("coordinates")}')
    desc = dest.get("description", "N/A")
    print(f'   Description: {desc[:150] if desc != "N/A" else "N/A"}...')
    print(f'   Short Desc: {dest.get("short_description", "N/A")}')
    print(f'   Vibe Tags: {dest.get("vibe_tags", [])}')
    print(f'   Category Tags: {dest.get("category_tags", [])}')
    print(f'   Budget: {dest.get("budget_range", "N/A")} (${dest.get("price_per_day_min")}-${dest.get("price_per_day_max")}/day)')
    print(f'   Trip Duration: {dest.get("average_trip_duration", "N/A")} days')
    print(f'   Best Time: {dest.get("best_time_to_visit", "N/A")}')
    print(f'   Climate: {dest.get("climate_type", "N/A")}')
    print(f'   Image: {"✅" if dest.get("image_url") else "❌ Missing"}')
    print(f'   Quality Score: {dest.get("data_quality_score", "N/A")}/100')

print('\n' + '='*70)
print('DATA QUALITY ANALYSIS')
print('='*70)

# Analyze completeness
total = len(result.data)
with_images = sum(1 for d in result.data if d.get('image_url'))
with_descriptions = sum(1 for d in result.data if d.get('description') and len(d.get('description', '')) > 50)
with_vibe_tags = sum(1 for d in result.data if d.get('vibe_tags') and len(d.get('vibe_tags', [])) > 0)
with_best_time = sum(1 for d in result.data if d.get('best_time_to_visit'))

print(f'\nCompleteness Metrics:')
print(f'  Images: {with_images}/{total} ({with_images/total*100:.0f}%)')
print(f'  Descriptions: {with_descriptions}/{total} ({with_descriptions/total*100:.0f}%)')
print(f'  Vibe Tags: {with_vibe_tags}/{total} ({with_vibe_tags/total*100:.0f}%)')
print(f'  Best Time to Visit: {with_best_time}/{total} ({with_best_time/total*100:.0f}%)')

print('\n' + '='*70)
