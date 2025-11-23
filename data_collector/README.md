# BeyondEscapism Data Collector

Standalone Python application for collecting and enriching travel data from free sources (OpenStreetMap, Wikidata) using local AI. This service populates the BeyondEscapism database with high-quality POIs (Points of Interest), attractions, and travel destinations.

## Features

- 🌍 **Free Data Sources**: Collect POIs from OpenStreetMap (100% FREE)
- 🤖 **Local AI Enrichment**: Enrich with Ollama local LLM (no API costs)
- 🎯 **Persona Scoring**: Score POIs for 6 travel personas (Adventure, Culture, Relaxation, Food, Nature, Luxury)
- 📊 **Quality Validation**: Automatic data validation and quality checks
- 💾 **Database Integration**: Direct upload to Supabase database
- 🔄 **Deduplication**: Smart deduplication to avoid duplicate entries
- 📈 **Progress Tracking**: Real-time collection progress monitoring
- 🌏 **Multi-Country Support**: Pre-configured for Thailand, India, Vietnam, and more

## Tech Stack

- **Language**: Python 3.11+
- **Data Sources**: OpenStreetMap (Overpass API), Wikidata
- **AI/LLM**: Ollama (local LLM - llama-3.1-8b)
- **Database**: Supabase (PostgreSQL)
- **Configuration**: YAML files
- **Environment**: dotenv for configuration

## Project Structure

```
data_collector/
├── README.md                # This file
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Your environment variables (create this)
├── setup.sh                # Setup script
├── quickstart.py           # Quick test script
├── collect_thailand.py     # Thailand collection script
├── collect_cities.py       # Multi-city collection script
├── generate_sample_data.py # Generate sample data
├── test_osm.py            # Test OpenStreetMap API
├── debug_osm.py           # Debug OSM queries
├── config/                 # Configuration files
│   ├── countries/          # Country-specific configs
│   │   ├── thailand.yaml
│   │   ├── india.yaml
│   │   └── vietnam.yaml
│   └── data_types/         # POI type configs
│       └── pois.yaml
├── sources/                # Data source collectors
│   ├── osm.py             # OpenStreetMap collector
│   └── wikidata.py        # Wikidata enrichment
├── agents/                 # AI agent modules
│   └── enrichment.py      # LLM enrichment agent
├── utils/                  # Utility modules
│   ├── llm.py             # Local LLM interface
│   ├── deduplication.py   # Deduplication logic
│   └── database.py        # Database operations
├── logs/                   # Log files (auto-generated)
└── output/                 # Temporary output files
```

## Prerequisites

- Python 3.11 or higher
- Ollama (for local LLM)
- Supabase account
- 8GB+ RAM (16GB+ recommended)
- Stable internet connection

## Installation

### 1. Quick Setup (Recommended)

```bash
# Navigate to data_collector directory
cd data_collector

# Run setup script (installs everything)
chmod +x setup.sh
./setup.sh
```

### 2. Manual Setup

#### Step 2.1: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### Step 2.2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Step 2.3: Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

#### Step 2.4: Pull LLM Model

```bash
# Start Ollama service (if not running)
ollama serve

# In another terminal, pull the model
ollama pull llama-3.1-8b
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama-3.1-8b

# Collection Settings
BATCH_SIZE=50
RATE_LIMIT_DELAY=2
```

## Usage

### Quick Test (5 minutes)

Test the entire pipeline with a small dataset:

```bash
python quickstart.py
```

This will:
1. Fetch 10 POIs from OpenStreetMap
2. Enrich them with local LLM
3. Score for travel personas
4. Upload to Supabase
5. Show progress and results

### Collect Country Data

#### Thailand

```bash
python collect_thailand.py
```

Collects data for all 77 provinces in Thailand.

#### Custom Cities

```bash
python collect_cities.py
```

Edit the script to specify cities you want to collect.

### Generate Sample Data

```bash
python generate_sample_data.py
```

Generates sample POI data for testing without API calls.

## Collection Scripts Explained

### quickstart.py
Quick test script that collects a small sample to verify setup.

