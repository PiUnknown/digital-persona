import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")
ACTOR = "apimaestro~linkedin-profile-detail"


def scrape_linkedin(url: str) -> dict:
    if not APIFY_TOKEN:
        raise ValueError("Missing APIFY_API_TOKEN in .env")

    if "linkedin.com/in/" not in url:
        raise ValueError("That doesn't look like a LinkedIn profile URL.")

    resp = requests.post(
        f"https://api.apify.com/v2/acts/{ACTOR}/runs",
        json={"username": url, "includeEmail": False},
        headers={"Content-Type": "application/json"},
        params={"token": APIFY_TOKEN}
    )

    if resp.status_code != 201:
        raise ConnectionError(f"Apify wouldn't start the run: {resp.text}")

    run_id = resp.json()["data"]["id"]
    print(f"Run started: {run_id}")

    # poll until done
    status_url = f"https://api.apify.com/v2/acts/{ACTOR}/runs/{run_id}"
    for _ in range(30):
        time.sleep(3)
        r = requests.get(status_url, params={"token": APIFY_TOKEN})
        status = r.json()["data"]["status"]

        if status == "SUCCEEDED":
            break
        if status in ["FAILED", "ABORTED", "TIMED-OUT"]:
            raise RuntimeError(f"Scraping failed with status: {status}")
    else:
        raise TimeoutError("Scraping timed out after 90s")

    dataset_id = r.json()["data"]["defaultDatasetId"]
    items = requests.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items",
        params={"token": APIFY_TOKEN}
    ).json()

    if not items:
        raise ValueError("Got no data back — profile might be private.")

    return items[0]


def parse_to_text(data: dict) -> str:
    basic = data.get("basic_info", {})
    chunks = []

    chunks.append(f"Name: {basic.get('fullname', 'N/A')}")
    chunks.append(f"Headline: {basic.get('headline', 'N/A')}")
    chunks.append(f"Location: {basic.get('location', {}).get('full', 'N/A')}")
    chunks.append(f"About: {basic.get('about', 'N/A')}")
    chunks.append(f"Current Company: {basic.get('current_company', 'N/A')}")
    chunks.append(f"Followers: {basic.get('follower_count', 'N/A')}")
    chunks.append(f"Profile URL: {basic.get('profile_url', 'N/A')}")

    hashtags = basic.get("creator_hashtags", [])
    if hashtags:
        chunks.append(f"Topics they post about: {', '.join(hashtags)}")

    chunks.append("")

    experience = data.get("experience", [])
    if experience:
        chunks.append("Experience:")
        for exp in experience:
            chunks.append(f"  - {exp.get('title')} at {exp.get('company')} ({exp.get('duration', '')})")
    else:
        chunks.append("Experience: Not listed")

    chunks.append("")

    education = data.get("education", [])
    if education:
        chunks.append("Education:")
        for edu in education:
            entry = f"  - {edu.get('school', 'N/A')}"
            if edu.get("duration"):
                entry += f" ({edu['duration']})"
            if edu.get("degree"):
                entry += f" — {edu['degree']}"
            chunks.append(entry)
    else:
        chunks.append("Education: Not listed")

    chunks.append("")

    skills = basic.get("top_skills", [])
    if skills:
        chunks.append(f"Skills: {', '.join(skills)}")
        chunks.append("")

    featured = data.get("featured", [])
    if featured:
        chunks.append("Featured Posts:")
        for post in featured:
            title = post.get("title", "")
            desc = post.get("description", "")
            likes = post.get("social_counts", {}).get("likes", 0)
            if title:
                chunks.append(f"  - {title}")
            if desc:
                short = desc[:300] + "..." if len(desc) > 300 else desc
                chunks.append(f"    {short}")
            if likes:
                chunks.append(f"    Likes: {likes}")

    return "\n".join(chunks)


def get_linkedin_knowledge_base(url: str) -> str:
    print(f"Scraping: {url}")
    data = scrape_linkedin(url)
    return parse_to_text(data)


if __name__ == "__main__":
    print(get_linkedin_knowledge_base("https://www.linkedin.com/in/williamhgates/"))