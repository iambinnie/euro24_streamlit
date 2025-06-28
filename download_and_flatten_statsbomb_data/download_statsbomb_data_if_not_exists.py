import os
import pandas as pd
from statsbombpy import sb
from datetime import datetime

from config.constants import ERRORS_DIR, MATCH_META_PATH, COMP_ID, SEASON_ID

# === Ensure error log dir exists (in case someone skips step 1) ===
os.makedirs(ERRORS_DIR, exist_ok=True)

# === Step 1: Load or Download match metadata ===
if os.path.exists(MATCH_META_PATH):
    matches = pd.read_csv(MATCH_META_PATH)
    print(f"Loaded existing match metadata: {len(matches)} matches.")
else:
    matches = sb.matches(competition_id=COMP_ID, season_id=SEASON_ID)
    matches.to_csv(MATCH_META_PATH, index=False)
    print(f"Downloaded and saved match metadata: {len(matches)} matches.")

# === Step 2: Download raw event data for each match ===
downloaded_count = 0
for _, row in matches.iterrows():
    match_id = row["match_id"]
    home = row["home_team"]
    away = row["away_team"]
    filename = f"{match_id}_{home}_vs_{away}".replace(" ", "_") + ".json"
    filepath = os.path.join(RAW_DIR, filename)

    if os.path.exists(filepath):
        print(f"Exists: {filename}")
        continue

    try:
        print(f"Downloading: {home} vs {away} (match_id={match_id})")
        events = sb.events(match_id=match_id)
        events.to_json(filepath, orient="records", lines=True)
        downloaded_count += 1
    except Exception as e:
        with open(ERROR_LOG_PATH, "a", encoding="utf-8") as log:
            log.write(f"[{datetime.now().isoformat()}] {match_id} - {home} vs {away} - ERROR: {str(e)}\n")
        print(f"ERROR downloading match {match_id}: {e}")

print(f"\nDownload complete. {downloaded_count} new files saved.")
print(f"Raw files located in: {RAW_DIR}")
