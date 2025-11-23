# Tourism Data Collector - Backend 🌍

A comprehensive ETL pipeline for collecting, enriching, and loading tourism data with AI-powered insights.

## Features

- 🗺️ **Automated Data Collection**: Extract POI data from OpenStreetMap
- 🤖 **AI Enrichment**: Enrich destinations and activities using Llama 3.1
- 🏗️ **Medallion Architecture**: Bronze → Silver → Gold data layers
- 📊 **Rich Schema**: Deep destination profiles with monthly insights, safety scores, budgets
- 🚀 **Scalable**: Parallel processing, caching, incremental updates
- ☁️ **Cloud-Ready**: Google Colab notebook with GPU support
- 🌍 **Auto-Discovery**: Automatically discover tourism destinations by country

## Quick Start

### Local Setup

```bash
# Clone repository
git clone https://github.com/alokanand1official/data-collector-be.git
cd data-collector-be

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run pipeline for a city
cd data_collector
python -c "from orchestrator import Orchestrator; orch = Orchestrator(); orch.run_bronze_layer('Tbilisi'); orch.run_silver_layer('Tbilisi'); orch.run_gold_layer('Tbilisi'); orch.run_load_layer('Tbilisi')"
```

### Google Colab Setup

1. Open `colab_setup.ipynb` in Google Colab
2. Enable GPU runtime
3. Add Supabase credentials to secrets
4. Run all cells

See [Colab Setup Guide](docs/colab_setup_guide.md) for detailed instructions.

## Architecture

### Medallion ETL Pipeline

```
Bronze Layer (Raw)
    ↓
Silver Layer (Standardized)
    ↓
Gold Layer (AI-Enriched)
    ↓
Load Layer (Supabase)
```

### Data Flow

1. **Extract**: OSM data via Overpass API
2. **Transform**: Standardize, deduplicate, prioritize
3. **Enrich**: AI-powered descriptions, personas, timing
4. **Load**: Upload to Supabase `byd_esp` schema

## Project Structure

```
data_collector/
├── config/              # City configurations
├── etl/
│   ├── extract/        # Bronze layer (OSM extraction)
│   ├── transform/      # Silver layer (standardization)
│   ├── enrich/         # Gold layer (AI enrichment)
│   └── load/           # Load layer (Supabase)
├── utils/              # Helper utilities
├── monitoring/         # Streamlit dashboard
├── scripts/            # Utility scripts
├── orchestrator.py     # Main pipeline coordinator
└── colab_setup.ipynb   # Google Colab notebook
```

## Key Features

### 1. Country-Based Auto-Discovery

Automatically discover tourism destinations for any country:

```python
from utils.destination_discovery import TourismDestinationDiscovery

discovery = TourismDestinationDiscovery()
destinations = discovery.discover_destinations("Azerbaijan", min_population=30000)
```

### 2. AI-Powered Enrichment

Generate rich content using Llama 3.1:
- Activity descriptions
- Duration estimates
- Best time to visit
- Persona scores (Culture, Adventure, Food, Relax)

### 3. Destination Profiling

Deep destination insights:
- Monthly weather and crowd levels
- Safety scores and notes
- Budget breakdowns (backpacker to luxury)
- Personality fit scores

### 4. Parallel Processing

5x faster enrichment with parallel POI processing:

```python
from etl.enrich.parallel_ai_enricher import ParallelAIEnricher

enricher = ParallelAIEnricher(max_workers=5)
enricher.process_city("Tbilisi")
```

## Database Schema

### `byd_esp` Schema

- **destinations**: Core destination data
- **destination_details**: Rich profiles (monthly insights, safety, budget)
- **activities**: Enriched POIs with timing and personas
- **neighborhoods**: City areas (future)
- **events**: Festivals and events (future)

See [Schema Design](docs/new_schema_design.sql) for details.

## Performance

| Metric | Local (Ollama) | Colab Free | Colab Pro |
|--------|---------------|------------|-----------|
| POI Enrichment | 7-8 sec/POI | 6-8 sec/POI | 2-3 sec/POI |
| Full City (200 POIs) | 25 min | 20 min | 8 min |
| Cost | $0 | $0 | $10/month |

## Documentation

- [Scalability Plan](docs/scalability_plan.md)
- [Colab Setup Guide](docs/colab_setup_guide.md)
- [Auto-Discovery Guide](docs/auto_discovery_guide.md)
- [Task Checklist](docs/task.md)

## Requirements

- Python 3.8+
- Supabase account
- Ollama (local) or Colab GPU (cloud)
- OpenStreetMap API access

## Environment Variables

```bash
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_service_role_key
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/alokanand1official/data-collector-be/issues
- Documentation: See `docs/` folder

## Roadmap

- [x] Medallion ETL architecture
- [x] AI enrichment with Llama
- [x] Destination profiling
- [x] Google Colab support
- [x] Country auto-discovery
- [ ] Caching system
- [ ] Incremental processing
- [ ] Multi-country parallelization
- [ ] Neighborhood data
- [ ] Event data

---

Built with ❤️ for better travel experiences
