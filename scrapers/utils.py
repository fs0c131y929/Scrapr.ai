"""
scrapers/utils.py — Shared helpers used by every scraper.
"""

import time
import random
import logging
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

# Rotate user-agents to reduce blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
]


def get_headers() -> dict:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.google.com/",
        "DNT": "1",
    }


def fetch(url: str, params: dict = None, timeout: int = 15) -> Optional[BeautifulSoup]:
    """GET a URL and return a BeautifulSoup object, or None on failure."""
    try:
        resp = requests.get(
            url, params=params, headers=get_headers(),
            timeout=timeout, allow_redirects=True
        )
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        log.warning(f"  fetch failed for {url}: {e}")
        return None


def polite_sleep(min_s: float = 1.5, max_s: float = 3.5):
    """Sleep a random amount to avoid rate-limiting."""
    time.sleep(random.uniform(min_s, max_s))


def categorise(title: str, categories: dict) -> str:
    """Map a job title string to one of the configured categories."""
    title_lower = title.lower()
    for category, keywords in categories.items():
        if category == "Other CS Roles":
            continue
        for kw in keywords:
            if kw in title_lower:
                return category
    return "Other CS Roles"


def clean_text(text: Optional[str]) -> str:
    if not text:
        return "N/A"
    return re.sub(r"\s+", " ", text).strip()


def make_job(
    title: str,
    company: str,
    location: str,
    url: str,
    source: str,
    categories: dict,
    description: str = "",
    date_posted: str = "",
    job_type: str = "",
) -> dict:
    """Construct a normalised job dict."""
    return {
        "title":       clean_text(title),
        "company":     clean_text(company),
        "location":    clean_text(location),
        "url":         url.strip() if url else "",
        "source":      source,
        "category":    categorise(title, categories),
        "description": clean_text(description)[:300],
        "date_posted": clean_text(date_posted),
        "job_type":    clean_text(job_type),
    }
