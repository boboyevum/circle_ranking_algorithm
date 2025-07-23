import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import numpy as np

PROCESSED_DATA_PATH = Path("data/processed/posts_clean.json")
SCORED_DATA_PATH = Path("data/processed/posts_scored.json")

AGE_BUCKETS = [
    (0, 2),
    (3, 5),
    (6, 7),
    (8, 14),
    (15, 30),
    (31, 90),
    (91, 10000),
]

WEIGHTS = {
    'likes': 1,
    'comments': 1,
    'recency': 0.05,
}

RECENCY_DECAY_HOURS = 12

def load_posts():
    with open(PROCESSED_DATA_PATH, "r") as f:
        return json.load(f)

def save_posts(posts):
    with open(SCORED_DATA_PATH, "w") as f:
        json.dump(posts, f, indent = 2)

def normalize(values):
    arr = np.array(values, dtype = float)
    if arr.max() == arr.min():
        return np.ones_like(arr)
    return (arr - arr.min()) / (arr.max() - arr.min())

def compute_age_in_days(published_at):
    now = datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    except Exception:
        dt = now
    delta = now - dt
    return delta.total_seconds() / (3600 * 24)

def compute_recency_score(published_at_list, decay_hours = RECENCY_DECAY_HOURS):
    now = datetime.now(timezone.utc)
    recency_scores = []
    for published_at in published_at_list:
        try:
            dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        except Exception:
            dt = now
        hours_ago = (now - dt).total_seconds() / 3600
        score = np.exp(-hours_ago / decay_hours)
        recency_scores.append(score)
    return np.array(recency_scores)

def assign_scores(posts):
    likes = [post.get("likes_count", 0) or 0 for post in posts]
    comments = [post.get("comments_count", 0) or 0 for post in posts]
    published_at = [post.get("published_at") for post in posts]
    recency_score = compute_recency_score(published_at)
    likes_score = normalize(likes)
    comments_score = normalize(comments)
    recency_score = normalize(recency_score)
    for i, post in enumerate(posts):
        score = (
            WEIGHTS['likes'] * likes_score[i] +
            WEIGHTS['comments'] * comments_score[i] +
            WEIGHTS['recency'] * recency_score[i]
        )
        post["score"] = round(float(score), 6)
    return posts

def bucketize_posts(posts):
    now = datetime.now(timezone.utc)
    buckets = [[] for _ in AGE_BUCKETS]
    for post in posts:
        age_days = compute_age_in_days(post.get("published_at", ""))
        for idx, (start, end) in enumerate(AGE_BUCKETS):
            if start <= age_days <= end:
                buckets[idx].append(post)
                break
    return buckets

def main():
    posts = load_posts()

    posts = assign_scores(posts)

    buckets = bucketize_posts(posts)

    ranked_posts = []
    for bucket in buckets:
        bucket_sorted = sorted(bucket, key = lambda x: x.get("score", 0), reverse = True)
        ranked_posts.extend(bucket_sorted)
    save_posts(ranked_posts)

    print("Top 30 posts (tiered by age, then by score):")
    for idx, post in enumerate(ranked_posts[:30], 1):
        age = int(compute_age_in_days(post.get("published_at", "")))
        print(f"{idx:2d}. Score: {post.get('score', 0):.4f} | Age: {age}d | Title: {post.get('title', '(No Title)')} | Published: {post.get('published_at', 'N/A')} | Likes: {post.get('likes_count', 0)} | Comments: {post.get('comments_count', 0)}")

if __name__ == "__main__":
    main()