import json
from pathlib import Path

RAW_DATA_PATH = Path("data/raw/posts_raw.json")
PROCESSED_DATA_PATH = Path("data/processed/posts_clean.json")
PROCESSED_DATA_PATH.parent.mkdir(parents = True, exist_ok = True)

def processing_function(post):
    return {
        "id": post.get("id"),
        "status": post.get("status"),
        "name": post.get("name"),
        "published_at": post.get("published_at"),
        "created_at": post.get("created_at"),
        "updated_at": post.get("updated_at"),

        "url": post.get("url"),
        "body": post.get("body", {}).get("body"),
        "record_type": post.get("body", {}).get("record_type"),

        "space_id": post.get("space_id"),
        "space_name": post.get("space_name"),
        "community_id": post.get("community_id"),

        "user_id": post.get("user_id"),
        "user_name": post.get("user_name"),
        "user_email": post.get("user_email"),

        "likes_count": post.get("likes_count"),
        "comments_count": post.get("comments_count")
    }

def main():
    print(f"loading raw post data from {RAW_DATA_PATH}...")
    with open(RAW_DATA_PATH, "r") as f:
        raw_posts = json.load(f)

    print(f"processing {len(raw_posts)} posts...")
    clean_posts = [processing_function(post) for post in raw_posts]

    print(f"saving cleaned posts to {PROCESSED_DATA_PATH}...")
    with open(PROCESSED_DATA_PATH, "w") as f:
        json.dump(clean_posts, f, indent = 2)

    print("Cleaned data ready.")

if __name__ == "__main__":
    main()
