"""
Flatten all raw Euro-24 StatsBomb JSON files into per-match CSV files
and produce one combined CSV suitable for analysis.

Assumes:
    - Raw JSONs are in RAW_DIR
    - Match metadata is available at MATCH_META_PATH
Outputs:
    - Per-match CSVs in FLATTENED_DIR
    - Combined file: BASE_DATA_DIR/euro24_all_events_combined.csv
    - Error log: ERRORS_DIR/flatten_errors.txt
"""

import os
import glob
import json
from datetime import datetime

import pandas as pd
from pandas import json_normalize

from config.constants import (
    RAW_DIR,
    FLATTENED_DIR,
    BASE_DATA_DIR,
    MATCH_META_PATH,
    ERRORS_DIR,
)

COMBINED_CSV_PATH = os.path.join(BASE_DATA_DIR, "euro24_all_events_combined.csv")
ERROR_LOG_PATH = os.path.join(ERRORS_DIR, "flatten_errors.txt")


def extract_coord(val, index):
    try:
        if isinstance(val, list) and len(val) > index:
            return val[index]
    except Exception:
        pass
    return None


def flatten_match(json_path: str, csv_path: str, matches_df: pd.DataFrame):
    """Flatten a single match's raw JSON data into a flat CSV with metadata."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f]

        events = json_normalize(records, sep=".")

        # === Coordinates ===
        events["x"] = events["location"].apply(lambda loc: extract_coord(loc, 0))
        events["y"] = events["location"].apply(lambda loc: extract_coord(loc, 1))

        if "pass.end_location" in events.columns:
            events["end_x"] = events["pass.end_location"].apply(lambda loc: extract_coord(loc, 0))
            events["end_y"] = events["pass.end_location"].apply(lambda loc: extract_coord(loc, 1))
        else:
            events["end_x"] = None
            events["end_y"] = None

        if "carry.end_location" in events.columns:
            carry_x = events["carry.end_location"].apply(lambda loc: extract_coord(loc, 0))
            carry_y = events["carry.end_location"].apply(lambda loc: extract_coord(loc, 1))
            events["end_x"] = events["end_x"].combine_first(carry_x)
            events["end_y"] = events["end_y"].combine_first(carry_y)

        if "shot.end_location" in events.columns:
            events["shot_end_x"] = events["shot.end_location"].apply(lambda loc: extract_coord(loc, 0))
            events["shot_end_y"] = events["shot.end_location"].apply(lambda loc: extract_coord(loc, 1))

        # === Inject Match Metadata ===
        match_id = int(os.path.basename(json_path).split("_")[0])
        match_meta = matches_df[matches_df["match_id"] == match_id]

        if match_meta.empty:
            raise ValueError(f"Match ID {match_id} not found in metadata.")

        home = match_meta["home_team"].values[0]
        away = match_meta["away_team"].values[0]

        events["match_id"] = match_id
        events["match_name"] = f"{home} vs {away}"
        events["home_team"] = home
        events["away_team"] = away

        # === Validate and Save ===
        required = ["x", "y", "end_x", "end_y"]
        missing = [col for col in required if col not in events.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        events.to_csv(csv_path, index=False)
        return True

    except Exception as e:
        os.makedirs(ERRORS_DIR, exist_ok=True)
        with open(ERROR_LOG_PATH, "a", encoding="utf-8") as log:
            log.write(f"[{datetime.now().isoformat()}] ERROR in {json_path}: {str(e)}\n")
        print(f"ERROR in {json_path}: {e}")
        return False


def main():
    print("Starting flattening...")
    os.makedirs(FLATTENED_DIR, exist_ok=True)

    matches_df = pd.read_csv(MATCH_META_PATH)
    raw_files = glob.glob(os.path.join(RAW_DIR, "*.json"))

    flattened = 0
    for json_path in raw_files:
        match_id = os.path.basename(json_path).split("_")[0]
        csv_name = os.path.basename(json_path).replace(".json", ".csv")
        csv_path = os.path.join(FLATTENED_DIR, csv_name)

        if os.path.exists(csv_path):
            print(f"Exists: {csv_name}")
            continue

        ok = flatten_match(json_path, csv_path, matches_df)
        if ok:
            flattened += 1

    print(f"Flattened {flattened} new matches.")

    # Combine all CSVs
    csv_files = glob.glob(os.path.join(FLATTENED_DIR, "*.csv"))
    if not csv_files:
        print("No flattened files found.")
        return

    combined_df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
    combined_df.to_csv(COMBINED_CSV_PATH, index=False)
    print(f"Combined CSV written to: {COMBINED_CSV_PATH}")


if __name__ == "__main__":
    main()
