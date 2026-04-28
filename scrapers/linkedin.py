"""
scrapers/linkedin.py — Scrapes LinkedIn's public job search (no login required).
Uses the /jobs/search endpoint that returns results without authentication.
"""

import logging
from urllib.parse import urlencode
 
from .utils import fetch, polite_sleep, make_job
 
log = logging.getLogger(__name__)
 
BASE_URL = "https://www.linkedin.com/jobs/search/"
 
# LinkedIn time filter values:
#   r3600    = past 1 hour
#   r86400   = past 24 hours  <-- we use this
#   r604800  = past week
#   r1209600 = past 2 weeks
 
 
def scrape_linkedin(cfg: dict) -> list[dict]:
    jobs = []
    categories = cfg["categories"]
    location   = cfg.get("location", "United States")
    max_per_q  = cfg.get("max_results_per_query", 10)
 
    for keyword in cfg["job_keywords"]:
        params = {
            "keywords": keyword,
            "location": location,
            "f_E":      "1,2",       # Entry level + Associate
            "f_TPR":    "r86400",    # Past 24 hours only
            "sortBy":   "DD",        # Sort by date posted (newest first)
            "position": 1,
            "pageNum":  0,
        }
        url = f"{BASE_URL}?{urlencode(params)}"
        soup = fetch(url)
        if not soup:
            polite_sleep(2, 5)
            continue
 
        cards = soup.select("div.base-card, li.jobs-search__results-list")
        count = 0
 
        for card in cards:
            if count >= max_per_q:
                break
 
            title_el   = card.select_one("h3.base-search-card__title, span.screen-reader-text")
            company_el = card.select_one("h4.base-search-card__subtitle, a.hidden-nested-link")
            loc_el     = card.select_one("span.job-search-card__location")
            link_el    = card.select_one("a.base-card__full-link, a[href*='/jobs/view/']")
            date_el    = card.select_one("time")
 
            title = title_el.get_text(strip=True) if title_el else None
            if not title:
                continue
 
            company = company_el.get_text(strip=True) if company_el else "Unknown"
            loc     = loc_el.get_text(strip=True)     if loc_el     else location
            href    = link_el["href"]                 if link_el    else ""
            date    = date_el.get("datetime", "")     if date_el    else ""
 
            jobs.append(make_job(title, company, loc, href, "LinkedIn", categories, date_posted=date))
            count += 1
 
        polite_sleep(2, 4)
 
    return jobs