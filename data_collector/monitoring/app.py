import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd

# Add parent dir to path to import orchestrator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import Orchestrator

st.set_page_config(
    page_title="Data Collector ETL Dashboard",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Data Collector ETL Dashboard")

# Initialize Orchestrator
orch = Orchestrator()

# Sidebar
st.sidebar.header("Pipeline Controls")
selected_city = st.sidebar.selectbox("Select City", ["Tbilisi", "Baku", "Bangkok"]) # TODO: Load from config

if st.sidebar.button("Refresh Status"):
    st.rerun()

# Main Dashboard
col1, col2, col3 = st.columns(3)

status = orch.get_pipeline_status()

with col1:
    st.metric("Bronze Layer (Raw)", f"{status['bronze']} Files")
    if st.button("Run Harvest (Bronze)"):
        with st.spinner(f"Harvesting {selected_city}..."):
            orch.run_bronze_layer(selected_city)
            st.success("Harvest Started!")

with col2:
    st.metric("Silver Layer (Clean)", f"{status['silver']} Files")
    if st.button("Run Transform (Silver)"):
        with st.spinner(f"Transforming {selected_city}..."):
            orch.run_silver_layer(selected_city)
            st.success("Transformation Started!")

with col3:
    st.metric("Gold Layer (Enriched)", f"{status['gold']} Files")
    if st.button("Run Enrich (Gold)"):
        with st.spinner(f"Enriching {selected_city}..."):
            orch.run_gold_layer(selected_city)
            st.success("Enrichment Started!")
            
    if st.button("🚀 Load to DB"):
        with st.spinner(f"Loading {selected_city} to Supabase..."):
            orch.run_load_layer(selected_city)
            st.success("Loading Started!")

# Manual Data Entry
st.sidebar.markdown("---")
st.sidebar.subheader("✍️ Add Manual POI")
with st.sidebar.form("manual_poi_form"):
    m_name = st.text_input("Name")
    m_category = st.selectbox("Category", ["museum", "restaurant", "hotel", "historic", "attraction"])
    m_lat = st.number_input("Latitude", value=41.7151, format="%.6f")
    m_lon = st.number_input("Longitude", value=44.8271, format="%.6f")
    m_desc = st.text_area("Description (Optional)")
    
    if st.form_submit_button("Add POI"):
        if m_name:
            # Save to manual_pois.json in Silver layer
            city_key = selected_city.lower().replace(" ", "_")
            silver_path = Path(f"layers/silver/{city_key}")
            silver_path.mkdir(parents=True, exist_ok=True)
            manual_file = silver_path / "manual_pois.json"
            
            new_poi = {
                "name": m_name,
                "category": m_category,
                "coordinates": {"lat": m_lat, "lon": m_lon},
                "description": m_desc, # Pre-filled description if provided
                "tags": {"manual": "true"},
                "osm_id": f"manual_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            current_manual = []
            if manual_file.exists():
                with open(manual_file, 'r') as f:
                    current_manual = json.load(f)
            
            current_manual.append(new_poi)
            
            with open(manual_file, 'w') as f:
                json.dump(current_manual, f, indent=2)
                
            st.sidebar.success(f"Added {m_name}!")
        else:
            st.sidebar.error("Name is required")

st.sidebar.markdown("---")
st.sidebar.subheader("📂 Upload CSV")
uploaded_file = st.sidebar.file_uploader("Upload POIs (CSV)", type=['csv'])
if uploaded_file is not None:
    if st.sidebar.button("Process CSV"):
        # Save temp file
        temp_path = Path(f"temp_{uploaded_file.name}")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # Process
        from etl.transform.csv_standardizer import CSVStandardizer
        silver_dir = Path("layers/silver")
        standardizer = CSVStandardizer(silver_dir)
        
        if standardizer.process_csv(temp_path, selected_city):
            st.sidebar.success(f"Processed {uploaded_file.name}!")
        else:
            st.sidebar.error("Failed to process CSV")
            
        # Cleanup
        temp_path.unlink()

# Recent Logs
st.subheader("Recent Logs")
try:
    with open("pipeline.log", "r") as f:
        logs = f.readlines()[-20:] # Last 20 lines
        st.code("".join(logs))
except FileNotFoundError:
    st.info("No logs found yet.")
