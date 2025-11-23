"""
Database utilities for data collector
Handles all Supabase interactions
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class Database:
    """Database interface for data collection"""
    
    def __init__(self, schema: str = None):
        """Initialize Supabase client"""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
            
        # Use provided schema or fallback to env var or default to 'public'
        self.schema = schema or os.getenv("DB_SCHEMA", "public")
        
        # Import ClientOptions here to avoid circular imports if any
        from supabase.lib.client_options import ClientOptions
        
        options = ClientOptions(schema=self.schema)
        self.client: Client = create_client(self.url, self.key, options=options)
        
        logger.info(f"Connected to Supabase (Schema: {self.schema})")
    
    def get_country(self, country_code: str) -> Optional[Dict]:
        """Get country by code"""
        try:
            result = self.client.table('countries').select('*').eq('code', country_code).single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting country {country_code}: {e}")
            return None
    
    def create_job(self, job_data: Dict) -> Optional[str]:
        """Create a new collection job"""
        try:
            result = self.client.table('data_collection_jobs').insert(job_data).execute()
            if result.data:
                job_id = result.data[0]['id']
                logger.info(f"Created job: {job_id}")
                return job_id
            return None
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            return None
    
    def update_job(self, job_id: str, updates: Dict) -> bool:
        """Update job status"""
        try:
            self.client.table('data_collection_jobs').update(updates).eq('id', job_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating job {job_id}: {e}")
            return False
    
    def log_message(self, job_id: str, level: str, message: str, data: Dict = None) -> None:
        """Log a message to data_collection_log"""
        try:
            log_entry = {
                'job_id': job_id,
                'level': level,
                'message': message,
                'data': data or {}
            }
            self.client.table('data_collection_log').insert(log_entry).execute()
        except Exception as e:
            logger.warning(f"Error logging message: {e}")
    
    def save_pois(self, pois: List[Dict]) -> int:
        """Save POIs to database with robust deduplication"""
        if not pois:
            return 0
        
        try:
            # Try upsert first (most efficient if constraint exists)
            result = self.client.table('pois').upsert(pois, on_conflict='osm_id').execute()
            count = len(result.data) if result.data else 0
            logger.info(f"Saved {count} POIs to database (upsert)")
            return count
        except Exception as e:
            error_msg = str(e)
            # Check for "no unique constraint" error (Postgres 42P10)
            if '42P10' in error_msg or 'there is no unique or exclusion constraint' in error_msg:
                logger.warning("Unique constraint missing on osm_id. Falling back to check-then-insert.")
                return self._save_pois_manual_dedup(pois)
            else:
                logger.error(f"Error saving POIs: {e}")
                return 0

    def _save_pois_manual_dedup(self, pois: List[Dict]) -> int:
        """Manually deduplicate POIs against database"""
        try:
            # Extract OSM IDs from input
            osm_ids = [p.get('osm_id') for p in pois if p.get('osm_id')]
            if not osm_ids:
                return 0
                
            # Query existing IDs
            # Note: Supabase limit is usually 1000, so we might need batching if list is huge
            # But for now we assume batch size < 1000
            existing_result = self.client.table('pois').select('osm_id').in_('osm_id', osm_ids).execute()
            existing_ids = {item['osm_id'] for item in existing_result.data}
            
            # Filter out existing
            new_pois = [p for p in pois if p.get('osm_id') not in existing_ids]
            
            if not new_pois:
                logger.info("No new POIs to insert.")
                return 0
                
            # Insert new records
            result = self.client.table('pois').insert(new_pois).execute()
            count = len(result.data) if result.data else 0
            logger.info(f"Saved {count} new POIs to database (manual dedup)")
            return count
            
        except Exception as e:
            logger.error(f"Error in manual deduplication: {e}")
            return 0
    
    def save_destinations(self, destinations: List[Dict]) -> int:
        """Save destinations to database"""
        if not destinations:
            return 0
        
        try:
            result = self.client.table('destinations').insert(destinations).execute()
            count = len(result.data) if result.data else 0
            logger.info(f"Saved {count} destinations to database")
            return count
        except Exception as e:
            logger.error(f"Error saving destinations: {e}")
            return 0
    
    def get_province(self, country_code: str, province_name: str) -> Optional[Dict]:
        """Get province by name"""
        try:
            result = self.client.table('provinces').select('*').eq(
                'country_code', country_code
            ).eq('name', province_name).single().execute()
            return result.data
        except Exception as e:
            logger.debug(f"Province {province_name} not found: {e}")
            return None
    
    def create_province(self, province_data: Dict) -> Optional[str]:
        """Create a new province"""
        try:
            result = self.client.table('provinces').insert(province_data).execute()
            if result.data:
                return result.data[0]['id']
            return None
        except Exception as e:
            logger.error(f"Error creating province: {e}")
            return None


# Global database instance
db = Database()
