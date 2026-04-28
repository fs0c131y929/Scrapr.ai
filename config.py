"""
config.py — All user-editable settings.
This is the only file you need to edit.
"""

# ─────────────────────────────────────────────────────────────────────────────
#  SEARCH KEYWORDS  — add or remove anything you like
# ─────────────────────────────────────────────────────────────────────────────
JOB_KEYWORDS = [
    "new grad software engineer",
    "entry level software engineer",
    "junior software developer",
    "new grad machine learning engineer",
    "entry level AI engineer",
    "junior data scientist",
    "entry level cybersecurity analyst",
    "new grad security engineer",
    "entry level robotics engineer",
    "new grad robotics software",
    "new grad DevOps engineer",
    "entry level cloud engineer",
    "new grad site reliability engineer",
]

RESEARCH_KEYWORDS = [
    "REU computer science 2025",
    "summer research program computer science undergraduate",
    "NSF REU machine learning",
    "research internship machine learning 2025",
]

# ─────────────────────────────────────────────────────────────────────────────
#  JOB CATEGORIES  — controls grouping in the HTML report
# ─────────────────────────────────────────────────────────────────────────────
CATEGORIES = {
    "Software Engineering": [
        "software engineer", "software developer", "swe", "backend", "frontend",
        "full stack", "fullstack", "web developer",
    ],
    "Machine Learning / AI": [
        "machine learning", "ml engineer", "ai engineer", "data scientist",
        "deep learning", "nlp", "computer vision",
    ],
    "Cybersecurity": [
        "security", "cybersecurity", "penetration", "soc analyst", "infosec",
    ],
    "Robotics": [
        "robotics", "autonomous", "embedded systems", "controls engineer",
    ],
    "Cloud / DevOps / SRE": [
        "devops", "cloud engineer", "site reliability", "sre", "platform engineer",
        "infrastructure",
    ],
    "Research / REU": [
        "research", "reu", "fellowship", "undergraduate research",
    ],
    "Other CS Roles": [],
}

# ─────────────────────────────────────────────────────────────────────────────
#  LOCATION  — set to "" to search everywhere, or e.g. "Remote", "New York, NY"
# ─────────────────────────────────────────────────────────────────────────────
LOCATION = "United States"

# ─────────────────────────────────────────────────────────────────────────────
#  MAX RESULTS PER KEYWORD PER SOURCE
# ─────────────────────────────────────────────────────────────────────────────
MAX_RESULTS_PER_QUERY = 10


def load_config() -> dict:
    return {
        "job_keywords":          JOB_KEYWORDS,
        "research_keywords":     RESEARCH_KEYWORDS,
        "categories":            CATEGORIES,
        "location":              LOCATION,
        "max_results_per_query": MAX_RESULTS_PER_QUERY,
        "ntfy_topic":            NTFY_TOPIC,
    }

# ─────────────────────────────────────────────────────────────────────────────
#  PHONE NOTIFICATIONS via ntfy.sh (free, no account needed)
#  1. Download the "ntfy" app on your phone (iOS or Android)
#  2. Make up any unique topic name and put it here, e.g. "mike-job-alerts-8472"
#  3. In the app, subscribe to that same topic name
#  That's it -- the scraper will ping your phone when each run finishes.
#  Leave blank to disable:  NTFY_TOPIC = ""
# ─────────────────────────────────────────────────────────────────────────────
NTFY_TOPIC = "job_alerts"   