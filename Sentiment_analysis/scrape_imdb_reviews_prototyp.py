import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os

# Movie IMDb URLs
movies = [
    {"title": "Barbie", "imdb_url": "https://www.imdb.com/title/tt1517268/reviews"},
    {"title": "Oppenheimer", "imdb_url": "https://www.imdb.com/title/tt15398776/reviews"},
    {"title": "The Marvels", "imdb_url": "https://www.imdb.com/title/tt10676048/reviews"},
    {"title": "Dune: Part Two", "imdb_url": "https://www.imdb.com/title/tt15239678/reviews"}
]

# Function to scrape IMDb reviews
def scrape_imdb_reviews(url, max_reviews=20):
    reviews = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"Successfully accessed {url} (Status: {response.status_code})")

        # Save raw HTML for debugging
        html_file = f"Sentiment_analysis/debug_{url.split('/')[-2]}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Saved raw HTML to {html_file}")

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the review list container
        lister_list = soup.find("div", class_="lister-list")
        if not lister_list:
            print("No lister-list container found. Check HTML structure.")
            return reviews

        # Extract reviews from ipc-html-content-inner-div
        review_elements = lister_list.find_all("div", class_="ipc-html-content-inner-div")
        print(f"Found {len(review_elements)} review elements with div.ipc-html-content-inner-div")

        for element in review_elements:
            review_text = element.text.strip()
            if review_text:  # Include all non-empty reviews
                reviews.append({"review": review_text})

        # Limit to max_reviews
        reviews = reviews[:max_reviews]
        print(f"Scraped {len(reviews)} reviews from {url}")

        # Debug: Print first review snippet
        if reviews:
            print(f"Sample review: {reviews[0]['review'][:100]}...")
        else:
            # Print sample HTML for debugging
            items = lister_list.find_all("div", class_="lister-item-content")[:2]
            if items:
                print("Sample lister-item-content HTML:", str(items[0])[:200] + "...")
            print("No valid reviews found. Check debug HTML for structure.")

        time.sleep(2)
    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
    return reviews

# Scrape reviews for each movie
all_reviews = []
for movie in movies:
    print(f"Scraping reviews for {movie['title']}...")
    reviews = scrape_imdb_reviews(movie["imdb_url"])
    for review in reviews:
        review["title"] = movie["title"]
    all_reviews.extend(reviews)

# Save reviews to CSV
if all_reviews:
    reviews_df = pd.DataFrame(all_reviews)
    reviews_df.to_csv("Sentiment_analysis/imdb_scraped_reviews.csv", index=False)
    print("Scraped reviews saved to Sentiment_analysis/imdb_scraped_reviews.csv")
else:
    print("No reviews scraped. Check debug HTML files in Sentiment_analysis/ for IMDb structure.")