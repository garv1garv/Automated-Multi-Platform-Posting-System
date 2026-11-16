from typing import Optional, List
from pydantic import BaseModel, field_validator
import re
from urllib.parse import urlparse

URL_REGEX = re.compile(
    r'(https?://[^\s<>"]+|www\.[^\s<>"]+)',
    re.IGNORECASE
)

class PostMessageRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        content = v.strip()
        if not content:
            raise ValueError("Message cannot be empty.")

        if len(content) > 200:
            raise ValueError(f"Message exceeds maximum allowed length of 200 characters (current length: {len(content)}).")

        found_urls = URL_REGEX.findall(content)

        if len(found_urls) == 0:
            raise ValueError("Message must contain exactly one CTA link. Found 0 links.")
        if len(found_urls) > 1:
            raise ValueError(f"Message must contain exactly one CTA link. Found {len(found_urls)} links: {', '.join(found_urls)}.")

        url = found_urls[0]
        if url.startswith("www."):
            parsed = urlparse("https://" + url)
        else:
            parsed = urlparse(url)

        if not parsed.scheme or parsed.scheme.lower() not in ("http", "https"):
            raise ValueError(f"Invalid URL scheme '{parsed.scheme}'. Only http and https are allowed.")

        if not parsed.netloc or "." not in parsed.netloc:
            raise ValueError(f"Invalid URL domain in '{url}'.")

        return content


class PlatformResult(BaseModel):
    platform: str
    status: str
    posted_url: Optional[str] = None
    public_access: bool
    date: Optional[str] = None
    time: Optional[str] = None
    error: Optional[str] = None


class PostMessageResponse(BaseModel):
    success: bool
    results: List[PlatformResult]
