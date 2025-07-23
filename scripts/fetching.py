import requests
import json
from pathlib import Path

API_TOKEN = "***REMOVED***"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

BASE_POSTS_URL = "https://app.circle.so/api/admin/v2/posts"

RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents = True, exist_ok = True)

# PAGINATED FETCH FUNCTION
def fetch_all(endpoint, per_page = 100, max_pages = None):
    all_data = []
    page = 1
    while True:
        print(f"fetching {endpoint} - page #{page}...")
        response = requests.get(
            endpoint,
            headers = HEADERS,
            params = {"page": page, "per_page": per_page}
        )
        if response.status_code != 200:
            print(f"error fetching page {page}: {response.status_code} - {response.text}")
            break

        data = response.json()
        records = data.get("records", [])
        all_data.extend(records)

        if not data.get("has_next_page", False):
            break
        page += 1
        if max_pages and page > max_pages:
            break

    print(f"Fetching complete. Total fetched from {endpoint.split('/')[-1]}: {len(all_data)}")
    return all_data

# MAIN FUNCTION
if __name__ == "__main__":
    print("\nfetching all posts...")
    posts = fetch_all(BASE_POSTS_URL)
    with open(RAW_DATA_DIR / "posts_raw.json", "w") as f:
        json.dump(posts, f, indent = 2)

    print("\nData saved to 'data/raw/' folder.")
