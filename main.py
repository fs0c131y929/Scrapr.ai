"""
CS Job & Research Opportunity Scraper
======================================
Scrapes new-grad CS roles and research opportunities,
opens an HTML report, and sends a phone notification when done.

Run once:           python main.py
Run on a schedule:  python main.py --schedule
Custom interval:    python main.py --schedule --every 6    (every 6 hours)
"""

import sys
import logging
import webbrowser
import argparse
import time
import requests
import schedule
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from scrapers.indeed import scrape_indeed
from scrapers.linkedin import scrape_linkedin
from scrapers.simplyhired import scrape_simplyhired
from scrapers.research import scrape_reu_opportunities
from scrapers.usajobs import scrape_usajobs
from config import load_config

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("scraper.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

CATEGORY_COLORS = {
    "Software Engineering":  "#3B82F6",
    "Machine Learning / AI": "#8B5CF6",
    "Cybersecurity":         "#EF4444",
    "Robotics":              "#F59E0B",
    "Cloud / DevOps / SRE":  "#10B981",
    "Research / REU":        "#06B6D4",
    "Other CS Roles":        "#6B7280",
}


# ── Notification ─────────────────────────────────────────────────────────────
def notify(cfg: dict, title: str, message: str):
    """Send a push notification via ntfy.sh (free, no account needed)."""
    topic = cfg.get("ntfy_topic", "")
    if not topic:
        return
    try:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers={
                "Title":    title,
                "Priority": "default",
                "Tags":     "briefcase",
            },
            timeout=10,
        )
        log.info("Notification sent!")
    except Exception as e:
        log.warning(f"Notification failed: {e}")


