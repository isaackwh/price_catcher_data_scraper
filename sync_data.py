import os
import datetime
import pandas as pd
from supabase import create_client, Client

# Fetch Environment Variables from GitHub Secrets
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main():
    # 1. Dynamically generate the current year and month (Format: YYYY-MM)
    # On July 2026, this automatically becomes "2026-07"
    current_date_str = datetime.datetime.now().strftime("%Y-%m")
    
    # 2. Inject the dynamic string into the OpenDOSM PriceCatcher URL template
    url = f"https://storage.data.gov.my/pricecatcher/pricecatcher_{current_date_str).parquet"
    
    print(f"Target URL generated: {url}")
    
    try:
        print("Downloading data from OpenDOSM...")
        df = pd.read_parquet(url)
    except Exception as e:
        print(f"Failed to download file. It might not be uploaded yet for this month. Error: {e}")
        return

    # 3. CRITICAL FOR PRICECATCHER: Filter data down!
    # PriceCatcher tracking is massive (millions of daily item price rows).
    # To stay under Supabase's 500 MB Free Tier, filter it to just your target items or location.
    # Example: Keeping only items tracked on the most recent available day
    if 'date' in df.columns:
        latest_day = df['date'].max()
        print(f"Filtering dataset to only keep rows from the latest date: {latest_day}")
        df = df[df['date'] == latest_day]

    # Convert dataframe to dictionary list
    records = df.to_dict(orient="records")
    print(f"Processed {len(records)} records. Uploading...")

    # 4. Upsert to Supabase
    # For PriceCatcher, conflict unique key is usually a combination of date + item_code + premises_code
    try:
        supabase.table("pricecatcher").upsert(
            records, 
            on_conflict="date,item_code,premises_code"  # Match your composite unique keys
        ).execute()
        print("PriceCatcher data successfully synced!")
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")

if __name__ == "__main__":
    main()
