import os
import time
import csv
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

#pathing
base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(base_dir, '..'))

data_dir       = os.path.join(project_root, 'data_collection')
fallback_path  = os.path.join(data_dir, 'fallback_boxoffice.csv')
cleaned_csv    = os.path.join(data_dir, 'omdb_cleaned.csv')
output_path    = os.path.join(data_dir, 'thenumbers_revenues.csv')

# fallbvck_boxoffice.csv load
if not os.path.exists(fallback_path):
    raise FileNotFoundError(f"Fallback CSV not found: {fallback_path}")
with open(fallback_path, newline='', encoding='utf-8') as f:
    fallback_rows = list(csv.DictReader(f))

# we want to get "year" per "title"
if not os.path.exists(cleaned_csv):
    raise FileNotFoundError(f"Cleaned OMDb CSV not found: {cleaned_csv}")
cleaned_df = pd.read_csv(cleaned_csv, usecols=['Title','Year'])

#title to a single integer  connection
year_map = {}
for _, row in cleaned_df.iterrows():
    raw = row['Year']
    year = None
    try:
        year = int(raw)
    except Exception:
        m = re.search(r"(\d{4})", str(raw))
        if m:
            year = int(m.group(1))
    if year:
        year_map[row['Title']] = year

# Helper: create slug for The-Numbers URL
def slugify(title, year):
    #removes punctuation, spaces and adds hyphens
    text = re.sub(r"[^\w\s-]", "", title)
    text = re.sub(r"\s+", " ", text).strip()
    slug = text.replace(' ', '-')
    return f"{slug}-{year}"

# the actual scraping func
def fetch_thenumbers_revenue(slug):
    url = f"https://www.the-numbers.com/movie/{slug}"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('table', attrs={'id': 'box_office'}) or \
                soup.find('table', attrs={'class': 'movie_finances'})
        if not table:
            return 0
        for row in table.find_all('tr'):
            th = row.find('th')
            td = row.find('td')
            if th and 'Domestic Box Office' in th.text and td:
                val = td.text.strip()
                num = re.sub(r"[\$,]", "", val)
                return int(num) if num.isdigit() else 0
    except Exception:
        return 0
    return 0

#scraping loop main
enhanced = []
for rec in tqdm(fallback_rows, desc='The-Numbers Scrape'):
    title = rec.get('Title', '')
    year = year_map.get(title)
    if not year:
        revenue = 0
    else:
        slug = slugify(title, year)
        revenue = fetch_thenumbers_revenue(slug)
    enhanced.append({
        'Title': title,
        'imdbID': rec.get('imdbID', ''),
        'tmdbId': rec.get('tmdbId', ''),
        'BoxOffice': revenue
    })
    time.sleep(0.2)

os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=enhanced[0].keys())
    writer.writeheader()
    writer.writerows(enhanced)

print(f"Saved {len(enhanced)} records → {output_path}")