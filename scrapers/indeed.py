"""
scrapers/indeed.py — Uses Indeed's public RSS feed instead of scraping HTML.
RSS feeds are officially supported by Indeed and far less likely to be blocked.
"""
 
import logging
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
 
from .utils import fetch, polite_sleep, make_job
 
log = logging.getLogger(__name__)
 
RSS_URL = "https://www.indeed.com/rss"
 
 
def scrape_indeed(cfg: dict) -> list[dict]:
    jobs = []
    categories = cfg["categories"]
    location   = cfg.get("location", "United States")
    max_per_q  = cfg.get("max_results_per_query", 10)
 
    for keyword in cfg["job_keywords"]:
        params = {
            "q":      keyword,
            "l":      location,
            "sort":   "date",
            "fromage": "1",   # posted within 1 day
            "limit":  max_per_q,
        }
        url = f"{RSS_URL}?{urlencode(params)}"
 
        try:
            import requests, random
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/124.0.0.0 Safari/537.36",
                "Accept": "application/rss+xml, application/xml, text/xml, */*",
            }
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
        except Exception as e:
            log.warning(f"  Indeed RSS failed for '{keyword}': {e}")
            polite_sleep()
            continue
 
        items = root.findall(".//item")
        for item in items[:max_per_q]:
            title   = item.findtext("title", "").strip()
            company_loc = item.findtext("source", "") or ""
            link    = item.findtext("link", "").strip()
            date    = item.findtext("pubDate", "")[:16]
 
            # Indeed puts "Job Title - Company" in the title field
            if " - " in title:
                parts   = title.rsplit(" - ", 1)
                title   = parts[0].strip()
                company = parts[1].strip() if len(parts) > 1 else "Unknown"
            else:
                company = "Unknown"
 
            # Location is in the description
            desc_raw = item.findtext("description", "")
            loc = location
            if "<b>location:</b>" in desc_raw.lower():
                import re
                m = re.search(r"location:\s*</b>\s*([^<]+)", desc_raw, re.IGNORECASE)
                if m:
                    loc = m.group(1).strip()
 
            if not title:
                continue
 
            jobs.append(make_job(
                title=title, company=company, location=loc,
                url=link, source="Indeed",
                categories=categories, date_posted=date,
            ))
 
        polite_sleep()
 
    return jobs