**Usage:**
```bash
python quickstart.py
```

**Output:**
- 10 POIs from Bangkok, Thailand
- Enriched with AI descriptions
- Persona scores
- Saved to `sample_pois.json`

### collect_thailand.py
Complete data collection for Thailand's 77 provinces.

**Usage:**
```bash
python collect_thailand.py
```

**Features:**
- Province-by-province collection
- Automatic rate limiting
- Progress tracking
- Resume capability
- Database upload

**Estimated Time:** 5-7 days (MacBook Pro 24GB)

### collect_cities.py
Flexible multi-city collection script.

**Usage:**
```bash
# Edit script to add cities, then run:
python collect_cities.py
```

**Example cities:**
```python
cities = [
    {"name": "New York", "country": "USA", "bbox": [...]},
    {"name": "London", "country": "UK", "bbox": [...]},
]
```

## Configuration Files

### Country Configuration (config/countries/thailand.yaml)

```yaml
country:
  code: "TH"
  name: "Thailand"
  regions:
    - name: "Bangkok"
      type: "province"
      bbox: [100.3315, 13.4930, 100.9380, 13.9555]
      poi_types:
        - temples
        - markets
        - restaurants
```

### POI Types Configuration (config/data_types/pois.yaml)

```yaml
poi_types:
  temple:
    osm_tags:
      - amenity=place_of_worship
      - building=temple
    persona_affinity:
      culture: 0.9
      spiritual: 0.8

  restaurant:
    osm_tags:
      - amenity=restaurant
    persona_affinity:
      food: 0.9
      social: 0.7
```

## AI Enrichment

The data collector uses Ollama (local LLM) to enrich POI data:

### Enrichment Process

1. **Data Collection**: Fetch raw POI data from OSM
2. **LLM Processing**: Send to Ollama for enrichment
3. **Persona Scoring**: Score for 6 travel personas
4. **Quality Validation**: Validate enriched data
5. **Database Upload**: Save to Supabase

### Supported Personas

- **Adventure Seeker**: Outdoor activities, extreme sports
- **Culture Enthusiast**: Museums, temples, historical sites
- **Relaxation Seeker**: Spas, beaches, quiet cafes
- **Food Explorer**: Restaurants, markets, food tours
- **Nature Lover**: Parks, gardens, natural attractions
- **Luxury Traveler**: High-end hotels, fine dining, exclusive experiences

### Example Enrichment

**Input (Raw OSM):**
```json
{
  "name": "Wat Phra Kaew",
  "type": "temple",
  "lat": 13.7508,
  "lon": 100.4920
}
```

**Output (Enriched):**
```json
{
  "name": "Wat Phra Kaew (Temple of the Emerald Buddha)",
  "type": "temple",
  "lat": 13.7508,
  "lon": 100.4920,
  "description": "The most sacred Buddhist temple in Thailand, home to the Emerald Buddha...",
  "highlights": [
    "Emerald Buddha statue",
    "Grand Palace complex",
    "Intricate architecture"
  ],
  "best_time": "Early morning (8-10 AM) to avoid crowds",
  "avg_duration": "2-3 hours",
  "persona_scores": {
    "culture": 0.95,
    "spiritual": 0.90,
    "photography": 0.85
  }
}
```

## Database Schema

The collector uploads data to the `byd_escapism` schema in Supabase:

### Tables

- `pois`: Points of Interest
- `cities`: City information
- `regions`: Region/province data
- `data_collection_jobs`: Collection tracking
- `poi_enrichment_logs`: Enrichment audit trail

## Monitoring Progress

### Real-time Logs

```bash
# Watch logs in real-time
tail -f logs/collection_$(date +%Y%m%d).log
```

### Database Queries

```sql
-- Overall progress
SELECT * FROM byd_escapism.v_country_collection_progress;

-- Recent collection jobs
SELECT * FROM byd_escapism.data_collection_jobs
ORDER BY created_at DESC
LIMIT 10;

-- POI counts by country
SELECT country_code, COUNT(*) as total_pois
FROM byd_escapism.pois
GROUP BY country_code;

-- POI counts by type
SELECT poi_type, COUNT(*) as count
FROM byd_escapism.pois
WHERE country_code = 'TH'
GROUP BY poi_type
ORDER BY count DESC;
```

