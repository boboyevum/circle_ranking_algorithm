import json
import os
from datetime import datetime, timezone
import numpy as np

RAW_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'posts_raw.json')
OUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'posts_scored.json')

WEIGHTS = {
    'likes': 1,
    'comments': 1,
    'recency': 0.05,
}

AGE_BINS = [2, 5, 7, 15, 30, 90]  # days

BIN_LABELS = [
    '0-2', '3-5', '6-7', '8-15', '16-30', '31-90', '>90'
]

def normalize(values):
    arr = np.array(values, dtype=float)
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

def compute_recency_score(published_at_list, decay_hours=12):
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

def get_age_bin(age):
    for i, upper in enumerate(AGE_BINS):
        if age <= upper:
            return i
    return len(AGE_BINS)

def main():
    with open(RAW_PATH, encoding='utf-8') as f:
        posts = json.load(f)

    for post in posts:
        age = compute_age_in_days(post.get('published_at', ''))
        post['age_days'] = age
        post['age_bin'] = get_age_bin(age)

    bucketed = {}
    for i in range(len(AGE_BINS)+1):
        bucketed[i] = []
    for post in posts:
        bucketed[post['age_bin']].append(post)

    ordered = []
    for bin_idx in range(len(AGE_BINS)+1):
        bin_posts = bucketed[bin_idx]
        if not bin_posts:
            continue
        scored = assign_scores(bin_posts)
        scored_sorted = sorted(scored, key = lambda x: x['score'], reverse = True)
        ordered.extend(scored_sorted)

    for post in ordered:
        post.pop('age_days', None)
        post.pop('age_bin', None)

    with open(OUT_PATH, 'w', encoding = 'utf-8') as f:
        json.dump(ordered, f, indent = 2)
    print(f"Wrote {len(ordered)} posts to {OUT_PATH}")

if __name__ == '__main__':
    main() 