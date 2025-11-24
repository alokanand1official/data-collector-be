"""
Clean database for a city and re-run the pipeline
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# City to clean
CITY = "batumi"
DESTINATION_ID = "ef571e71-2190-48e8-a67d-80dc898f97d4"

# Connect to Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

print(f"🗑️  Cleaning database for {CITY}...")

# Delete activities
print("Deleting activities...")
result = supabase.schema('byd_esp').table('activities').delete().eq('destination_id', DESTINATION_ID).execute()
print(f"  Deleted {len(result.data) if result.data else 0} activities")

# Delete destination details
print("Deleting destination details...")
result = supabase.schema('byd_esp').table('destination_details').delete().eq('destination_id', DESTINATION_ID).execute()
print(f"  Deleted {len(result.data) if result.data else 0} destination details")

# Delete destination
print("Deleting destination...")
result = supabase.schema('byd_esp').table('destinations').delete().eq('slug', CITY).execute()
print(f"  Deleted {len(result.data) if result.data else 0} destinations")

print(f"✅ Database cleaned for {CITY}")
