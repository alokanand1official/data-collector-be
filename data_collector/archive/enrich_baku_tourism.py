#!/usr/bin/env python3
"""
Re-enrich Baku destination with comprehensive tourism data
"""

from utils.database import Database
from utils.llm import LocalLLM
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def enrich_baku():
    """Enrich Baku with comprehensive tourism information"""
    
    db = Database(schema='byd_escapism')
    llm = LocalLLM()
    
    # Comprehensive Baku data
    baku_data = {
        "name": "Baku",
        "description": """Baku, the capital of Azerbaijan, is a captivating blend of ancient history and futuristic architecture. The UNESCO-listed Old City (Icherisheher) features the iconic Maiden Tower and Palace of the Shirvanshahs, while modern landmarks like the Flame Towers illuminate the skyline. Stroll along the Caspian Sea Boulevard, explore world-class museums including the Heydar Aliyev Center, and experience vibrant nightlife in this cosmopolitan city where East meets West.""",
        
        "short_description": "Azerbaijan's cosmopolitan capital blending ancient Old City charm with striking modern architecture on the Caspian Sea.",
        
        "vibe_tags": ["Modern", "Historic", "Cosmopolitan", "Nightlife", "Architecture", "Shopping", "Luxury", "Cultural", "Waterfront", "Vibrant"],
        
        "category_tags": ["City Break", "Culture", "History", "Shopping", "Nightlife", "Architecture", "Museums", "Family-Friendly", "Solo-Friendly", "Couples"],
        
        "best_time_to_visit": "April-June and September-October (mild weather, fewer crowds)",
        
        "climate_type": "Semi-arid with hot summers and mild winters",
        
        "budget_range": "moderate",
        "price_per_day_min": 60,
        "price_per_day_max": 150,
        
        "average_trip_duration": 4,
        
        "language": "Azerbaijani (Russian and English widely spoken in tourist areas)",
        "currency": "Azerbaijani Manat (AZN)",
        "time_zone": "UTC+4",
        
        "data_quality_score": 95
    }
    
    logger.info("Updating Baku destination with comprehensive tourism data...")
    
    try:
        # Update in database
        result = db.client.table('destinations').update(baku_data).eq('name', 'Baku').execute()
        
        if result.data:
            logger.info("✅ Successfully enriched Baku destination!")
            logger.info(f"   Description: {len(baku_data['description'])} chars")
            logger.info(f"   Vibe Tags: {len(baku_data['vibe_tags'])} tags")
            logger.info(f"   Category Tags: {len(baku_data['category_tags'])} tags")
            logger.info(f"   Quality Score: {baku_data['data_quality_score']}/100")
        else:
            logger.error("Failed to update Baku")
            
    except Exception as e:
        logger.error(f"Error updating Baku: {e}")
        raise

if __name__ == "__main__":
    enrich_baku()
    print("\n🎉 Baku enrichment complete!")
