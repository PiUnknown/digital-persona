import re

def validate_linkedin_url(url: str) -> tuple[bool, str]:
    if not url or not url.strip():
        return False, "URL cannot be empty."
    if "linkedin.com/in/" not in url:
        return False, "Invalid LinkedIn URL. Must contain 'linkedin.com/in/'"
    pattern = r'linkedin\.com/in/[a-zA-Z0-9\-_%]+'
    if not re.search(pattern, url):
        return False, "Invalid LinkedIn profile URL format."
    return True, ""


def validate_twitter_handle(handle: str) -> tuple[bool, str]:
    if not handle or not handle.strip():
        return False, "Twitter handle cannot be empty."
    # Strip @ if present
    clean = handle.lstrip("@").strip()
    if not clean:
        return False, "Invalid Twitter handle."
    pattern = r'^[a-zA-Z0-9_]{1,15}$'
    if not re.match(pattern, clean):
        return False, "Invalid Twitter handle format. Only letters, numbers, underscores allowed (max 15 chars)."
    return True, ""