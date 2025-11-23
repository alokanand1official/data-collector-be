from utils.database import Database

def check_staging():
    db = Database(schema='byd_escapism')
    print("Connected to byd_escapism")
    
    dests = db.client.table('destinations').select('*').execute().data
    print(f"Found {len(dests)} destinations:")
    for d in dests:
        print(f" - {d['name']} (ID: {d.get('id')})")

if __name__ == "__main__":
    check_staging()
