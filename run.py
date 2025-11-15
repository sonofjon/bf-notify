"""Watch Stockholm housing site for new apartments and email summaries.

Fetches listings from bostad.stockholm.se, applies user-defined filters,
tracks seen IDs in JSON files, and sends notifications via SMTP. Supports
multiple independent queries, each with its own filter criteria and
tracking.

Author: Andreas Jonsson
Contact: ajdev8@gmail.com
GitHub: https://github.com/sonofjon/bf-notify
"""

import json
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

import requests


def load_config():
    """Load and validate configuration from config.json.

    Returns the parsed configuration dictionary.

    Raises SystemExit if config is invalid (missing file, duplicate IDs).
    """
    config_path = Path("config.json")
    try:
        with config_path.open() as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config.json: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate unique IDs
    ids = [query["id"] for query in config["queries"]]
    if len(ids) != len(set(ids)):
        duplicates = [id_ for id_ in ids if ids.count(id_) > 1]
        print(
            f"Error: Duplicate query IDs found: {set(duplicates)}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate exclude_municipalities and include_municipalities mutual
    # exclusivity
    for query in config["queries"]:
        exclude_municipalities = query.get("exclude_municipalities")
        include_municipalities = query.get("include_municipalities")
        if (exclude_municipalities is not None and
                include_municipalities is not None):
            query_id = query["id"]
            query_name = query["name"]
            print(
                f"Error: Query {query_id} ('{query_name}') has both "
                f"exclude_municipalities and include_municipalities set. "
                f"Only one can be non-null.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Validate exclude_districts and include_districts mutual exclusivity
    for query in config["queries"]:
        exclude_districts = query.get("exclude_districts")
        include_districts = query.get("include_districts")
        if exclude_districts is not None and include_districts is not None:
            query_id = query["id"]
            query_name = query["name"]
            print(
                f"Error: Query {query_id} ('{query_name}') has both "
                f"exclude_districts and include_districts set. Only one can "
                f"be non-null.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Validate exclude_types and include_types mutual exclusivity
    for query in config["queries"]:
        exclude_types = query.get("exclude_types")
        include_types = query.get("include_types")
        if exclude_types is not None and include_types is not None:
            query_id = query["id"]
            query_name = query["name"]
            print(
                f"Error: Query {query_id} ('{query_name}') has both "
                f"exclude_types and include_types set. Only one can be "
                f"non-null.",
                file=sys.stderr,
            )
            sys.exit(1)

    return config


def load_seen(query_id):
    """Load seen apartment IDs for a specific query.

    Returns a set of apartment IDs that have been previously seen.
    """
    seen_path = Path(f"seen_{query_id}.json")
    try:
        with seen_path.open() as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


def save_seen(query_id, seen):
    """Save seen apartment IDs for a specific query."""
    seen_path = Path(f"seen_{query_id}.json")
    with seen_path.open("w") as f:
        json.dump(sorted(seen), f)


def matches_query(apt, query, skip_incomplete):
    """Check if apartment matches query criteria.

    Returns True if the apartment matches all filters in the query.
    """
    # Extract data fields
    municipality = apt.get("Kommun")
    district = apt.get("Stadsdel")
    rooms = apt.get("AntalRum")
    size = apt.get("Yta")
    rent = apt.get("Hyra")

    # Skip items with missing data (if enabled)
    if skip_incomplete:
        if None in (district, municipality, rooms, size, rent):
            return False

    # Filter by municipality
    exclude_municipalities = query.get("exclude_municipalities")
    include_municipalities = query.get("include_municipalities")

    if exclude_municipalities is not None:
        # Exclude apartments in these municipalities
        if municipality in exclude_municipalities:
            return False

    if include_municipalities is not None:
        # Only include apartments in these municipalities
        if municipality not in include_municipalities:
            return False

    # Filter by district
    exclude_districts = query.get("exclude_districts")
    include_districts = query.get("include_districts")

    if exclude_districts is not None:
        # Exclude apartments in these districts
        if district in exclude_districts:
            return False

    if include_districts is not None:
        # Only include apartments in these districts
        if district not in include_districts:
            return False

    # Filter by apartment type (mutually exclusive)
    exclude_types = query.get("exclude_types")
    include_types = query.get("include_types")

    if exclude_types is not None:
        # Exclude apartments with these types
        if any(apt.get(flag, False) for flag in exclude_types):
            return False

    if include_types is not None:
        # Only include apartments with these types
        if not any(apt.get(flag, False) for flag in include_types):
            return False

    min_size = query["size"]["min"]
    max_size = query["size"]["max"]
    if min_size is not None and size is not None and size < min_size:
        return False
    if max_size is not None and size is not None and size > max_size:
        return False

    min_rooms = query["rooms"]["min"]
    max_rooms = query["rooms"]["max"]
    if min_rooms is not None and rooms is not None and rooms < min_rooms:
        return False
    if max_rooms is not None and rooms is not None and rooms > max_rooms:
        return False

    min_rent = query["rent"]["min"]
    max_rent = query["rent"]["max"]
    if min_rent is not None and rent is not None and rent < min_rent:
        return False
    if max_rent is not None and rent is not None and rent > max_rent:
        return False

    return True


def send_email(query_name, apartments):
    """Send email notification for new apartments."""
    msg = EmailMessage()
    msg["Subject"] = f"New apartments: {query_name}"
    msg["From"] = os.environ["EMAIL_FROM"]
    msg["To"] = os.environ["EMAIL_TO"]

    lines = [
        f"{a['Stadsdel']} - {a['Gatuadress']} - "
        f"{a['AntalRum']} rum - {a['Yta']} m2 - "
        f"{a['Hyra']} kr/mån - "
        f"https://bostad.stockholm.se{a['Url']}"
        for a in apartments
    ]
    msg.set_content("\n".join(lines))

    with smtplib.SMTP(
        os.environ["SMTP_SERVER"], int(os.environ["SMTP_PORT"])
    ) as smtp:
        smtp.starttls()
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        smtp.send_message(msg)


def main():
    """Run all queries from config.json."""
    # Load configuration
    config = load_config()
    skip_incomplete = config.get("skip_incomplete", True)

    # Fetch apartment data
    print("Fetching apartment data...")
    r = requests.get("https://bostad.stockholm.se/AllaAnnonser", timeout=10)
    apartments = r.json()

    # Process each query
    for query in config["queries"]:
        query_id = query["id"]
        query_name = query["name"]
        print(f"Processing query {query_id}: {query_name}")

        # Load seen IDs for this query
        seen = load_seen(query_id)

        # Find matching apartments
        new_items = []
        for apt in apartments:
            if matches_query(apt, query, skip_incomplete):
                lid = apt["LägenhetId"]
                if lid not in seen:
                    new_items.append(apt)
                    seen.add(lid)

        # Send email if new apartments found
        if new_items:
            print(f"  Found {len(new_items)} new apartment(s)")
            send_email(query_name, new_items)
        else:
            print("  No new apartments")

        # Save updated seen list
        save_seen(query_id, seen)

    print("Done")


if __name__ == "__main__":
    main()
