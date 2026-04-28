"""
scrapers/simplyhired.py — Scrapes SimplyHired, which is more scraper-friendly
than Indeed or LinkedIn and lists many entry-level positions.
"""

import logging
from urllib.parse import urlencode

from .utils import fetch, polite_sleep, make_job

log = logging.getLogger(__name__)

BASE_URL = "https://www.simplyhired.com/search"


def scrape_simplyhired(cfg: dict) -> list[dict]:
    jobs = []
    categories = cfg["categories"]
    location   = cfg.get("location", "United States")
    max_per_q  = cfg.get("max_results_per_query", 10)

    for keyword in cfg["job_keywords"]:
        params = {
            "q":  keyword,
            "l":  location,
            "fdb": "14",   # last 14 days
        }
        url = f"{BASE_URL}?{urlencode(params)}"
        soup = fetch(url)
        if not soup:
            polite_sleep()
            continue

        cards = soup.select(
            "article[data-jobkey], div[data-testid='searchSerpJob']"
        )
        count = 0

        for card in cards:
            if count >= max_per_q:
                break

            title_el   = card.select_one("h2[data-testid='searchSerpJobTitle'], h3.jobposting-title")
            company_el = card.select_one("span[data-testid='companyName'], span.jobposting-company")
            loc_el     = card.select_one("span[data-testid='searchSerpJobLocation'], span.jobposting-location")
            link_el    = card.select_one("a[data-testid='searchSerpJobTitle'], a.jobposting-permalink")
            date_el    = card.select_one("time, span[data-testid='searchSerpJobDateStamp']")

            title = title_el.get_text(strip=True) if title_el else None
            if not title:
                continue

            company = company_el.get_text(strip=True) if company_el else "Unknown"
            loc     = loc_el.get_text(strip=True)     if loc_el     else location
            href    = link_el["href"]                 if link_el    else ""
            if href and not href.startswith("http"):
                href = "https://www.simplyhired.com" + href
            date    = date_el.get_text(strip=True)    if date_el    else ""

            jobs.append(make_job(title, company, loc, href, "SimplyHired", categories, date_posted=date))
            count += 1

        polite_sleep()

    return jobs
