import os
import json
import smtplib
from email.message import EmailMessage
import requests

# 1. load seen IDs
SEEN_PATH = "seen.json"
try:
    seen = set(json.load(open(SEEN_PATH)))
except FileNotFoundError:
    seen = set()

# 2. fetch all apartments
r = requests.get("https://bostad.stockholm.se/AllaAnnonser")
data = r.json()

# 3. your filters
WANT_DISTRICTS = {"Södermalm", "Långholmen", "Reimerholme"}  # desired areas
MIN_SIZE = 35  # minimum square meters
MAX_ROOMS = 2  # maximum number of rooms
SKIP_FLAGS = ["Ungdom", "Student", "Senior", "Korttid"]  # types to skip

new_items = []
for apt in data:
    # 1) skip if any of these flags are true
    if any(apt.get(flag, False) for flag in SKIP_FLAGS):
        continue

    # 2) stadsdel/size/room guard
    stadsdel = apt.get("Stadsdel")
    rum = apt.get("AntalRum")
    yta = apt.get("Yta")
    if yta is None or rum is None or stadsdel is None:
        continue

    # 3) filters
    if stadsdel in WANT_DISTRICTS and rum <= MAX_ROOMS and yta >= MIN_SIZE:
        lid = apt["LägenhetId"]
        if lid not in seen:
            new_items.append(apt)
            seen.add(lid)

# 4. if new, send email
if new_items:
    msg = EmailMessage()
    msg["Subject"] = f"New apartments: {len(new_items)}"
    msg["From"] = os.environ["EMAIL_FROM"]
    msg["To"] = os.environ["EMAIL_TO"]

    lines = []
    for a in new_items:
        lines.append(
            f"{a['Stadsdel']} – {a['Gatuadress']} – "
            f"{a['AntalRum']} rum – {a['Yta']} m2 – "
            f"{a['Hyra']} kr/månad – "
            f"https://bostad.stockholm.se{a['Url']}"
        )
    msg.set_content("\n".join(lines))

    # SMTP send
    with smtplib.SMTP(os.environ["SMTP_SERVER"], int(os.environ["SMTP_PORT"])) as smtp:
        smtp.starttls()
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        smtp.send_message(msg)

# 5. write back seen.json
with open(SEEN_PATH, "w") as f:
    json.dump(sorted(seen), f)