# ── HTML builder ──────────────────────────────────────────────────────────────
def build_html(jobs: list) -> str:
    today = datetime.now().strftime("%B %d, %Y  %I:%M %p")
    grouped = defaultdict(list)
    for j in jobs:
        grouped[j.get("category", "Other CS Roles")].append(j)

    cards_html = ""
    for cat, color in CATEGORY_COLORS.items():
        items = grouped.get(cat, [])
        if not items:
            continue
        cards_html += f"""
        <div class="section">
          <h2 style="color:{color};border-color:{color}">{cat}
            <span class="count">{len(items)}</span>
          </h2>
          <div class="grid">
        """
        for j in items:
            desc = j.get("description", "")
            desc_block = f'<p class="desc">{desc[:200]}{"..." if len(desc) > 200 else ""}</p>' if desc and desc != "N/A" else ""
            date = f'<span class="meta">Posted: {j["date_posted"]}</span>' if j.get("date_posted") else ""
            cards_html += f"""
            <div class="card" style="border-top:3px solid {color}">
              <div class="card-meta">
                <span class="source">{j['source']}</span>
                {date}
              </div>
              <a class="title" href="{j['url']}" target="_blank">{j['title']}</a>
              <p class="company">Company: {j['company']} | Location: {j['location']}</p>
              {desc_block}
              <a class="btn" href="{j['url']}" target="_blank" style="background:{color}">View and Apply</a>
            </div>
            """
        cards_html += "</div></div>"

    summary_pills = "".join(
        f'<div class="pill" style="border-color:{color}">'
        f'<span class="pill-num" style="color:{color}">{len(grouped.get(cat,[]))}</span>'
        f'<span class="pill-label">{cat}</span></div>'
        for cat, color in CATEGORY_COLORS.items() if grouped.get(cat)
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CS Job Digest -- {today}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #F1F5F9; color: #1E293B; padding: 24px 16px; }}
  .header {{ background: linear-gradient(135deg,#0F172A,#1E3A5F);
             border-radius: 16px; padding: 36px; text-align: center; margin-bottom: 24px; }}
  .header h1 {{ color: #fff; font-size: 28px; font-weight: 800; letter-spacing: -0.5px; }}
  .header p  {{ color: #94A3B8; font-size: 14px; margin-top: 6px; }}
  .pills {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 28px; justify-content: center; }}
  .pill {{ background: #fff; border: 2px solid; border-radius: 10px;
           padding: 10px 16px; text-align: center; min-width: 120px; }}
  .pill-num   {{ display: block; font-size: 22px; font-weight: 800; }}
  .pill-label {{ display: block; font-size: 11px; color: #64748B; margin-top: 2px; font-weight: 500; }}
  .section {{ margin-bottom: 36px; }}
  .section h2 {{ font-size: 19px; font-weight: 700; padding-bottom: 10px;
                 border-bottom: 2px solid; margin-bottom: 16px;
                 display: flex; align-items: center; gap: 10px; }}
  .count {{ background: #F1F5F9; color: #64748B; font-size: 13px;
            font-weight: 600; padding: 2px 9px; border-radius: 20px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 14px; }}
  .card {{ background: #fff; border-radius: 12px; padding: 18px;
           box-shadow: 0 1px 4px rgba(0,0,0,.07); display: flex;
           flex-direction: column; gap: 8px; }}
  .card-meta {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
  .source {{ background: #F1F5F9; color: #475569; font-size: 11px;
             font-weight: 600; padding: 2px 8px; border-radius: 6px; }}
  .meta   {{ color: #94A3B8; font-size: 11px; }}
  .title  {{ color: #0F172A; font-size: 15px; font-weight: 700;
             text-decoration: none; line-height: 1.35; }}
  .title:hover {{ text-decoration: underline; }}
  .company {{ color: #475569; font-size: 13px; }}
  .desc    {{ color: #64748B; font-size: 12px; line-height: 1.5; }}
  .btn    {{ display: inline-block; color: #fff; padding: 7px 14px; border-radius: 7px;
             font-size: 12px; font-weight: 600; text-decoration: none;
             margin-top: auto; align-self: flex-start; }}
  .btn:hover {{ opacity: 0.85; }}
  .footer {{ text-align: center; color: #94A3B8; font-size: 12px; margin-top: 32px; }}
</style>
</head>
<body>
  <div class="header">
    <h1>CS New-Grad Job Digest</h1>
    <p>Generated {today} | {len(jobs)} unique listings (past 24 hours)</p>
  </div>
  <div class="pills">{summary_pills}</div>
  {cards_html}
  <div class="footer">
    <p>Apply early -- new-grad roles fill fast! | Re-run python main.py to refresh.</p>
  </div>
</body>
</html>"""


# ── Scrape pipeline ───────────────────────────────────────────────────────────
def run():
    log.info("Starting scrape run...")
    cfg = load_config()
    all_jobs = []

    scrapers = [
        ("Indeed",       scrape_indeed),
        ("LinkedIn",     scrape_linkedin),
        ("SimplyHired",  scrape_simplyhired),
        ("REU/Research", scrape_reu_opportunities),
        ("USAJobs",      scrape_usajobs),
    ]

    for name, fn in scrapers:
        try:
            log.info(f"Scraping {name}...")
            results = fn(cfg)
            log.info(f"  {len(results)} listings found")
            all_jobs.extend(results)
        except Exception as e:
            log.error(f"  FAILED {name}: {e}")

    # Deduplicate
    seen, unique = set(), []
    for j in all_jobs:
        key = (j["title"].lower().strip(), j["company"].lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(j)

    unique.sort(key=lambda j: (j.get("category", ""), j.get("source", "")))
    log.info(f"Total unique listings: {len(unique)}")

    # Save + open report
    out = Path("job_report.html")
    out.write_text(build_html(unique), encoding="utf-8")
    log.info(f"Report saved to {out.resolve()}")
    webbrowser.open(out.resolve().as_uri())

    # Notify
    by_cat = defaultdict(int)
    for j in unique:
        by_cat[j.get("category", "Other")] += 1
    summary = ", ".join(f"{v} {k}" for k, v in list(by_cat.items())[:4])
    notify(
        cfg,
        title=f"Job Digest Ready -- {len(unique)} listings",
        message=f"New roles found: {summary}. Report is open in your browser.",
    )

    log.info("Done!\n")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CS Job Scraper")
    parser.add_argument("--schedule", action="store_true",
                        help="Run on a repeating schedule")
    parser.add_argument("--every", type=int, default=24,
                        help="How often to run in hours (default: 24)")
    args = parser.parse_args()

    if args.schedule:
        log.info(f"Scheduled mode: running every {args.every} hour(s). Press Ctrl+C to stop.")
        run()  # run immediately on start
        schedule.every(args.every).hours.do(run)
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        run()