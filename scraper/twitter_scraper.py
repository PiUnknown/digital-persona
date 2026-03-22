import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")
ACTOR = "apidojo~tweet-scraper"


def scrape_twitter(handle: str) -> list:
    if not APIFY_TOKEN:
        raise ValueError("Missing APIFY_API_TOKEN in .env")

    username = handle.lstrip("@").strip()
    url = f"https://twitter.com/{username}"

    resp = requests.post(
        f"https://api.apify.com/v2/acts/{ACTOR}/runs",
        json={"startUrls": [url], "maxItems": 10},
        headers={"Content-Type": "application/json"},
        params={"token": APIFY_TOKEN}
    )

    if resp.status_code != 201:
        raise ConnectionError(f"Apify run failed to start: {resp.text}")

    run_id = resp.json()["data"]["id"]
    print(f"Twitter run started: {run_id}")

    status_url = f"https://api.apify.com/v2/acts/{ACTOR}/runs/{run_id}"
    for _ in range(40):
        time.sleep(3)
        r = requests.get(status_url, params={"token": APIFY_TOKEN})
        status = r.json()["data"]["status"]

        if status == "SUCCEEDED":
            break
        if status in ["FAILED", "ABORTED", "TIMED-OUT"]:
            raise RuntimeError(f"Twitter scraping failed: {status}")
    else:
        raise TimeoutError("Twitter scraping timed out")

    dataset_id = r.json()["data"]["defaultDatasetId"]
    tweets = requests.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items",
        params={"token": APIFY_TOKEN}
    ).json()

    if not tweets:
        raise ValueError("No tweets found — account might be private.")

    return tweets


def parse_twitter_to_text(tweets: list, handle: str) -> str:
    username = handle.lstrip("@").strip()
    lines = [f"\n--- Twitter/X (@{username}) ---"]

    own_tweets = [t for t in tweets if not t.get("isRetweet", False)]

    if own_tweets:
        lines.append("Recent tweets:")
        for t in own_tweets[:10]:
            text = t.get("text", "").replace("\n", " ")
            likes = t.get("likeCount", 0)
            rts = t.get("retweetCount", 0)
            date = t.get("createdAt", "")[:16]
            lines.append(f"  - [{date}] {text}")
            lines.append(f"    Likes: {likes} | Retweets: {rts}")
    else:
        lines.append("No recent tweets found.")

    return "\n".join(lines)


def get_twitter_knowledge_base(handle: str) -> str:
    username = handle.lstrip("@").strip()
    print(f"Scraping Twitter: @{username}")
    tweets = scrape_twitter(username)
    text = parse_twitter_to_text(tweets, username)
    print("Twitter data ready.")
    return text


if __name__ == "__main__":
    print(get_twitter_knowledge_base("BillGates"))