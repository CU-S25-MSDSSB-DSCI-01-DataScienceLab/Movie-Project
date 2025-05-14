import re
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import os
import seaborn as sns
import matplotlib.pyplot as plt

# Ensure VADER lexicon is available (nltk.download('vader_lexicon') should be run once prior)

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
    summary_data = [] # Changed to list of dicts for easier DataFrame creation
    
    for movie, reviews in reviews_by_movie.items():
        positive, negative, neutral = 0, 0, 0
        movie_results = []
        
        if not reviews: # Handle case where a movie might have no reviews scraped
            print(f"Warning: No reviews found for {movie} in the input file.")
            summary_data.append({
                'Movie': movie,
                'Total Reviews': 0,
                'Positive (%)': 0,
                'Negative (%)': 0,
                'Neutral (%)': 0
            })
            continue
            
        for i, review in enumerate(reviews, 1):
            scores = sia.polarity_scores(review)
            compound = scores['compound']
            
            if compound >= 0.05:
                sentiment_label = 'Positive'
                positive += 1
            elif compound <= -0.05:
                sentiment_label = 'Negative'
                negative += 1
            else:
                sentiment_label = 'Neutral'
                neutral += 1
            
            movie_results.append({
                'Movie': movie,
                'Review Number': i,
                'Review Text': review,
                'Sentiment': sentiment_label,
                'Compound Score': compound
            })
        
        total = positive + negative + neutral
        summary_data.append({
            'Movie': movie,
            'Total Reviews': total,
            'Positive (%)': (positive / total * 100) if total > 0 else 0,
            'Negative (%)': (negative / total * 100) if total > 0 else 0,
            'Neutral (%)': (neutral / total * 100) if total > 0 else 0
        })
        
        results.extend(movie_results)
    
    df_summary = pd.DataFrame(summary_data)
    return results, df_summary

def save_sentiment_outputs(results, df_summary, output_dir='.'):
    # output_dir is current directory by default
    os.makedirs(output_dir, exist_ok=True) # Ensure dir exists, though '.' always does
    
    df_detailed_results = pd.DataFrame(results)
    detailed_csv_path = os.path.join(output_dir, 'sentiment_detailed_results.csv')
    df_detailed_results.to_csv(detailed_csv_path, index=False, encoding='utf-8')
    print(f"Saved detailed sentiment results to {detailed_csv_path}")
    
    summary_csv_path = os.path.join(output_dir, 'sentiment_summary_table.csv')
    df_summary.to_csv(summary_csv_path, index=False, encoding='utf-8')
    print(f"Saved sentiment summary table to {summary_csv_path}")

    summary_txt_path = os.path.join(output_dir, 'sentiment_summary.txt')
    with open(summary_txt_path, 'w', encoding='utf-8') as f:
        for index, row in df_summary.iterrows():
            f.write(f"\n=== {row['Movie']} ===\n")
            f.write(f"Total Reviews: {row['Total Reviews']}\n")
            f.write(f"Positive: {row['Positive (%)']:.2f}%\n")
            f.write(f"Negative: {row['Negative (%)']:.2f}%\n")
            f.write(f"Neutral: {row['Neutral (%)']:.2f}%\n")
    print(f"Saved text sentiment summary to {summary_txt_path}")

def plot_sentiment_summary_chart(df_summary, output_dir='.'):
    if df_summary.empty or 'Movie' not in df_summary.columns:
        print("Summary DataFrame is empty or malformed, skipping plot.")
        return
        
    df_melted = df_summary.melt(id_vars='Movie', 
                                value_vars=['Positive (%)', 'Negative (%)', 'Neutral (%)'],
                                var_name='Sentiment_Type', # Renamed to avoid conflict with 'Sentiment' column in detailed results
                                value_name='Percentage')
    
    plt.figure(figsize=(12, 7))
    ax = sns.barplot(data=df_melted, x='Movie', y='Percentage', hue='Sentiment_Type')
    ax.set_title('Sentiment Distribution per Movie')
    ax.set_ylim(0, 100)
    plt.xticks(rotation=45, ha='right')

    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f'{height:.1f}%', 
                        (p.get_x() + p.get_width() / 2., height), 
                        ha='center', va='bottom', fontsize=9)

    plt.legend(title='Sentiment Type')
    plt.tight_layout()
    plot_path = os.path.join(output_dir, 'sentiment_summary_plot.png')
    plt.savefig(plot_path)
    print(f"Saved sentiment summary plot to {plot_path}")
    # plt.show() # Avoid showing plot in non-interactive environment

