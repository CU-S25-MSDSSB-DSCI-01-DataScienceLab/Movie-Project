import requests
import json
import time

# our omdb key
API_KEY = "2942608b"

with open("C:\PythonProjects\Movie-Team\data_collection\movie_list.txt", "r") as f:
    movie_list = [line.strip() for line in f if line.strip()]

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

    time.sleep(1)

with open("omdb_data.json", "w") as f:
    json.dump(all_data, f, indent=4)

# here we save failed movies to a separate file
with open("omdb_failed.txt", "w") as f:
    f.write("\n".join(failed_movies))

print("Finished fetching OMDb data.")
print(f"✅ {len(all_data)} movies fetched")
print(f"❌ {len(failed_movies)} movies failed")
