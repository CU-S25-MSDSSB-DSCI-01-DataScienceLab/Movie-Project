import requests
import json
import time
import os

# this script fetches movie data from the OMDb api for a list of movies
# and saves the results to a JSON file.

# our omdb key
API_KEY = "a088fd89"

# dynamic paths to use on different PCs
base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

data_dir = os.path.join(project_root, "data_collection", "OMDb")
movie_list_path = os.path.join(project_root, "data_collection", "movie_list.txt")
omdb_data_path = os.path.join(data_dir, "omdb_data.json")
omdb_failed_path = os.path.join(data_dir, "omdb_failed.txt")

with open(movie_list_path, "r", encoding="utf-8") as f:
    movie_list = [line.strip() for line in f if line.strip()]

all_data = []
failed_movies = []

total = len(movie_list)
for idx, title in enumerate(movie_list, 1):
    try:
        response = requests.get(
            "http://www.omdbapi.com/",
            params={"t": title, "apikey": API_KEY},
            timeout=5
        )
        data = response.json()
    except requests.RequestException as e:
        print(f"[{idx}/{total}] ⁉️ {title} — Request error: {e}")
        failed_movies.append(title)
        time.sleep(0.2)
        continue

    if data.get("Response") == "True":
        all_data.append(data)
        print(f"[{idx}/{total}] ✅ {title}")
    else:
        failed_movies.append(title)
        # Inline error retrieval to avoid stray assignment
        print(f"[{idx}/{total}] ⁉️ {title} — {data.get('Error', 'Unknown error')}")

    # 5 requests per second as we have a paid version
    time.sleep(0.2)

# save to JSON
os.makedirs(data_dir, exist_ok=True)
with open(omdb_data_path, "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

# failed to fetch to txt
with open(omdb_failed_path, "w", encoding="utf-8") as f:
    for title in failed_movies:
        f.write(f"{title}\n")

print("\nFinished fetching OMDb data.")
print(f"☑️ {len(all_data)} movies fetched")
print(f"⁉️ {len(failed_movies)} movies failed")