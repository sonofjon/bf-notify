# bf-notify

A simple Python-based watcher that checks the
[Bostadsförmedlingen](https://bostad.stockholm.se) site for new apartment
listings matching your criteria and emails you a daily summary.

The application can be run manually on a local machine, or, automatically
using GitHub Actions. It then runs once per day, maintaining state in a flat
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
- Filters by district, size, room count, and rent.
- Skips special-purpose listings (youth, student, senior, short-term).
- Tracks seen apartment IDs in `seen.json`.
- Sends email via any SMTP server (Gmail, Mailgun, etc.).
- Scheduled daily (08:00 UTC) with GitHub Actions.

## Prerequisites

- Python 3.7+ for local testing.
- An SMTP account that supports TLS (e.g. Gmail with an App password).
- A GitHub account and a repository to host this code.

## Installation

### Local Testing

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

### GitHub Actions

1. Fork this repository on GitHub (your fork will host the workflow).
2. No local install needed — the Actions runner installs the required dependencies.

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

In your **fork** on GitHub, go to **Settings → Secrets and variables → Actions** and add these secrets:

- `SMTP_SERVER`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `EMAIL_TO`

No other configuration is needed.

## Usage

### Local Testing

1. Initialize or reset your seen-IDs file:
   ```bash
   echo "[]" > seen.json
   ```
2. Run the watcher:
   ```bash
   python apartments.py
   ```
3. Inspect your inbox (for any matches) and `seen.json` (for new IDs).

### GitHub Actions

1. Push or merge any changes to your fork.
2. In your fork on GitHub, go to **Actions → Daily apartment check → Run workflow** to trigger it.
3. The workflow will thereafter run automatically each day at 08:00 UTC, send emails for new listings, and update `seen.json` in your repo.

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
