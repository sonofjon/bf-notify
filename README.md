# bf-notify

A simple Python-based watcher that checks the
[Bostadsförmedlingen](https://bostad.stockholm.se) site for new apartment
listings matching your criteria and emails you a daily summary.

Runs once per day via GitHub Actions (free), maintaining state in a flat
JSON-file, so you only get notified once per listing.

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Custom Filters](#custom-filters)

## Features

- Fetches all apartments from `https://bostad.stockholm.se/AllaAnnonser`.
- Filters by district, size, room count, rent.
- Skips special-purpose listings (youth, student, senior, short-term).
- Tracks seen apartment IDs in `seen.json`.
- Sends email via any SMTP server (Gmail, Mailgun, etc.).
- Scheduled daily (08:00 UTC) with GitHub Actions.

## Prerequisites

- Python 3.7+ for local testing.
- An SMTP account of your choice that supports TLS (e.g. Gmail with an App Password).
- A GitHub account and a repository to host this code.

## Installation

### Local Testing

1. Clone or fork this repository.
2. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### GitHub Actions

No additional setup is required in the repository itself beyond committing your code and workflow file. Dependencies are installed automatically by the workflow.

## Configuration

### Local Testing

Before running locally, export the required environment variables in your shell:

```bash
export SMTP_SERVER=smtp.example.com
export SMTP_PORT=587
export SMTP_USER=your_smtp_username
export SMTP_PASSWORD=your_smtp_password
export EMAIL_FROM=alerts@example.com
export EMAIL_TO=you@example.com
```

### GitHub Actions

In your GitHub repository, go to **Settings → Secrets and variables → Actions** and add these same six secrets:

- `SMTP_SERVER`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `EMAIL_TO`

## Usage

### Local Testing

1. Make sure `seen.json` is present and empty (or has previous IDs):
   ```bash
   echo "[]" > seen.json
   ```
2. Run the watcher:
   ```bash
   python apartments.py
   ```
3. Check your inbox for an email summary (if any matches) and inspect `seen.json` for added IDs.

### GitHub Actions

Once the code and workflow are pushed to your GitHub repo:

1. Navigate to **Actions → Daily apartment check → Run workflow** to test it immediately.
2. The workflow will also run automatically every day at 08:00 UTC, fetch new listings, send you an email, and update `seen.json`.

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
