import pandas as pd
import requests
import json

# Step 1: Define selected movies
movies = [
    {"title": "Barbie", "release_year": 2023, "genre": "Comedy/Fantasy", "tmdb_id": 346698},
    {"title": "Oppenheimer", "release_year": 2023, "genre": "Drama/Biopic", "tmdb_id": 872585},
    {"title": "The Marvels", "release_year": 2023, "genre": "Action/Superhero", "tmdb_id": 609681},
    {"title": "Dune: Part Two", "release_year": 2024, "genre": "Sci-Fi/Action", "tmdb_id": 693134}
]

# Save movie list to CSV
movies_df = pd.DataFrame(movies)
movies_df.to_csv('Sentiment_analysis/selected_movies.csv', index=False)
print("Selected movies saved to Sentiment_analysis/selected_movies.csv")

# Step 2: Fetch TMDb data
TMDB_API_KEY = "1d779d5d4246f2809fc00d7729449f09"

def fetch_tmdb_data(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching TMDb data for ID {tmdb_id}: {e}")
        return None

# Collect TMDb data for each movie
tmdb_data = []
for movie in movies:
    data = fetch_tmdb_data(movie["tmdb_id"])
    if data:
        tmdb_data.append({
            "title": data["title"],
            "revenue": data["revenue"],
            "budget": data["budget"],
            "vote_average": data["vote_average"],
            "vote_count": data["vote_count"],
            "release_date": data["release_date"],
            "genres": ", ".join([g["name"] for g in data["genres"]])
        })

# Save TMDb data to CSV
if tmdb_data:
    tmdb_df = pd.DataFrame(tmdb_data)
    tmdb_df.to_csv("Sentiment_analysis/tmdb_movie_data.csv", index=False)
    print("TMDb data saved to Sentiment_analysis/tmdb_movie_data.csv")
else:
    print("No TMDb data collected. Check API key or network connection.")

# Step 3: Box Office Mojo data (manually collected)
box_office_data = [
    {"title": "Barbie", "worldwide_gross": 1445638102},
    {"title": "Oppenheimer", "worldwide_gross": 975147360},
    {"title": "The Marvels", "worldwide_gross": 206139140},
    {"title": "Dune: Part Two", "worldwide_gross": 711844360}
]
box_office_df = pd.DataFrame(box_office_data)
box_office_df.to_csv("Sentiment_analysis/box_office_data.csv", index=False)
print("Box Office Mojo data saved to Sentiment_analysis/box_office_data.csv")

# Step 4: Note on IMDb reviews
print("Note: Download IMDb 50K Reviews from https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews")
print("Save as 'Sentiment_analysis/IMDB Dataset.csv' or scrape IMDb/X reviews for selected movies.")


import re
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import os
import seaborn as sns
import matplotlib.pyplot as plt

# Download VADER lexicon (run once)
nltk.download('vader_lexicon')

def read_reviews(file_path):
    reviews_by_movie = {}
    current_movie = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('=== Reviews for '):
                current_movie = line.replace('=== Reviews for ', '').replace(' ===', '')
                reviews_by_movie[current_movie] = []
            elif line.startswith('Review ') and current_movie:
                review_text = re.sub(r'^Review \d+:\s*', '', line)
                if review_text:
                    reviews_by_movie[current_movie].append(review_text)
    return reviews_by_movie

def analyze_sentiment(reviews_by_movie):
    sia = SentimentIntensityAnalyzer()
    results = []
    summary = {}
    
    for movie, reviews in reviews_by_movie.items():
        positive, negative, neutral = 0, 0, 0
        movie_results = []
        
        for i, review in enumerate(reviews, 1):
            scores = sia.polarity_scores(review)
            compound = scores['compound']
            
            if compound >= 0.05:
                sentiment = 'Positive'
                positive += 1
            elif compound <= -0.05:
                sentiment = 'Negative'
                negative += 1
            else:
                sentiment = 'Neutral'
                neutral += 1
            
            movie_results.append({
                'Movie': movie,
                'Review Number': i,
                'Review Text': review,
                'Sentiment': sentiment,
                'Compound Score': compound
            })
        
        total = positive + negative + neutral
        summary[movie] = {
            'Total Reviews': total,
            'Positive (%)': (positive / total * 100) if total > 0 else 0,
            'Negative (%)': (negative / total * 100) if total > 0 else 0,
            'Neutral (%)': (neutral / total * 100) if total > 0 else 0
        }
        
        results.extend(movie_results)
    
    return results, summary

def save_results(results, summary, output_dir='Sentiment_analysis'):
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.DataFrame(results)
    csv_path = os.path.join(output_dir, 'sentiment_results.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"Saved detailed sentiment results to {csv_path}")
    
    summary_path = os.path.join(output_dir, 'sentiment_summary.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        for movie, stats in summary.items():
            f.write(f"\n=== {movie} ===\n")
            f.write(f"Total Reviews: {stats['Total Reviews']}\n")
            f.write(f"Positive: {stats['Positive (%)']:.2f}%\n")
            f.write(f"Negative: {stats['Negative (%)']:.2f}%\n")
            f.write(f"Neutral: {stats['Neutral (%)']:.2f}%\n")
    print(f"Saved sentiment summary to {summary_path}")

def plot_sentiment_summary(summary):
    df_summary = pd.DataFrame.from_dict(summary, orient='index')
    df_summary = df_summary.reset_index().rename(columns={'index': 'Movie'})
    
    df_melted = df_summary.melt(id_vars='Movie', 
                                value_vars=['Positive (%)', 'Negative (%)', 'Neutral (%)'],
                                var_name='Sentiment', 
                                value_name='Percentage')
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df_melted, x='Movie', y='Percentage', hue='Sentiment')
    ax.set_title('Sentiment Distribution per Movie')
    ax.set_ylim(0, 100)

    # Add percentage labels on top of bars
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f'{height:.1f}%', 
                        (p.get_x() + p.get_width() / 2., height), 
                        ha='center', va='bottom', fontsize=9)

    plt.legend(title='Sentiment')
    plt.tight_layout()
    plt.savefig('Sentiment_analysis/sentiment_plot.png')
    plt.show()

def main():
    reviews_file = 'Sentiment_analysis/imdb_reviews.txt'
    output_dir = 'Sentiment_analysis'
    
    print("Reading reviews...")
    reviews_by_movie = read_reviews(reviews_file)
    
    print("Analyzing sentiment...")
    results, summary = analyze_sentiment(reviews_by_movie)
    
    print("Saving results...")
    save_results(results, summary, output_dir)
    
    print("\n=== Sentiment Summary ===")
    for movie, stats in summary.items():
        print(f"\n{movie}:")
        print(f"Total Reviews: {stats['Total Reviews']}")
        print(f"Positive: {stats['Positive (%)']:.2f}%")
        print(f"Negative: {stats['Negative (%)']:.2f}%")
        print(f"Neutral: {stats['Neutral (%)']:.2f}%")

    print("\nGenerating visualization...")
    plot_sentiment_summary(summary)

if __name__ == '__main__':
    main()


import pandas as pd

# Load the combined data
combined_data = pd.read_csv('Sentiment_analysis/combined.csv')

# Check the first few rows to ensure it's loaded correctly
print(combined_data.head())

# Remove the percentage signs and convert to float
combined_data['Positive'] = combined_data['Positive'].str.replace('%', '').astype(float)
combined_data['Negative'] = combined_data['Negative'].str.replace('%', '').astype(float)
combined_data['Neutral'] = combined_data['Neutral'].str.replace('%', '').astype(float)

# Make sure that 'worldwide_gross' is a numeric column
combined_data['worldwide_gross'] = pd.to_numeric(combined_data['worldwide_gross'], errors='coerce')

# Check the data types
print(combined_data.dtypes)

# Correlation matrix to understand the relationships between columns
correlation_matrix = combined_data[['worldwide_gross', 'Positive', 'Negative', 'Neutral']].corr()

# Print the correlation matrix
print(correlation_matrix)

import matplotlib.pyplot as plt
import seaborn as sns

# Set the style for the plots
sns.set(style="whitegrid")

# Create a scatter plot for Positive sentiment vs Worldwide Gross
plt.figure(figsize=(10, 6))
sns.scatterplot(data=combined_data, x='Positive', y='worldwide_gross')
plt.title('Positive Sentiment vs Worldwide Gross')
plt.xlabel('Positive Sentiment (%)')
plt.ylabel('Worldwide Gross ($)')
plt.show()

# Repeat for Negative sentiment vs Worldwide Gross
plt.figure(figsize=(10, 6))
sns.scatterplot(data=combined_data, x='Negative', y='worldwide_gross')
plt.title('Negative Sentiment vs Worldwide Gross')
plt.xlabel('Negative Sentiment (%)')
plt.ylabel('Worldwide Gross ($)')
plt.show()

# Repeat for Neutral sentiment vs Worldwide Gross
plt.figure(figsize=(10, 6))
sns.scatterplot(data=combined_data, x='Neutral', y='worldwide_gross')
plt.title('Neutral Sentiment vs Worldwide Gross')
plt.xlabel('Neutral Sentiment (%)')
plt.ylabel('Worldwide Gross ($)')
plt.show()

sns.pairplot(combined_data[['worldwide_gross', 'Positive', 'Negative', 'Neutral']])
plt.show()

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Define the features (sentiments) and target (box office revenue)
X = combined_data[['Positive', 'Negative', 'Neutral']]
y = combined_data['worldwide_gross']

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and fit the model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)

# Evaluate the model's performance
from sklearn.metrics import mean_squared_error, r2_score
mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(f"Mean Squared Error: {mse}")
print(f"R-Squared: {r2}")

