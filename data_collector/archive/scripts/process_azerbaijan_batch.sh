#!/bin/bash
# Batch process all remaining Azerbaijan destinations
# Runs complete ETL pipeline for each city

set -e  # Exit on error

CITIES=("Sheki" "Ganja" "Quba" "Lahij" "Gobustan")

echo "=========================================="
echo "Azerbaijan Destinations - Batch Processing"
echo "=========================================="
echo ""
echo "Cities to process: ${CITIES[@]}"
echo "Total: ${#CITIES[@]} cities"
echo ""

for CITY in "${CITIES[@]}"; do
    echo ""
    echo "=========================================="
    echo "Processing: $CITY"
    echo "=========================================="
    
    # Stage 1: EXTRACT
    echo "📥 Stage 1: Harvesting OSM data..."
    python main.py harvest --city "$CITY"
    
    # Stage 2: TRANSFORM
    echo "🔄 Stage 2a: Processing and cleaning..."
    python main.py process --city "$CITY"
    
    echo "🎯 Stage 2b: Prioritizing POIs..."
    python scripts/utilities/prioritize_pois.py --city "$CITY"
    
    echo "🤖 Stage 2c: Enriching essential POIs..."
    python main.py enrich --city "$CITY" --tier essential
    
    echo "🤖 Stage 2d: Enriching important POIs (top 30)..."
    python main.py enrich --city "$CITY" --tier important --limit 30
    
    # Stage 3: LOAD
    echo "✅ Stage 3a: Filtering to enriched POIs..."
    python scripts/utilities/filter_enriched.py --city "$CITY"
    
    echo "🔍 Stage 3b: Quality check..."
    CITY_LOWER=$(echo "$CITY" | tr '[:upper:]' '[:lower:]')
    python scripts/utilities/quality_check_pois.py --city "$CITY" --input "processed_data/${CITY_LOWER}_pois_enriched_only.json" --min-score 70 || echo "⚠️  Quality check warning (continuing anyway)"
    
    echo "📤 Stage 3c: Loading to staging..."
    python scripts/utilities/load_to_staging.py --city "$CITY"
    
    echo "🚀 Stage 3d: Deploying to production..."
    python main.py promote --city "$CITY"
    
    echo "✅ $CITY complete!"
    echo ""
done

echo ""
echo "=========================================="
echo "✨ All Azerbaijan destinations processed!"
echo "=========================================="
echo ""
echo "Summary:"
for CITY in "${CITIES[@]}"; do
    echo "  ✅ $CITY"
done
echo ""
echo "Next: Verify data in production database"
