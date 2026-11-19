# YouTube Trending Video Analytics (Python)

## Objective
Analyze trending YouTube videos across regions to understand category popularity, title/tag sentiment, regional view patterns, and how long videos remain trending.

## Dataset
- Recommended real dataset: [Trending YouTube Video Statistics on Kaggle](https://www.kaggle.com/datasets/datasnaek/youtube-new)
- Download country CSV files such as `INvideos.csv`, `USvideos.csv`, `GBvideos.csv`, and their category JSON files if available.
- Put the CSV files inside `data/`.
- `data/youtube_trending_demo.csv` is a small **synthetic demo dataset** included so the code can run immediately. Do not present its results as real-world findings.

## Setup
```bash
pip install -r requirements.txt
python -m textblob.download_corpora
```

## Run with demo data
```bash
python youtube_trending_analysis.py --input data/youtube_trending_demo.csv
```

## Run with real multi-country data
```bash
python youtube_trending_analysis.py --input data/INvideos.csv data/USvideos.csv data/GBvideos.csv
```

## Outputs
- `outputs/cleaned_youtube_trending.csv`
- Category average views, sentiment, regional comparison, and timeline PNG charts
- CSV summary tables for Tableau
- SQL examples in `analysis_queries.sql`

## Methods
1. Load and combine country CSV files.
2. Standardize text, dates, and numeric fields; remove duplicate video-region-date records.
3. Map category IDs to category names.
4. Apply TextBlob polarity to title + tags and classify as Positive, Neutral, or Negative.
5. Calculate trending duration as the number of distinct trending dates for each video and region.
6. Export charts and summary tables; use SQL queries for ranking and Tableau for dashboarding.

## Tableau dashboard suggestion
Connect Tableau to `cleaned_youtube_trending.csv` or the summary CSV files. Add KPI cards (video records, average views, average trending days), bar charts for category and region, a sentiment split, a date trend line, and filters for region/category/sentiment.

## Limitations
The historical Kaggle dataset is from an earlier period and is not a live feed. TextBlob measures simple lexical polarity; it may misread sarcasm, slang, emojis, and multilingual titles. Trending duration is only observable within the dates present in the downloaded dataset.
