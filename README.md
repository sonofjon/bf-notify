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
- Supports multiple independent queries with different filter criteria.
- Filters by municipality, district, apartment type, size, room count, and rent.
- Include or exclude specific municipalities, districts, and apartment types.
- Tracks seen apartment IDs per query in `seen_*.json` files.
- Sends separate email per query with matching apartments.
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

Run the apartment watcher:

```bash
python run.py
```

## GitHub Actions

To automate:

1. Fork or clone this repo into your own GitHub account.
2. In your fork, go to **Settings → Secrets and variables → Actions**.
3. Add new secrets for each of the six environment variables above.

The repo includes a workflow (`.github/workflows/daily.yml`) that:

1. Checks out your repo
2. Installs dependencies
3. Runs `python run.py`
4. Commits & pushes back any changes to `seen_*.json` files

To trigger it manually:

1. In your fork, go to **Actions → Daily apartment check**
2. Click **Run workflow**

The workflow runs automatically at 08:00 UTC every day.

## Custom Filters

Define multiple queries in `config.json`. Each query runs independently with
its own tracking and sends a separate email.

### Example Configuration

```json
{
  "skip_incomplete": false,
  "queries": [
    {
      "id": 0,
      "name": "1-2 room apartments (with min size)",
      "include_municipalities": null,
      "exclude_municipalities": null,
      "include_districts": ["Södermalm", "Långholmen", "Reimersholme"],
      "exclude_districts": null,
      "include_types": null,
      "exclude_types": ["Ungdom", "Student", "Senior", "Korttid"],
      "size": {"min": 35, "max": null},
      "rooms": {"min": null, "max": 2},
      "rent": {"min": null, "max": null}
    },
    {
      "id": 1,
      "name": "3-room apartments (with max price)",
      "include_municipalities": null,
      "exclude_municipalities": null,
      "include_districts": ["Södermalm", "Långholmen", "Reimersholme"],
      "exclude_districts": null,
      "include_types": null,
      "exclude_types": ["Ungdom", "Student", "Senior", "Korttid"],
      "size": {"min": null, "max": null},
      "rooms": {"min": 3, "max": 3},
      "rent": {"min": null, "max": 12000}
    },
    {
      "id": 2,
      "name": "1-3 room apartments (short-term, with max price)",
      "include_municipalities": null,
      "exclude_municipalities": null,
      "include_districts": ["Södermalm", "Långholmen", "Reimersholme"],
      "exclude_districts": null,
      "include_types": ["Korttid"],
      "exclude_types": null,
      "size": {"min": null, "max": null},
      "rooms": {"min": null, "max": 3},
      "rent": {"min": null, "max": 15000}
    }
  ]
}
```

### Configuration Fields

**Global Settings**

**`skip_incomplete`**
- Whether to skip apartments with missing data (size, rent, etc.)
- Set to `false` to include apartments even if they have missing fields
- Note: About 10% of apartments have missing size/rent data

**Per-Query Settings**

**`id`**
- Unique numeric identifier for the query

**`name`**
- Human-readable query name

**`include_municipalities`**
- List of municipalities to include in results
- Example: `["Stockholm", "Solna"]`

**`exclude_municipalities`**
- List of municipalities to exclude from results
- Example: `["Järfälla", "Botkyrka"]`

**`include_districts`**
- List of districts to include in results
- Example: `["Södermalm", "Långholmen"]`

**`exclude_districts`**
- List of districts to exclude from results
- Example: `["Farsta", "Skärholmen"]`

**`include_types`**
- List of apartment types to include in results
- Example: `["Vanlig", "Korttid"]`

**`exclude_types`**
- List of apartment types to exclude from results
- Example: `["Ungdom", "Student", "Senior", "BostadSnabbt"]`

**`size`**
- Square meter limits
- Example: `{"min": 35, "max": null}`

**`rooms`**
- Room count limits
- Example: `{"min": 3, "max": 3}`

**`rent`**
- Monthly rent limits in SEK
- Example: `{"min": null, "max": 15000}`

**Apartment types**

The following types are available (mutually exclusive):
- `Vanlig` - Regular apartments (most common)
- `Student` - Student housing
- `Ungdom` - Youth housing
- `Senior` - Senior housing
- `Korttid` - Short-term rentals
- `BostadSnabbt` - Fast housing program

### Important Notes

- Use `null` to disable any filter or limit (matches all values)
- Each query ID must be unique
- For municipalities, districts, and types: only one of the include or exclude variants can be non-null in each query
- To add a new query, use the next available `id` number
