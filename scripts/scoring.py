import json
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

PROCESSED_DATA_PATH = Path("data/processed/posts_clean.json")
SCORED_DATA_PATH = Path("data/processed/posts_scored.json")

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

def compute_recency_score(published_at_list, decay_hours = 24):
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

def main():
    posts = load_posts()
    likes = [post.get("likes_count", 0) or 0 for post in posts]
    comments = [post.get("comments_count", 0) or 0 for post in posts]
    published_at = [post.get("published_at") for post in posts]

    likes_score = normalize(likes)
    comments_score = normalize(comments)
    recency_score = compute_recency_score(published_at)

    w_likes = 0.3
    w_comments = 0.4
    w_recency = 0.3

    for i, post in enumerate(posts):
        score = (
            w_likes * likes_score[i] +
            w_comments * comments_score[i] +
            w_recency * recency_score[i]
        )
        post["score"] = round(float(score), 6)

    save_posts(posts)
    print(f"Scored posts saved to {SCORED_DATA_PATH}")

if __name__ == "__main__":
    main()
