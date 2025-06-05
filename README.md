# bf-notify

A simple Python watcher that checks
[Bostadsförmedlingen](https://bostad.stockholm.se) for new apartments
matching your criteria and emails you a daily summary.

The application can be run manually on a local machine, or, automatically
using GitHub Actions. It then runs once per day, maintaining state in a flat
JSON-file, so you only get notified once per listing.

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [GitHub Actions](#github-actions)
7. [Custom Filters](#custom-filters)

## Features

- Fetches all listings from `https://bostad.stockholm.se/AllaAnnonser`.
- Filters by district, size, room count, and rent.
- Skips special-purpose listings (youth, student, senior, short-term).
- Tracks seen apartment IDs in `seen.json`.
- Sends email summaries via any SMTP server.
- Scheduled daily (08:00 UTC) with GitHub Actions (optional).

## Prerequisites

- Python 3.7+
- An SMTP account that supports TLS (e.g. Gmail with App password)
- A GitHub account and a repository to host this code.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/sonofjon/bf-notify.git
   cd bf-notify
   ```
2. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Export the required environment variables in your shell:

```bash
export SMTP_SERVER=smtp.example.com
export SMTP_PORT=587
export SMTP_USER=your_smtp_username
export SMTP_PASSWORD=your_smtp_password
export EMAIL_FROM=alerts@example.com
export EMAIL_TO=you@example.com
```

## Usage

Just run:

```bash
python apartments.py
```

## GitHub Actions

To automate:

1. Fork or clone this repo into your own GitHub account.
2. In your fork, go to **Settings → Secrets and variables → Actions**.
3. Add new secrets for each of the six environment variables above.

The repo includes a workflow (`.github/workflows/daily.yml`) that:

1. Checks out your repo
2. Installs dependencies
3. Runs `python apartments.py`
4. Commits & pushes back any changes to `seen.json`

To trigger it manually:

1. In your fork, go to **Actions → Daily apartment check**
2. Click **Run workflow**

The workflow runs automatically at 08:00 UTC every day.

## Custom Filters

All the filtering logic lives at the top of `apartments.py`:

```python
WANT_DISTRICTS = {"Södermalm", "Långholmen", "Reimerholme"}  # desired areas
SKIP_TYPES = ["Ungdom", "Student", "Senior", "Korttid"]  # types to skip

# Size in m2
MIN_SIZE = 35   # minimum square meters, or None to disable
MAX_SIZE = None # maximum square meters, or None to disable

# Room count
MIN_ROOMS = None  # minimum rooms, or None to disable
MAX_ROOMS = 2     # maximum rooms, or None to disable

# Rent in kr/month
MIN_RENT = None   # minimum rent, or None to disable
MAX_RENT = None   # maximum rent, or None to disable
```

Adjust these values to match your preferences.
