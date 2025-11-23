"""
Quick Start Test Script
Tests all components of the data collector
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...\n")
    
    checks = {
        "overpy": False,
        "yaml": False,
        "langchain_ollama": False,
        "supabase": False,
        "dotenv": False,
    }
    
    for package in checks.keys():
        try:
            __import__(package)
            checks[package] = True
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} NOT installed")
    
    print()
    
    if not all(checks.values()):
        print("⚠️  Missing packages. Install with:")
        print("pip install -r requirements.txt")
        return False
    
    # Check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("SUPABASE_URL"):
        print("❌ SUPABASE_URL not set in .env file")
        return False
    else:
        print("✅ SUPABASE_URL configured")
    
    if not os.getenv("SUPABASE_KEY"):
        print("❌ SUPABASE_KEY not set in .env file")
        return False
    else:
        print("✅ SUPABASE_KEY configured")
    
    print("\n✅ All requirements met!\n")
    return True


def test_database():
    """Test database connection"""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60 + "\n")
    
    try:
        from utils.database import db
        
        # Test query
        result = db.client.table('countries').select('code, name').limit(3).execute()
        
        print(f"✅ Connected to Supabase (byd_escapism schema)")
        print(f"Found {len(result.data)} countries:")
        for country in result.data:
            print(f"  - {country['name']} ({country['code']})")
        print()
        
        return True
    
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nMake sure:")
        print("  1. .env file exists with SUPABASE_URL and SUPABASE_KEY")
        print("  2. Database schema is installed (run data_collection_schema_v2.sql)")
        print()
        return False


def test_osm_collector():
    """Test OpenStreetMap collector"""
    print("=" * 60)
    print("Testing OpenStreetMap Collector")
    print("=" * 60 + "\n")
    
    try:
        from sources.osm import OSMCollector
        
        collector = OSMCollector()
        
        print("Collecting 3 temples in Chiang Mai...")
        pois = collector.collect_pois_in_province(
            province_name="Chiang Mai",
            poi_type="temple",
            country_code="TH",
            limit=3
        )
        
        print(f"\n✅ Collected {len(pois)} temples\n")
        
        if pois:
            poi = pois[0]
            print("Example POI:")
            print(f"  Name: {poi['name']}")
            print(f"  Type: {poi['poi_type']}")
            print(f"  Coordinates: {poi['coordinates']}")
            print(f"  OSM ID: {poi.get('osm_id')}")
            print()
        
        return True
    
    except Exception as e:
        print(f"❌ OSM test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm():
    """Test local LLM (Ollama)"""
    print("=" * 60)
    print("Testing Local LLM (Ollama)")
    print("=" * 60 + "\n")
    
    try:
        from utils.llm import LocalLLM
        
        print("Initializing Llama 3.1 8B...")
        llm = LocalLLM(model="llama-3.1-8b")
        
        print("✅ LLM initialized\n")
        
        # Test persona scoring
        poi_data = {
            'name': 'Wat Phra That Doi Suthep',
            'poi_type': 'temple',
            'description': 'Sacred Buddhist temple on mountain overlooking Chiang Mai'
        }
        
        personas = [
            {'id': 'cultural_explorer', 'keywords': ['temple', 'historical', 'cultural']},
            {'id': 'adventure_seeker', 'keywords': ['hiking', 'adventure', 'mountain']},
            {'id': 'wellness_retreater', 'keywords': ['meditation', 'peaceful', 'spiritual']},
        ]
        
        print("Scoring POI for personas...")
        scores = llm.score_poi_for_personas(poi_data, personas)
        
        print("\n✅ Persona Scores:")
        for persona_id, score in scores.items():
            print(f"  {persona_id}: {score}/100")
        
        print()
        return True
    
    except Exception as e:
        print(f"❌ Error testing LLM: {e}")
        print("\nMake sure Ollama is running:")
        print("  1. Install: curl -fsSL https://ollama.com/install.sh | sh")
        print("  2. Pull model: ollama pull llama-3.1-8b")
        print("  3. Start server: ollama serve")
        print()
        return False


def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print(" BeyondEscapism Data Collector - Quick Start")
    print("=" * 60 + "\n")
    
    # Check requirements
    if not check_requirements():
        print("❌ Setup incomplete. Please install missing requirements.\n")
        return
    
    # Test components
    print("\n🧪 Testing Components...\n")
    
    # 1. Test database
    db_ok = test_database()
    
    if not db_ok:
        print("❌ Cannot proceed without database connection\n")
        return
    
    # 2. Test OSM
    osm_ok = test_osm_collector()
    
    # 3. Test LLM (optional)
    llm_ok = test_llm()
    
    if not llm_ok:
        print("⚠️  LLM test failed. You can still collect data, but won't have AI enrichment\n")
    
    # Success!
    if db_ok and osm_ok:
        print("\n" + "=" * 60)
        print("✅ ALL CORE TESTS PASSED!")
        print("=" * 60)
        print("\nYou're ready to start collecting data! 🎉")
        print("\nNext steps:")
        print("  1. Run: python collect_thailand.py")
        print("  2. Monitor progress in Supabase")
        print()
    else:
        print("\n❌ Some tests failed. Please fix the issues above.\n")


if __name__ == "__main__":
    main()
