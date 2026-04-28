"""
scrapers/usajobs.py — Scrapes USAJobs.gov via their public REST API.
No API key is required for basic searches.
"""

import logging
import requests

from .utils import polite_sleep, make_job

log = logging.getLogger(__name__)

API_URL = "https://data.usajobs.gov/api/search"

HEADERS = {
    "Host":            "data.usajobs.gov",
    "User-Agent":      "Mozilla/5.0 (educational scraper)",
    "Authorization-Key": "",   # optional — sign up at usajobs.gov/developer for higher limits
}

CS_KEYWORDS = [
    "software engineer",
    "computer scientist",
    "cybersecurity",
    "data scientist",
    "machine learning",
    "information technology",
]


def scrape_usajobs(cfg: dict) -> list[dict]:
    jobs = []
    categories  = cfg["categories"]
    max_per_q   = cfg.get("max_results_per_query", 10)

    for kw in CS_KEYWORDS:
        params = {
            "Keyword":           kw,
            "ResultsPerPage":    max_per_q,
            "SortField":         "OpenDate",
            "SortDirection":     "Desc",
            "StudentIndicator":  "True",   # student / recent grad positions
        }
        try:
            resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            log.warning(f"USAJobs API error for '{kw}': {e}")
            polite_sleep()
            continue

        for item in data.get("SearchResult", {}).get("SearchResultItems", []):
            pos   = item.get("MatchedObjectDescriptor", {})
            title = pos.get("PositionTitle", "")
            if not title:
                continue

            org       = pos.get("OrganizationName", "Federal Agency")
            locations = pos.get("PositionLocation", [{}])
            loc       = locations[0].get("LocationName", "Various") if locations else "Various"
            url       = pos.get("PositionURI", "")
            date      = pos.get("PublicationStartDate", "")[:10]

            jobs.append(make_job(
                title=title, company=org, location=loc,
                url=url, source="USAJobs",
                categories=categories,
                date_posted=date, job_type="Government",
            ))

        polite_sleep()

    return jobs