def perform_correlation_analysis(merged_movie_data_path, sentiment_summary_df, output_dir='.'):
    try:
        df_movies = pd.read_csv(merged_movie_data_path)
    except FileNotFoundError:
        print(f"Error: {merged_movie_data_path} not found. Skipping correlation analysis.")
        return

    # Merge movie data with sentiment summary
    # Ensure 'Movie' in sentiment_summary_df matches 'Title' in df_movies
    df_combined = pd.merge(df_movies, sentiment_summary_df, left_on='Title', right_on='Movie', how='left')
    if 'Movie' != 'Title' and 'Movie' in df_combined.columns:
         df_combined.drop(columns=['Movie'], inplace=True) # Drop redundant 'Movie' column if names differed
    
    combined_csv_path = os.path.join(output_dir, 'combined_movie_sentiment_data.csv')
    df_combined.to_csv(combined_csv_path, index=False)
    print(f"Saved combined movie and sentiment data to {combined_csv_path}")

    # Select relevant columns for correlation
    # Ensure 'Final_Revenue' exists from preprocess_data.py script
    if 'Final_Revenue' not in df_combined.columns:
        print("Error: 'Final_Revenue' column not found in combined data. Skipping correlation.")
        return
    if not pd.api.types.is_numeric_dtype(df_combined['Final_Revenue']):
        df_combined['Final_Revenue'] = pd.to_numeric(df_combined['Final_Revenue'], errors='coerce')
    
    sentiment_cols = ['Positive (%)', 'Negative (%)', 'Neutral (%)']
    for col in sentiment_cols:
        if col not in df_combined.columns:
            print(f"Error: Sentiment column '{col}' not found. Skipping correlation.")
            return
        if not pd.api.types.is_numeric_dtype(df_combined[col]):
             df_combined[col] = pd.to_numeric(df_combined[col], errors='coerce')

    df_combined.dropna(subset=['Final_Revenue'] + sentiment_cols, inplace=True) # Drop rows if key data is missing after conversion
    
    if df_combined.shape[0] < 2:
        print("Not enough data points after cleaning for correlation analysis. Skipping.")
        return

    correlation_matrix = df_combined[['Final_Revenue'] + sentiment_cols].corr()
    print("\n--- Correlation Matrix (Revenue vs Sentiment) ---")
    print(correlation_matrix)

    # Save correlation matrix
    correlation_matrix.to_csv(os.path.join(output_dir, 'correlation_matrix.csv'))
    print(f"Saved correlation matrix to {os.path.join(output_dir, 'correlation_matrix.csv')}")

    # Visualizations for correlation
    for sent_col in sentiment_cols:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df_combined, x=sent_col, y='Final_Revenue')
        plt.title(f'{sent_col} vs Worldwide Gross')
        plt.xlabel(sent_col)
        plt.ylabel('Worldwide Gross ($)')
        scatter_plot_path = os.path.join(output_dir, f'{sent_col.replace(" (%)", "").lower()}_vs_revenue_scatter.png')
        plt.savefig(scatter_plot_path)
        print(f"Saved scatter plot to {scatter_plot_path}")
        # plt.show()

    pairplot_path = os.path.join(output_dir, 'sentiment_revenue_pairplot.png')
    sns.pairplot(df_combined[['Final_Revenue'] + sentiment_cols])
    plt.savefig(pairplot_path)
    print(f"Saved pairplot to {pairplot_path}")
    # plt.show()
    
    # Basic Linear Regression (Example)
    # Check if enough data for split
    if df_combined.shape[0] >= 4: # Minimum for a small test split, ideally more
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_squared_error, r2_score

        X = df_combined[sentiment_cols]
        y = df_combined['Final_Revenue']
        
        # Given the very small dataset (4 movies), train_test_split might be problematic.
        # For demonstration, we'll fit on all data or handle small N.
        if df_combined.shape[0] >= 2: # Fit if at least 2 points
            model = LinearRegression()
            model.fit(X, y)
            predictions = model.predict(X)
            mse = mean_squared_error(y, predictions)
            r2 = r2_score(y, predictions)
            print(f"\n--- Linear Regression (fitted on all {df_combined.shape[0]} data points) ---")
            print(f"Coefficients: {model.coef_}")
            print(f"Intercept: {model.intercept_}")
            print(f"Mean Squared Error: {mse}")
            print(f"R-Squared: {r2}")
        else:
            print("Not enough data for linear regression model fitting.")
    else:
        print("Dataset too small for train/test split in linear regression example.")

def main():
    reviews_file_path = 'imdb_reviews.txt' # Assumes it's in the current directory
    merged_movie_data_path = 'merged_movie_data.csv' # From preprocess_data.py
    output_dir = '.' # Save outputs in the current directory

    print("Reading reviews...")
    if not os.path.exists(reviews_file_path):
        print(f"Error: Reviews file '{reviews_file_path}' not found. Please ensure it exists.")
        return
    reviews_by_movie = read_reviews(reviews_file_path)
    
    print("Analyzing sentiment...")
    detailed_sentiment_results, sentiment_summary_df = analyze_sentiment(reviews_by_movie)
    
    if not detailed_sentiment_results:
        print("No sentiment results to save or plot. Exiting.")
        return
        
    print("Saving sentiment analysis outputs...")
    save_sentiment_outputs(detailed_sentiment_results, sentiment_summary_df, output_dir)
    
    print("\n=== Sentiment Summary (from DataFrame) ===")
    print(sentiment_summary_df)

    print("\nGenerating sentiment summary visualization...")
    plot_sentiment_summary_chart(sentiment_summary_df, output_dir)
    
    print("\nPerforming correlation analysis with movie financial data...")
    perform_correlation_analysis(merged_movie_data_path, sentiment_summary_df, output_dir)

if __name__ == '__main__':
    main()

