import requests
import pandas as pd
import time

API_TOKEN = "***REMOVED***"
BASE_URL = "https://app.circle.so/api/admin/v2/posts"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# PAGINATION LOOP
def fetch_all_posts(per_page = 100, max_pages = None, sleep = 0.3):
    all_posts = []
    page = 1
    while True:
        print(f"Fetching page {page}...")
        params = {"page": page, "per_page": per_page, "status": "published"}
        response = requests.get(BASE_URL, headers = HEADERS, params = params)
        if response.status_code != 200:
            print(f"Error fetching page {page}: {response.status_code} - {response.text}")
            break
        data = response.json()
        records = data.get("records", [])
        all_posts.extend(records)
        
        if not data.get("has_next_page", False):
            break
        page += 1
        if max_pages and page > max_pages:
            break
        time.sleep(sleep)

    print(f"\nFetched total posts: {len(all_posts)}")
    return all_posts

# NORMALIZE / FLATTEN POSTS
def posts_to_dataframe(posts):
    # Normalize flat + nested fields of interest
    df = pd.json_normalize(
        posts,
        sep = '_',
        meta = [
            'id',
            'name',
            'slug',
            'published_at',
            'created_at',
            'updated_at',
            'comments_count',
            'likes_count',
            ['author', 'id'],
            ['author', 'name'],
        ],
        record_path = None,
        errors = 'ignore'
    )
    
    df.rename(columns = {
        'id': 'post_id',
        'author_id': 'author_id',
        'author_name': 'author_name',
    }, inplace = True)

    if 'body_body' in df.columns:
        df['body_text'] = df['body_body'].str.replace('<[^<]+?>', '', regex = True)

    return df

# === MAIN RUN ===
if __name__ == "__main__":
    posts_raw = fetch_all_posts(per_page = 100)
    df_posts = posts_to_dataframe(posts_raw)
    
    print("\nSample:")
    print(df_posts[['post_id', 'name', 'likes_count', 'comments_count', 'published_at']].head())

    df_posts.to_csv("circle_posts_data.csv", index = False)
    print("\nData saved to circle_posts_data.csv")
