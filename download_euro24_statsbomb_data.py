import os
import pandas as pd
from statsbombpy import sb
from pandas import json_normalize

# === Config ===
SAVE_DIR = "data"
COMP_ID = 55  # Euro
SEASON_ID = 282  # 2024

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(os.path.join(SAVE_DIR, "events_json"), exist_ok=True)
os.makedirs(os.path.join(SAVE_DIR, "events_csv"), exist_ok=True)

# === 1. Download Matches Metadata ===
matches = sb.matches(competition_id=COMP_ID, season_id=SEASON_ID)
matches.to_csv(os.path.join(SAVE_DIR, "euro24_matches.csv"), index=False)
print(f"✅ Saved match metadata ({len(matches)} matches)")

# === 2. Download and Flatten Event Data ===
for _, row in matches.iterrows():
    match_id = row['match_id']
    home = row['home_team']
    away = row['away_team']
    clean_name = f"{match_id}_{home}_vs_{away}".replace(" ", "_")

    print(f"⬇️ Downloading: {home} vs {away} (Match ID: {match_id})")

    try:
        # Download event data
        events_raw = sb.events(match_id=match_id)

        # Save raw JSON
        json_path = os.path.join(SAVE_DIR, "events_json", f"{clean_name}.json")
        events_raw.to_json(json_path, orient='records', lines=True)

        # Flatten event data
        events = json_normalize(
            events_raw.to_dict(orient='records'),
            sep='.'
        )

        # Extract useful nested fields if they exist
        if 'location' in events.columns:
            events['x'] = events['location'].apply(
                lambda loc: loc[0] if isinstance(loc, list) and len(loc) >= 2 else None)
            events['y'] = events['location'].apply(
                lambda loc: loc[1] if isinstance(loc, list) and len(loc) >= 2 else None)
        if 'pass.end_location' in events.columns:
            events['end_x'] = events['pass.end_location'].apply(
                lambda loc: loc[0] if isinstance(loc, list) and len(loc) >= 2 else None)
            events['end_y'] = events['pass.end_location'].apply(
                lambda loc: loc[1] if isinstance(loc, list) and len(loc) >= 2 else None)
        if 'shot.end_location' in events.columns:
            events['shot_end_x'] = events['shot.end_location'].apply(
                lambda loc: loc[0] if isinstance(loc, list) and len(loc) >= 2 else None)
            events['shot_end_y'] = events['shot.end_location'].apply(
                lambda loc: loc[1] if isinstance(loc, list) and len(loc) >= 2 else None)

        # Save as CSV
        csv_path = os.path.join(SAVE_DIR, "events_csv", f"{clean_name}.csv")
        events.to_csv(csv_path, index=False)

    except Exception as e:
        print(f"❌ Error processing match {match_id}: {e}")
        continue

print("🎉 All Euro 2024 event data downloaded, flattened, and saved as CSV + JSON.")
