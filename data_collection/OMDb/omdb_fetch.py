import requests
import json

# our omdb key
API_KEY = "2942608b"

movies = ["The Wolf of Wall Street", "Dallas Buyers Club", "The House That Jack Built", 
          "The Ballad of Buster Scruggs", "The Hateful Eight", "The Big Short", 
          "The Irishman", "The Lighthouse", "The Gentlemen", "The Grand Budapest Hotel", 
          "The Revenant", "The Shape of Water", "The Martian", "The Social Network",
          "The King's Speech", "The Theory of Everything", "The Imitation Game", 
          "Django Unchained", "Inglourious Basterds", "Once Upon a Time in Hollywood",
          "Ford v Ferrari", "The Two Popes", "Marriage Story", " 1917", "Jojo Rabbit",
          "Joker", "Parasite", "Z", "Zombieland", "Zombieland: Double Tap"]

collected_data = []

for movie in movies:
    url = f"http://www.omdbapi.com/?t={movie}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    collected_data.append(data)  # add each movie's data to the list

# save the data into a JSON file
with open("movies_data.json", "w") as file:
    json.dump(collected_data, file, indent=4) 

print("Data collection for 30 movies has been completed. Check movies_data.json")