## Performance Metrics

### Hardware Requirements

| Hardware | Collection Rate | Thailand (77 provinces) |
|----------|----------------|------------------------|
| MacBook Pro M1 (24GB) | 250-300 POIs/hour | ~7 days |
| MacBook Air M2 (16GB) | 200-250 POIs/hour | ~9 days |
| Google Colab (Free GPU) | 400-500 POIs/hour | ~4 days |
| Desktop (32GB, GPU) | 500-600 POIs/hour | ~3 days |

### Optimization Tips

1. **Increase Batch Size**: Edit `.env`
   ```env
   BATCH_SIZE=100  # Increase from 50
   ```

2. **Reduce Rate Limit**: Only if you have premium API access
   ```env
   RATE_LIMIT_DELAY=1  # Decrease from 2
   ```

3. **Use GPU**: Ollama automatically uses GPU if available

4. **Parallel Processing**: Run multiple collectors for different regions

## Cost Breakdown

**Total Cost: $0/month** 🎉

- **OpenStreetMap**: Free, unlimited
- **Wikidata**: Free, unlimited
- **Ollama**: Free, runs locally
- **Supabase**: Free tier (500MB database)

**Comparison with Commercial APIs:**

| Service | Monthly Cost (for Thailand data) |
|---------|--------------------------------|
| Google Places API | ~$5,000 |
| Foursquare API | ~$3,500 |
| **This Solution** | **$0** |

## Troubleshooting

### Ollama Not Running

```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve

# Test Ollama
curl http://localhost:11434/api/tags
```

### Model Not Found

```bash
# List installed models
ollama list

# Pull the model
ollama pull llama-3.1-8b
```

### Rate Limiting from OSM

The collector automatically respects rate limits. If you see errors:

1. Increase delay in `.env`:
   ```env
   RATE_LIMIT_DELAY=5  # Increase from 2
   ```

2. Check OSM status: https://status.openstreetmap.org/

### Database Connection Errors

```bash
# Test Supabase connection
python test_supabase.py

# Verify credentials
python validate_env.py
```

### Memory Issues

If running out of memory:

1. Reduce batch size:
   ```env
   BATCH_SIZE=25  # Reduce from 50
   ```

2. Use smaller LLM model:
   ```bash
   ollama pull llama-3.1-7b
   ```

3. Increase system swap space

### Collection Stuck/Hanging

```bash
# Check logs
tail -f logs/collection_*.log

# Kill and restart
pkill -f collect_thailand.py
python collect_thailand.py
```

## Advanced Usage

### Custom Region Collection

```python
from sources.osm import OSMCollector
from utils.database import upload_to_supabase

collector = OSMCollector()
pois = collector.collect_region(
    bbox=[100.3315, 13.4930, 100.9380, 13.9555],
    poi_types=["temple", "restaurant", "market"]
)

upload_to_supabase(pois, schema="byd_escapism")
```

### Custom Enrichment

```python
from agents.enrichment import enrich_poi
from utils.llm import get_llm_client

llm = get_llm_client()
enriched_poi = enrich_poi(
    poi_data=raw_poi,
    llm_client=llm,
    personas=["culture", "food"]
)
```

## Testing

### Test OpenStreetMap API

```bash
python test_osm.py
```

### Debug OSM Queries

```bash
python debug_osm.py
```

### Validate Environment

```bash
python validate_env.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Roadmap

- [ ] Support for more countries
- [ ] Image scraping from Wikimedia Commons
- [ ] Review aggregation from multiple sources
- [ ] Real-time update mechanism
- [ ] Machine learning for better persona scoring
- [ ] Multi-language support
- [ ] Integration with Google Places (optional fallback)

## License

MIT

## Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review logs in `logs/` directory
- Open an issue on GitHub
- Contact: support@beyondescapism.com
