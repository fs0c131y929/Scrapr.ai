# CS New-Grad Job Scraper

Automatically scrapes new-graduate CS, software engineering, machine learning, cybersecurity, and robotics roles — plus summer research / REU opportunities — from multiple sources. Opens a formatted HTML report in your browser and sends a phone notification when done.

---

## What It Scrapes

| Source | What |
|---|---|
| LinkedIn | Entry-level roles, past 24 hours, sorted by newest |
| Indeed | New-grad roles via RSS feed |
| SimplyHired | Aggregated entry-level listings |
| NSF REU | Summer undergraduate research sites |
| Handshake | University research postings |
| USAJobs | Federal government CS/tech roles |

---

## Project Structure

```
JobScraper/
├── main.py               ← Run this
├── config.py             ← Edit this to customise keywords, location, notifications
├── requirements.txt
├── README.md
└── scrapers/
    ├── __init__.py
    ├── utils.py
    ├── indeed.py
    ├── linkedin.py
    ├── simplyhired.py
    ├── research.py
    └── usajobs.py
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure settings

Open `config.py` and adjust:

- **`JOB_KEYWORDS`** — add or remove search terms
- **`LOCATION`** — e.g. `"Remote"`, `"New York, NY"`, or `"United States"`
- **`MAX_RESULTS_PER_QUERY`** — how many results per keyword per source
- **`NTFY_TOPIC`** — your ntfy topic name for phone notifications (see below)

---

## Running

### Run once
```bash
python main.py
```

### Run on a schedule (keeps running, press Ctrl+C to stop)
```bash
python main.py --schedule              # every 24 hours (default)
python main.py --schedule --every 8   # every 8 hours
python main.py --schedule --every 12  # every 12 hours
```

The scraper runs immediately on start, then repeats on the chosen interval. Leave the terminal open in VS Code to keep it running.

---

## Phone Notifications (Optional)

Uses [ntfy.sh](https://ntfy.sh) — free, no account required.

1. Download the **ntfy** app on your phone (available on iOS and Android)
2. Make up a unique topic name, e.g. `yourname-jobs-1234`
3. In the app, tap **Subscribe** and enter that topic name
4. In `config.py`, set:
```python
NTFY_TOPIC = "yourname-jobs-1234"
```

You will get a push notification on your phone each time a scrape run finishes.

---

## Output

Each run saves a `job_report.html` file in the project folder and opens it automatically in your browser. Jobs are grouped by category with colour-coded cards:

- Software Engineering
- Machine Learning / AI
- Cybersecurity
- Robotics
- Cloud / DevOps / SRE
- Research / REU
- Other CS Roles

---

## Pushing to GitHub

### First time setup

**1. Create a new repo on GitHub**
- Go to [github.com](https://github.com) and sign in
- Click the **+** icon in the top right and select **New repository**
- Give it a name (e.g. `job-scraper`), leave it empty (no README, no .gitignore), and click **Create repository**

**2. Initialise git in your project folder**

Open the terminal in VS Code (`Ctrl+`` `) and run:

```bash
git init
git add .
git commit -m "Initial commit"
```

**3. Connect to GitHub and push**

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repo name.

---

### Pushing future updates

After making any changes to the code:

```bash
git add .
git commit -m "Describe what you changed"
git push
```

---

### Pulling updates on another machine

```bash
git pull
pip install -r requirements.txt
python main.py
```

---

## .gitignore

The repo includes a `.gitignore` that excludes:

```
scraper.log       ← log file generated on each run
job_report.html   ← HTML report generated on each run
__pycache__/
*.pyc
```

These are generated files that do not need to be in version control.
