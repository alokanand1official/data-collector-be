# Robust Data Collection Pipeline

This is a new, crash-proof system for collecting data from OpenStreetMap.

## Architecture

1.  **Harvester** (`pipeline/harvester.py`): Downloads raw data from OSM tile-by-tile and saves it to `raw_data/`.
    *   Resumes automatically if interrupted.
    *   Handles rate limits (429) with exponential backoff.
    *   Saves raw JSON responses.

2.  **Processor** (`pipeline/processor.py`): Reads raw files, cleans them, and saves to `processed_data/`.
    *   Deduplicates items (tiles overlap).
    *   Normalizes data structure.

3.  **Loader** (`pipeline/loader.py`): Uploads processed data to Supabase.
    *   Batched uploads.

## Usage

Run the pipeline using `main.py`:

```bash
# 1. Harvest (Download data)
python main.py harvest --city "Bangkok"

# 2. Process (Clean data)
python main.py process --city "Bangkok"

# 3. Load (Upload to DB)
python main.py load --city "Bangkok"

# OR Run all steps
python main.py all --city "Bangkok"
```

## Configuration

Cities are configured in `main.py`. You can add more cities there.

## Directory Structure

*   `raw_data/`: Contains thousands of small JSON files (one per tile).
*   `processed_data/`: Contains one big JSON file per city.
