import os
import pandas as pd
from statsbombpy import sb
from pandas import json_normalize

# === CONFIG ===
SAVE_DIR = "data"
COMP_ID = 55    # UEFA Euro Championship (customized by user)
SEASON_ID = 282 # Euro 2024 season (customized by user)

EVENTS_JSON_DIR = os.path.join(SAVE_DIR, "events_json")
EVENTS_CSV_DIR = os.path.join(SAVE_DIR, "events_csv")
LOG_FILE = os.path.join(SAVE_DIR, "download_errors.txt")

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(EVENTS_JSON_DIR, exist_ok=True)
os.makedirs(EVENTS_CSV_DIR, exist_ok=True)

# === Coordinate extractor ===
def extract_coord(val, index):
    try:
        if isinstance(val, list) and len(val) > index:
            return val[index]
    except:
        pass
    return None

# === Step 1: Download match metadata ===
matches = sb.matches(competition_id=COMP_ID, season_id=SEASON_ID)
matches.to_csv(os.path.join(SAVE_DIR, "euro24_matches.csv"), index=False)
print(f"✅ Saved metadata for {len(matches)} matches.")

# === Step 2: Loop over matches and extract event data ===
for _, row in matches.iterrows():
    match_id = row['match_id']
    home = row['home_team']
    away = row['away_team']
    match_name = f"{match_id}_{home}_vs_{away}".replace(" ", "_")

    try:
        print(f"⬇️ Downloading: {home} vs {away} (Match ID: {match_id})")

        # Download events
        events_raw = sb.events(match_id=match_id)

        # Save raw JSON
        json_path = os.path.join(EVENTS_JSON_DIR, f"{match_name}.json")
        events_raw.to_json(json_path, orient='records', lines=True)

        # Flatten the JSON
        events = json_normalize(events_raw.to_dict(orient='records'), sep='.')

        # === Flatten key location fields ===

        # Location
        events['x'] = events['location'].apply(lambda loc: extract_coord(loc, 0))
        events['y'] = events['location'].apply(lambda loc: extract_coord(loc, 1))

        # Pass end location
        if 'pass.end_location' in events.columns:
            events['end_x'] = events['pass.end_location'].apply(lambda loc: extract_coord(loc, 0))
            events['end_y'] = events['pass.end_location'].apply(lambda loc: extract_coord(loc, 1))
        else:
            events['end_x'] = None
            events['end_y'] = None

        # Carry end location
        if 'carry.end_location' in events.columns:
            carry_x = events['carry.end_location'].apply(lambda loc: extract_coord(loc, 0))
            carry_y = events['carry.end_location'].apply(lambda loc: extract_coord(loc, 1))
            events['end_x'] = events['end_x'].combine_first(carry_x)
            events['end_y'] = events['end_y'].combine_first(carry_y)

        # Shot end location
        if 'shot.end_location' in events.columns:
            events['shot_end_x'] = events['shot.end_location'].apply(lambda loc: extract_coord(loc, 0))
            events['shot_end_y'] = events['shot.end_location'].apply(lambda loc: extract_coord(loc, 1))

        # Save CSV
        csv_path = os.path.join(EVENTS_CSV_DIR, f"{match_name}.csv")
        events.to_csv(csv_path, index=False)

    except Exception as e:
        with open(LOG_FILE, "a") as log:
            log.write(f"{match_id} - {home} vs {away} - ERROR: {e}\n")
        print(f"❌ Failed to process {match_id}: {e}")
        continue

print("🎉 All Euro 2024 matches processed. Flattened CSV and JSON saved.")
