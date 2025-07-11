"""Watch Stockholm housing site for new apartments and email daily summaries.

Fetches listings from bostad.stockholm.se, applies user-defined filters,
tracks seen IDs in a JSON file, and sends notifications via SMTP.

Author: Andreas jonsson
Contact: ajdev8@gmail.com
GitHub: https://github.com/sonofjon/bf-notify
"""

import json
import os
import smtplib
from email.message import EmailMessage

import requests

# 1. Load seen IDs
SEEN_PATH = "seen.json"
try:
    with open(SEEN_PATH) as f:
        seen = set(json.load(f))
except FileNotFoundError:
    seen = set()

# 2. Fetch all apartments
r = requests.get("https://bostad.stockholm.se/AllaAnnonser", timeout=10)
data = r.json()

# 3. Define filters
WANT_DISTRICTS = {"Södermalm", "Långholmen", "Reimerholme", "Skeppsholmen",
                  "Gamla Stan"}  # desired areas
SKIP_TYPES = ["Ungdom", "Student", "Senior", "Korttid"]  # types to skip

# Size in m2
MIN_SIZE = 35  # minimum square meters, or None to disable
MAX_SIZE = None  # maximum square meters, or None to disable

# Room count
MIN_ROOMS = None  # minimum rooms, or None to disable
MAX_ROOMS = 2  # maximum rooms, or None to disable

# Rent in kr/month
MIN_RENT = None  # minimum rent, or None to disable
MAX_RENT = None  # maximum rent, or None to disable

new_items = []
for apt in data:
    # 1) Skip unwanted types
    if any(apt.get(flag, False) for flag in SKIP_TYPES):
        continue

    # 2) Skip items with missing data
    district = apt.get("Stadsdel")
    rooms = apt.get("AntalRum")
    size = apt.get("Yta")
    rent = apt.get("Hyra")
    if None in (district, rooms, size, rent):
        continue

    # 3) Apply filters
    if (
        district in WANT_DISTRICTS
        and (MIN_SIZE is None or size >= MIN_SIZE)
        and (MAX_SIZE is None or size <= MAX_SIZE)
        and (MIN_ROOMS is None or rooms >= MIN_ROOMS)
        and (MAX_ROOMS is None or rooms <= MAX_ROOMS)
        and (MIN_RENT is None or rent >= MIN_RENT)
        and (MAX_RENT is None or rent <= MAX_RENT)
    ):
        lid = apt["LägenhetId"]
        if lid not in seen:
            new_items.append(apt)
            seen.add(lid)

# 4. If new, send email
if new_items:
    msg = EmailMessage()
    msg["Subject"] = f"New apartments: {len(new_items)}"
    msg["From"] = os.environ["EMAIL_FROM"]
    msg["To"] = os.environ["EMAIL_TO"]

    lines = [
        f"{a['Stadsdel']} - {a['Gatuadress']} - "
        f"{a['AntalRum']} rum - {a['Yta']} m2 - "
        f"{a['Hyra']} kr/mån - "
        f"https://bostad.stockholm.se{a['Url']}"
        for a in new_items
    ]
    msg.set_content("\n".join(lines))

    with smtplib.SMTP(
        os.environ["SMTP_SERVER"], int(os.environ["SMTP_PORT"])
    ) as smtp:
        smtp.starttls()
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        smtp.send_message(msg)

# 5. Write back seen.json
with open(SEEN_PATH, "w") as f:
    json.dump(sorted(seen), f)
