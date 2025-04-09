import json
import os

#here we want to check if we have box office data for all 988 movies 
# Dynamically locate the JSON file (to run it on different PCs)
base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, "omdb_data.json")

# Load the data using the relative path
with open(json_path, "r") as f:
    data = json.load(f)

boxofficefield_count = sum(1 for movie in data if movie.get("BoxOffice") not in [None, "N/A"])

# count the number of movies with box office data availabble
print(f"{boxofficefield_count} out of {len(data)} movies have box office data.")