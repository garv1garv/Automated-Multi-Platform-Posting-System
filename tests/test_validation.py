import pytest
from pydantic import ValidationError
from app.schemas import PostMessageRequest

def test_valid_message():
    valid_text = "Check out our latest business platform and grow your online visibility. https://example.com"
    req = PostMessageRequest(message=valid_text)
    assert req.message == valid_text

def test_message_exceeds_200_chars():
    long_text = "a" * 185 + " https://example.com"
    assert len(long_text) > 200
    with pytest.raises(ValidationError) as excinfo:
        PostMessageRequest(message=long_text)
    assert "exceeds maximum allowed length of 200 characters" in str(excinfo.value)

def test_message_no_url():
    no_url_text = "Check out our latest business platform without any links."
    with pytest.raises(ValidationError) as excinfo:
        PostMessageRequest(message=no_url_text)
    assert "Message must contain exactly one CTA link. Found 0 links." in str(excinfo.value)

def test_message_multiple_urls():
    multi_url_text = "Visit https://example.com and check https://another.com"
    with pytest.raises(ValidationError) as excinfo:
        PostMessageRequest(message=multi_url_text)
    assert "Message must contain exactly one CTA link. Found 2 links" in str(excinfo.value)

def test_empty_message():
    with pytest.raises(ValidationError):
        PostMessageRequest(message="   ")

def test_invalid_url_scheme():
    invalid_scheme = "Check out ftp://files.example.com for data."
    with pytest.raises(ValidationError) as excinfo:
        PostMessageRequest(message=invalid_scheme)
    # Regex only matches http/https/www, so this triggers 0 links or invalid scheme
    assert "CTA link" in str(excinfo.value)

