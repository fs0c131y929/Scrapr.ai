"""
scrapers/research.py — Scrapes summer research / REU opportunities from:
  - NSF REU site search (nsf.gov)
  - pathways.gov (federal internships / research)
  - research.gov programme search
  - Handshake public listings (unauthenticated search)

These pages change layout frequently — multiple selector fallbacks are used.
"""

import logging
from urllib.parse import urlencode, urljoin

from .utils import fetch, polite_sleep, make_job

log = logging.getLogger(__name__)


# ── NSF REU Search ────────────────────────────────────────────────────────────
def _scrape_nsf_reu(cfg: dict) -> list[dict]:
    """
    NSF hosts a searchable directory of REU sites at
    https://www.nsf.gov/crssprgm/reu/reu_search.jsp
    """
    categories = cfg["categories"]
    jobs = []

    url = "https://www.nsf.gov/crssprgm/reu/list_result.jsp"
    params = {
        "keyword":  "computer science",
        "Submit":   "Search",
    }
    soup = fetch(url, params=params)
    if not soup:
        return jobs

    rows = soup.select("table.REUsiteResult tr, tr.searchResultItem")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        title   = cols[0].get_text(strip=True)
        inst    = cols[1].get_text(strip=True) if len(cols) > 1 else "NSF"
        loc     = cols[2].get_text(strip=True) if len(cols) > 2 else "Various"
        link_el = cols[0].find("a")
        href    = urljoin("https://www.nsf.gov", link_el["href"]) if link_el else url

        if not title or "site title" in title.lower():
            continue

        jobs.append(make_job(
            title=f"REU: {title}",
            company=inst,
            location=loc,
            url=href,
            source="NSF REU",
            categories=categories,
            job_type="Research / REU",
        ))

    polite_sleep()
    return jobs


# ── pathways.gov (Federal Internships) ───────────────────────────────────────
def _scrape_pathways(cfg: dict) -> list[dict]:
    """
    USAJobs Pathways Internship Programme — federal CS / STEM internships.
    """
    categories = cfg["categories"]
    jobs = []

    url = "https://www.usajobs.gov/Search/Results"
    params = {
        "p":          1,
        "k":          "computer science intern",
        "hp":         "student",
        "s":          "salary",
        "sd":         "asc",
    }
    soup = fetch(url, params=params)
    if not soup:
        return jobs

    cards = soup.select("div.usajobs-search-result--core, li.usajobs-search-result")
    for card in cards[:cfg.get("max_results_per_query", 10)]:
        title_el   = card.select_one("h2 a, h3 a, a.usajobs-search-result--core__title")
        company_el = card.select_one("p.usajobs-search-result--core__agency, span.agency")
        loc_el     = card.select_one("p.usajobs-search-result--core__location, span.location")

        title   = title_el.get_text(strip=True)   if title_el   else None
        if not title:
            continue
        company = company_el.get_text(strip=True) if company_el else "Federal Agency"
        loc     = loc_el.get_text(strip=True)     if loc_el     else "Various"
        href    = urljoin("https://www.usajobs.gov", title_el["href"]) if title_el else url

        jobs.append(make_job(
            title=title, company=company, location=loc,
            url=href, source="Pathways (USAJobs)",
            categories=categories, job_type="Federal Internship / Research",
        ))

    polite_sleep()
    return jobs


# ── Handshake public listings ────────────────────────────────────────────────
def _scrape_handshake(cfg: dict) -> list[dict]:
    """
    Handshake's public search endpoint (no auth required for public listings).
    """
    categories = cfg["categories"]
    jobs = []

    research_terms = [
        "summer research undergraduate computer science",
        "REU fellowship machine learning",
    ]

    for kw in research_terms:
        params = {
            "query":      kw,
            "page":       1,
            "per_page":   cfg.get("max_results_per_query", 10),
            "job_types[]": "268",   # research / internship type IDs on Handshake
        }
        url = f"https://app.joinhandshake.com/jobs?{urlencode(params)}"
        soup = fetch(url)
        if not soup:
            polite_sleep()
            continue

        cards = soup.select("li[data-hook='jobs-card'], div.job-listing-card")
        for card in cards[:cfg.get("max_results_per_query", 10)]:
            title_el   = card.select_one("a[data-hook='job-card-title'], h3 a")
            company_el = card.select_one("span[data-hook='employer-name'], p.employer-name")
            loc_el     = card.select_one("span[data-hook='job-location'], p.location")

            title   = title_el.get_text(strip=True)   if title_el   else None
            if not title:
                continue
            company = company_el.get_text(strip=True) if company_el else "Unknown"
            loc     = loc_el.get_text(strip=True)     if loc_el     else "Various"
            href    = title_el["href"]                if title_el    else url
            if href and not href.startswith("http"):
                href = "https://app.joinhandshake.com" + href

            jobs.append(make_job(
                title=title, company=company, location=loc,
                url=href, source="Handshake",
                categories=categories, job_type="Research / Internship",
            ))

        polite_sleep()

    return jobs


# ── Google Scholar / MIT PRIMES-style fallback ────────────────────────────────
def _scrape_research_gov(cfg: dict) -> list[dict]:
    """
    Scrape research.gov programme listings for CS-related opportunities.
    """
    categories = cfg["categories"]
    jobs = []

    url  = "https://new.nsf.gov/funding/opportunities"
    params = {"q": "undergraduate research computer science"}
    soup = fetch(url, params=params)
    if not soup:
        return jobs

    items = soup.select("article.opportunity-card, div[class*='opportunity']")
    for item in items[:cfg.get("max_results_per_query", 10)]:
        title_el = item.select_one("h2 a, h3 a, a[class*='title']")
        desc_el  = item.select_one("p[class*='description'], div[class*='desc']")

        title = title_el.get_text(strip=True) if title_el else None
        if not title:
            continue
        desc  = desc_el.get_text(strip=True) if desc_el else ""
        href  = urljoin("https://new.nsf.gov", title_el["href"]) if title_el else url

        jobs.append(make_job(
            title=title, company="NSF", location="Various (US)",
            url=href, source="NSF Funding",
            categories=categories,
            description=desc, job_type="Research Grant / Fellowship",
        ))

    polite_sleep()
    return jobs


def scrape_reu_opportunities(cfg: dict) -> list[dict]:
    """Aggregate all research / REU scrapers."""
    results = []
    for fn in [_scrape_nsf_reu, _scrape_pathways, _scrape_handshake, _scrape_research_gov]:
        try:
            results.extend(fn(cfg))
        except Exception as e:
            log.warning(f"Research sub-scraper {fn.__name__} failed: {e}")
    return results
