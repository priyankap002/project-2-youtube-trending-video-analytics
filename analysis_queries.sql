-- YouTube Trending Video Analytics: optional SQL analysis
-- Import outputs/cleaned_youtube_trending.csv into a table named youtube_trending.

-- 1. Rank categories by average views
SELECT category_name, AVG(views) AS avg_views,
       RANK() OVER (ORDER BY AVG(views) DESC) AS category_rank
FROM youtube_trending
GROUP BY category_name
ORDER BY avg_views DESC;

-- 2. Compare average views by region
SELECT region, AVG(views) AS avg_views, SUM(views) AS total_views
FROM youtube_trending
GROUP BY region
ORDER BY avg_views DESC;

-- 3. Sentiment by region
SELECT region, sentiment, COUNT(*) AS video_count
FROM youtube_trending
GROUP BY region, sentiment
ORDER BY region, video_count DESC;

-- 4. Average trending duration by category and region
SELECT region, category_name, AVG(trending_days) AS avg_trending_days
FROM youtube_trending
GROUP BY region, category_name
ORDER BY region, avg_trending_days DESC;
