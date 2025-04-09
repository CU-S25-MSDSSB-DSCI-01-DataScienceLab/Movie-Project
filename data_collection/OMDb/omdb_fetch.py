import requests
import json
import time
import os

# this script fetches movie data from the OMDb api for a list of movies
# and saves the results to a JSON file.

# dynamic paths to use on different PCs
base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

movie_list_path = os.path.join(project_root, "data_collection", "movie_list.txt")
omdb_data_path = os.path.join(base_dir, "omdb_data.json")
omdb_failed_path = os.path.join(base_dir, "omdb_failed.txt")

with open(movie_list_path, "r") as f:
    movie_list = [line.strip() for line in f if line.strip()]

# our omdb key
API_KEY = "2942608b"

all_data = []
failed_movies = []

for title in movie_list:
    url = f"http://www.omdbapi.com/?t={title}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data.get("Response") == "True": 
        all_data.append(data)
        print(f"✅{title}")
    else:
        failed_movies.append(title)
        print(f"❌{title} — {data.get('Error')}")

# to avoid hitting the API rate limit (1 request per second in free version)
    time.sleep(1) 

with open(omdb_data_path, "w") as f:
    json.dump(all_data, f, indent=4)

# here we save failed movies to a separate file
with open(omdb_failed_path, "w") as f:
    f.write("\n".join(failed_movies))

print("Finished fetching OMDb data.")
print(f"✅ {len(all_data)} movies fetched")
print(f"❌ {len(failed_movies)} movies failed")