from urllib.parse import urlparse, urlunparse


def normalize_url(raw_url: str) -> str:
    """Normalize user-entered URLs so internal tools receive a real URL."""

    url = raw_url.strip()
    if not url:
        raise ValueError("URL cannot be empty")

    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
        parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http and https URLs are supported")

    if not parsed.netloc:
        raise ValueError("URL must include a domain")

    return urlunparse(parsed)


def get_origin(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"
