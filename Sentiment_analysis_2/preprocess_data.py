import pandas as pd
import json
from pathlib import Path

# Define file paths within the Sentiment_analysis directory
DATA_DIR = Path.cwd().parent / "Sentiment_analysis_2"

tmdb_data_path       = DATA_DIR / "tmdb_movie_data.csv"
omdb_data_path       = DATA_DIR / "movie_data.csv"
box_office_mojo_path = DATA_DIR / "box_office_data.csv"
output_merged_path   = DATA_DIR / "merged_movie_data.csv"

df_tmdb            = pd.read_csv(tmdb_data_path)
df_omdb            = pd.read_csv(omdb_data_path)
df_box_office_mojo = pd.read_csv(box_office_mojo_path)

# Load datasets
df_tmdb = pd.read_csv(tmdb_data_path)
df_omdb = pd.read_csv(omdb_data_path)
df_box_office_mojo = pd.read_csv(box_office_mojo_path)

print("--- Original TMDb Data ---")
print(df_tmdb.info())
print(df_tmdb.head())

print("\n--- Original OMDb Data (movie_data.csv) ---")
print(df_omdb.info())
print(df_omdb.head())

print("\n--- Original Box Office Mojo Data ---")
print(df_box_office_mojo.info())
print(df_box_office_mojo.head())

# --- Preprocessing and Renaming --- 

# Standardize title columns for merging
df_tmdb.rename(columns={"title": "Title"}, inplace=True)
df_box_office_mojo.rename(columns={"title": "Title"}, inplace=True)
# df_omdb already has "Title"

# Select and rename columns from TMDb data
df_tmdb_processed = df_tmdb[["Title", "revenue", "budget", "vote_average", "vote_count", "release_date", "genres"]].copy()
df_tmdb_processed.rename(columns={
    "revenue": "TMDb_Revenue",
    "budget": "TMDb_Budget",
    "vote_average": "TMDb_VoteAverage",
    "vote_count": "TMDb_VoteCount",
    "release_date": "TMDb_ReleaseDate",
    "genres": "TMDb_Genres"
}, inplace=True)

# Process OMDb data (df_omdb)
# Extract specific ratings from the 'Ratings' column (string of list of dicts)
def parse_omdb_ratings(ratings_str):
    try:
        ratings_list = eval(ratings_str) # eval is used as per previous notebook, handle with care
        parsed = {}
        for item in ratings_list:
            if item["Source"] == "Internet Movie Database":
                parsed["OMDb_IMDb_Rating"] = item["Value"].split("/")[0] # e.g., "8.3/10"
            elif item["Source"] == "Rotten Tomatoes":
                parsed["OMDb_RottenTomatoes_Rating"] = item["Value"]
            elif item["Source"] == "Metacritic":
                parsed["OMDb_Metacritic_Rating"] = item["Value"].split("/")[0] # e.g., "75/100"
        return pd.Series(parsed)
    except:
        return pd.Series({})

ratings_extracted = df_omdb["Ratings"].apply(parse_omdb_ratings)
df_omdb_processed = pd.concat([df_omdb[["Title", "Year", "Rated", "Runtime", "Genre", "Director", "Actors", "Plot", "Language", "Metascore", "imdbRating", "imdbVotes"]], ratings_extracted], axis=1)

# Clean OMDb imdbVotes (e.g., "1,234,567" to 1234567)
df_omdb_processed["imdbVotes"] = df_omdb_processed["imdbVotes"].astype(str).str.replace(",", "", regex=False).fillna(0).astype(int)
df_omdb_processed.rename(columns={
    "Year": "OMDb_Year",
    "Rated": "OMDb_Rated",
    "Runtime": "OMDb_Runtime",
    "Genre": "OMDb_Genre",
    "Director": "OMDb_Director",
    "Actors": "OMDb_Actors",
    "Plot": "OMDb_Plot",
    "Language": "OMDb_Language",
    "Metascore": "OMDb_Metascore_Direct", # Already numeric in source
    "imdbRating": "OMDb_imdbRating_Direct" # Already numeric in source
}, inplace=True)

# Convert extracted ratings to numeric
for col in ["OMDb_IMDb_Rating", "OMDb_Metacritic_Rating"]:
    if col in df_omdb_processed.columns:
        df_omdb_processed[col] = pd.to_numeric(df_omdb_processed[col], errors='coerce')
if "OMDb_RottenTomatoes_Rating" in df_omdb_processed.columns:
     df_omdb_processed["OMDb_RottenTomatoes_Rating"] = pd.to_numeric(df_omdb_processed["OMDb_RottenTomatoes_Rating"].str.replace("%", "", regex=False), errors='coerce') / 100.0

# Box Office Mojo data is already clean (Title, worldwide_gross)
df_box_office_mojo.rename(columns={"worldwide_gross": "BoxOfficeMojo_WorldwideGross"}, inplace=True)

# --- Merging DataFrames --- 
# Start with TMDb data as the base
df_merged = df_tmdb_processed.copy()

# Merge with OMDb data
df_merged = pd.merge(df_merged, df_omdb_processed, on="Title", how="left")

# Merge with Box Office Mojo data
df_merged = pd.merge(df_merged, df_box_office_mojo, on="Title", how="left")

print("\n--- Merged Data ---")
print(df_merged.info())
print(df_merged.head())
print("Missing values in merged data:\n", df_merged.isnull().sum())

# Save the merged dataframe
df_merged.to_csv(output_merged_path, index=False)
print(f"\nMerged data saved to {output_merged_path}")

# Further define which revenue column to use as primary
# For now, we have TMDb_Revenue and BoxOfficeMojo_WorldwideGross
# User's Sentiment.py used 'worldwide_gross' from a manually collected box_office_data, which is now df_box_office_mojo
# So, BoxOfficeMojo_WorldwideGross should be the primary one.

if 'BoxOfficeMojo_WorldwideGross' in df_merged.columns:
    df_merged['Final_Revenue'] = df_merged['BoxOfficeMojo_WorldwideGross']
elif 'TMDb_Revenue' in df_merged.columns:
    df_merged['Final_Revenue'] = df_merged['TMDb_Revenue']
else:
    df_merged['Final_Revenue'] = None # Or handle error

print("\n--- Merged Data with Final_Revenue column ---")
print(df_merged[['Title', 'TMDb_Revenue', 'BoxOfficeMojo_WorldwideGross', 'Final_Revenue']].head())

# Save again with Final_Revenue if you want it in the CSV
df_merged.to_csv(output_merged_path, index=False)
print(f"Final merged data (with Final_Revenue) saved to {output_merged_path}")

