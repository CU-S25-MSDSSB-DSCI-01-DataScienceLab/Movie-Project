import pandas as pd
import scipy.stats as stats
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Load merged movie data and sentiment summary
merged_data = pd.read_csv("box_office_data.csv")
sentiment_summary = pd.read_csv("sentiment_summary.csv")

# Merge datasets
final_data = merged_data.merge(sentiment_summary, on="title", how="left")

# Compute correlations
correlation_sentiment, p_value_sentiment = stats.pearsonr(final_data["avg_sentiment"], final_data["worldwide_gross"])
correlation_rating, p_value_rating = stats.pearsonr(final_data["vote_average"], final_data["worldwide_gross"])
print(f"Correlation (avg_sentiment vs. worldwide_gross): {correlation_sentiment:.3f}, P-value: {p_value_sentiment:.3f}")
print(f"Correlation (vote_average vs. worldwide_gross): {correlation_rating:.3f}, P-value: {p_value_rating:.3f}")

# Linear regression
X = final_data[["avg_sentiment", "vote_average", "budget"]]
y = final_data["worldwide_gross"]
model = LinearRegression().fit(X, y)
print(f"Linear Regression R^2: {model.score(X, y):.3f}")

# Scatter plot: Sentiment vs. Revenue
plt.figure(figsize=(8, 6))
plt.scatter(final_data["avg_sentiment"], final_data["worldwide_gross"], color="blue")
for i, txt in enumerate(final_data["title"]):
    plt.annotate(txt, (final_data["avg_sentiment"].iloc[i], final_data["worldwide_gross"].iloc[i]))
plt.xlabel("Average Sentiment Score")
plt.ylabel("Worldwide Gross ($)")
plt.title("Sentiment vs. Box Office Revenue")
plt.grid(True)
plt.savefig("sentiment_vs_revenue.png")
plt.close()

# Scatter plot: Vote Average vs. Revenue
plt.figure(figsize=(8, 6))
plt.scatter(final_data["vote_average"], final_data["worldwide_gross"], color="green")
for i, txt in enumerate(final_data["title"]):
    plt.annotate(txt, (final_data["vote_average"].iloc[i], final_data["worldwide_gross"].iloc[i]))
plt.xlabel("TMDb Vote Average")
plt.ylabel("Worldwide Gross ($)")
plt.title("Vote Average vs. Box Office Revenue")
plt.grid(True)
plt.savefig("vote_average_vs_revenue.png")
plt.close()

print("Plots saved as sentiment_vs_revenue.png and vote_average_vs_revenue.png")