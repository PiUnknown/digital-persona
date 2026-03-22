import re


def validate_linkedin_url(url: str) -> tuple[bool, str]:
    if not url or not url.strip():
        return False, "URL can't be empty."
    if "linkedin.com/in/" not in url:
        return False, "Needs to be a LinkedIn profile URL (linkedin.com/in/...)"
    if not re.search(r'linkedin\.com/in/[a-zA-Z0-9\-_%]+', url):
        return False, "URL format looks off."
    return True, ""


def validate_twitter_handle(handle: str) -> tuple[bool, str]:
    if not handle or not handle.strip():
        return False, "Handle can't be empty."
    clean = handle.lstrip("@").strip()
    if not re.match(r'^[a-zA-Z0-9_]{1,15}$', clean):
        return False, "Invalid handle — only letters, numbers, underscores (max 15 chars)."
    return True, ""