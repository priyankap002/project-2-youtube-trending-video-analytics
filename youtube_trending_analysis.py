"""
YouTube Trending Video Analytics
Run:
    pip install -r requirements.txt
    python youtube_trending_analysis.py --input data/youtube_trending_demo.csv

For the full project, download country CSV files (e.g. INvideos.csv, USvideos.csv)
from Kaggle's "Trending YouTube Video Statistics" dataset and place them in data/.
Then run:
    python youtube_trending_analysis.py --input data/INvideos.csv data/USvideos.csv

The bundled demo CSV is synthetic and only demonstrates the workflow. Replace it
with the real Kaggle files for valid research conclusions.
"""
import argparse, re
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob

CATEGORY_MAP = {
    1:"Film & Animation", 2:"Autos & Vehicles", 10:"Music", 15:"Pets & Animals",
    17:"Sports", 19:"Travel & Events", 20:"Gaming", 22:"People & Blogs",
    23:"Comedy", 24:"Entertainment", 25:"News & Politics", 26:"Howto & Style",
    27:"Education", 28:"Science & Technology", 29:"Nonprofits & Activism"
}

def sentiment_label(text):
    polarity = TextBlob(str(text)).sentiment.polarity
    if polarity > 0.05: return "Positive"
    if polarity < -0.05: return "Negative"
    return "Neutral"

def load_and_clean(paths):
    frames = []
    for path in paths:
        df = pd.read_csv(path)
        # Region is inferred from country file name when not supplied.
        if "region" not in df.columns:
            df["region"] = Path(path).stem[:2].upper()
        # Normalize column names and map common source field names.
        df.columns = [c.strip().lower() for c in df.columns]
        if "category_name" not in df.columns and "category_id" in df.columns:
            df["category_name"] = df["category_id"].map(CATEGORY_MAP).fillna("Other")
        if "trending_date" in df.columns:
            raw = df["trending_date"].astype(str)
            parsed = pd.to_datetime(raw, format="%y.%d.%m", errors="coerce")
            df["trending_date"] = parsed.fillna(pd.to_datetime(raw, errors="coerce"))
        elif "date" in df.columns:
            df["trending_date"] = pd.to_datetime(df["date"], errors="coerce")
        for col in ["views","likes","dislikes","comment_count"]:
            if col not in df.columns: df[col] = 0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        for col in ["title","tags","category_name","region"]:
            if col not in df.columns: df[col] = "Unknown"
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()
        frames.append(df)
    data = pd.concat(frames, ignore_index=True)
    data = data.drop_duplicates(subset=["video_id","trending_date","region"], keep="first")
    data = data[(data["views"] >= 0) & (data["likes"] >= 0)]
    data["title_tags"] = data["title"] + " " + data["tags"]
    data["sentiment"] = data["title_tags"].apply(sentiment_label)
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs="+", default=["data/youtube_trending_demo.csv"])
    parser.add_argument("--output", default="outputs")
    args = parser.parse_args()
    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    df = load_and_clean(args.input)
    # Duration = number of distinct days a video appears in trending data.
    duration = (df.groupby(["region","video_id"])["trending_date"]
                  .nunique().rename("trending_days").reset_index())
    df = df.merge(duration, on=["region","video_id"], how="left")
    df.to_csv(out/"cleaned_youtube_trending.csv", index=False)

    # 1. Popular genres by average views
    genre = df.groupby("category_name", as_index=False)["views"].mean().sort_values("views", ascending=False)
    plt.figure(figsize=(10,5))
    plt.barh(genre.head(10)["category_name"], genre.head(10)["views"])
    plt.gca().invert_yaxis()
    plt.title("Top Categories by Average Views"); plt.xlabel("Average views"); plt.ylabel("Category")
    plt.tight_layout(); plt.savefig(out/"category_avg_views.png", dpi=160); plt.close()

    # 2. Sentiment distribution
    plt.figure(figsize=(7,4))
    counts = df["sentiment"].value_counts().reindex(["Positive","Neutral","Negative"], fill_value=0)
    plt.bar(counts.index, counts.values)
    plt.title("Sentiment of Video Titles and Tags"); plt.tight_layout()
    plt.savefig(out/"sentiment_distribution.png", dpi=160); plt.close()

    # 3. Region comparison
    region = df.groupby("region", as_index=False)["views"].mean().sort_values("views", ascending=False)
    plt.figure(figsize=(8,4))
    plt.bar(region["region"], region["views"])
    plt.title("Average Views by Region"); plt.tight_layout()
    plt.savefig(out/"region_comparison.png", dpi=160); plt.close()

    # 4. Trending duration over time
    trend = df.groupby("trending_date", as_index=False).agg(
        video_records=("video_id","count"), avg_views=("views","mean"))
    plt.figure(figsize=(10,4))
    plt.plot(trend["trending_date"], trend["video_records"], marker="o")
    plt.title("Daily Trending Video Records"); plt.xticks(rotation=35)
    plt.tight_layout(); plt.savefig(out/"trending_timeline.png", dpi=160); plt.close()

    # 5. SQL-ready aggregate tables
    genre.to_csv(out/"category_summary.csv", index=False)
    region.to_csv(out/"region_summary.csv", index=False)
    duration.groupby("region", as_index=False)["trending_days"].mean().to_csv(out/"avg_trending_duration.csv", index=False)

    print("Analysis complete.")
    print(f"Rows after cleaning: {len(df):,}")
    print("\\nTop categories by average views:")
    print(genre.head(5).to_string(index=False))
    print("\\nSentiment counts:")
    print(df["sentiment"].value_counts().to_string())
    print("\\nOutputs saved in:", out.resolve())

if __name__ == "__main__":
    main()
