import os
import pandas as pd
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def sync_items():
    url = "https://storage.data.gov.my/pricecatcher/lookup_item.parquet"
    print("Downloading item lookups...")
    df = pd.read_parquet(url)
    records = df.to_dict(orient="records")
    print(f"Upserting {len(records)} items...")
    supabase.table("item_lookup").upsert(records, on_conflict="item_code").execute()

def sync_premises():
    url = "https://storage.data.gov.my/pricecatcher/lookup_premise.parquet"
    print("Downloading premise lookups...")
    df = pd.read_parquet(url)
    records = df.to_dict(orient="records")
    print(f"Upserting {len(records)} premises...")
    supabase.table("premise_lookup").upsert(records, on_conflict="premise_code").execute()

if __name__ == "__main__":
    sync_items()
    sync_premises()
    print("All lookups successfully populated!")
