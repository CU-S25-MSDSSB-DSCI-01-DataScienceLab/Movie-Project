import requests
from bs4 import BeautifulSoup
import os

def scrape_imdb_reviews(title_ids, output_dir="Sentiment_analysis"):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    # Dictionary of movie titles and their IMDb IDs
    movies = {
        'Barbie': title_ids.get('Barbie', 'tt1517268'),
        'Oppenheimer': title_ids.get('Oppenheimer', 'tt15398776'),
        'The Marvels': title_ids.get('The Marvels', 'tt10676048'),
        'Dune: Part Two': title_ids.get('Dune: Part Two', 'tt15239678')
    }
    
    # File to save all reviews
    reviews_file = os.path.join(output_dir, 'imdb_reviews.txt')
    
    for movie, title_id in movies.items():
        url = f"https://www.imdb.com/title/{title_id}/reviews"
        print(f"Scraping reviews for {movie}...")
        
        try:
            # Fetch the page
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Successfully accessed {url} (Status: {response.status_code})")
            
            # Save raw HTML for debugging
            debug_file = os.path.join(output_dir, f"debug_{title_id}.html")
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"Saved raw HTML to {debug_file}")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            review_containers = soup.find_all('div', class_='ipc-html-content-inner-div')
            
            if review_containers:
                print(f"Found {len(review_containers)} reviews for {movie}.")
                with open(reviews_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n=== Reviews for {movie} ===\n")
                    for i, review in enumerate(review_containers, 1):
                        review_text = review.get_text(strip=True)
                        f.write(f"Review {i}: {review_text}\n")
                        print(f"Review {i}: {review_text[:100]}...")  # Print first 100 chars
            else:
                print("No reviews found. Check HTML structure in debug file.")
        
        except requests.RequestException as e:
            print(f"Failed to access {url}: {e}")
    
    if os.path.exists(reviews_file):
        print(f"All reviews saved to {reviews_file}")
    else:
        print("No reviews scraped. Check debug HTML files for IMDb structure.")

# Movie IMDb IDs
title_ids = {
    'Barbie': 'tt1517268',
    'Oppenheimer': 'tt15398776',
    'The Marvels': 'tt10676048',
    'Dune: Part Two': 'tt15239678'
}

# Run the scraper
scrape_imdb_reviews(title_ids)