#!/usr/bin/env python
import os
import time
import csv
import requests
from tqdm import tqdm

TMDB_APIKEY = "1d779d5d4246f2809fc00d7729449f09"

# paths
INPUT_PATH  = os.path.join(os.getcwd(), "data_collection", "missing_boxoffice_enhanced.csv")
OUTPUT_PATH = os.path.join(os.getcwd(), "data_collection", "tmdb_revenues.csv")
DELAY = 0.2  #api call delay

def load_missing(path):
    """Load enhanced missing list with Title, imdbID, tmdbId."""
    rows = []
    if not os.path.exists(path):
        print(f"Missing input file: {path}")
        return rows
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_id = row.get("tmdbId", "")
            # filter out empty or NaN-like IDs
            if raw_id and raw_id.lower() != "nan":
                rows.append(row)
    return rows

# here we fetch revenue for each movie row
def fetch_revenues(rows):
    enhanced_rows = []
    for row in tqdm(rows, desc="Fetching revenues"):
        raw_id = row.get("tmdbId", "")
        try:
            tmdb_id = int(float(raw_id))
            url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
            r = requests.get(
                url,
                params={"api_key": TMDB_APIKEY},
                timeout=10
            )
            data = r.json()
            revenue = data.get("revenue") or 0
        except Exception as e:
            print(f"Error fetching {row.get('Title','')} (tmdbId '{raw_id}'): {e}")
            revenue = 0
        enhanced_rows.append({
            "Title": row.get("Title", ""),
            "imdbID": row.get("imdbID", ""),
            "tmdbId": raw_id,
            "BoxOffice": revenue
        })
        time.sleep(DELAY)
    return enhanced_rows

#   save list to CSV
def save_csv(rows, path):
    if not rows:
        print("Nothing to save")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} revenue records to {path}")

def main():
    rows = load_missing(INPUT_PATH)
    if not rows:
        return
    enhanced = fetch_revenues(rows)
    save_csv(enhanced, OUTPUT_PATH)

if __name__ == "__main__":
    main()