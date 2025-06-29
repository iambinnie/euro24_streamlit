"""
Flatten raw StatsBomb Euro‑24 JSON event files into per‑match CSVs,
inject match metadata, validate required coordinates, and combine into
a master CSV if all pass validation.

- Reads raw files from RAW_DIR
- Writes per-match CSVs to FLATTENED_DIR
- Writes combined CSV to BASE_DATA_DIR/euro24_all_events_combined.csv
- Logs validation results to ERRORS_DIR/flatten_report.txt
"""

import os
import glob
import json
from datetime import datetime

import pandas as pd

from config.constants import (
    RAW_DIR,
    FLATTENED_DIR,
    BASE_DATA_DIR,
    MATCH_META_PATH,
    ERRORS_DIR,
)

COMBINED_CSV = os.path.join(BASE_DATA_DIR, "euro24_all_events_combined.csv")
REPORT_PATH = os.path.join(ERRORS_DIR, "flatten_report.txt")


def extract_coord(val, idx):
    """Safely return coordinate from list or None."""
    return val[idx] if isinstance(val, list) and len(val) > idx else None


def flatten_single(json_path, csv_path, meta_df, report_lines):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f]

        df = pd.json_normalize(records, sep=".")

        # Basic coords
        df["x"] = df["location"].apply(lambda loc: extract_coord(loc, 0))
        df["y"] = df["location"].apply(lambda loc: extract_coord(loc, 1))

        # Use flat keys instead of nested pass.end_location
        df["end_x"] = df["pass_end_location"].apply(lambda loc: extract_coord(loc, 0)) if "pass_end_location" in df else None
        df["end_y"] = df["pass_end_location"].apply(lambda loc: extract_coord(loc, 1)) if "pass_end_location" in df else None

        if "carry_end_location" in df:
            carry_x = df["carry_end_location"].apply(lambda loc: extract_coord(loc, 0))
            carry_y = df["carry_end_location"].apply(lambda loc: extract_coord(loc, 1))
            df["end_x"] = df["end_x"].combine_first(carry_x)
            df["end_y"] = df["end_y"].combine_first(carry_y)

        if "shot.end_location" in df:
            df["shot_end_x"] = df["shot.end_location"].apply(lambda loc: extract_coord(loc, 0))
            df["shot_end_y"] = df["shot.end_location"].apply(lambda loc: extract_coord(loc, 1))

        # Inject metadata
        match_id = int(os.path.basename(json_path).split("_")[0])
        meta_row = meta_df.loc[meta_df["match_id"] == match_id]

        if meta_row.empty:
            report_lines.append(f"[{match_id}]  ERROR  Metadata not found\n")
            return False

        home = meta_row["home_team"].values[0]
        away = meta_row["away_team"].values[0]

        df["match_id"] = match_id
        df["match_name"] = f"{home} vs {away}"
        df["home_team"] = home
        df["away_team"] = away

        # Validate: all Pass/Carry must have end_x/end_y
        pass_carry = df[df["type"].isin(["Pass", "Carry"])]
        missing = pass_carry[pass_carry[["end_x", "end_y"]].isna().any(axis=1)]

        if not missing.empty:
            report_lines.append(f"[{match_id}]  FAIL  {len(missing)} Pass/Carry rows missing end coords\n")
            return False

        df.to_csv(csv_path, index=False)
        report_lines.append(f"[{match_id}]  OK    Flattened {len(df)} rows\n")
        return True

    except Exception as e:
        report_lines.append(f"[ERROR]  {os.path.basename(json_path)}  ::  {e}\n")
        return False


def main():
    os.makedirs(FLATTENED_DIR, exist_ok=True)
    os.makedirs(ERRORS_DIR, exist_ok=True)

    meta_df = pd.read_csv(MATCH_META_PATH)
    raw_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.json")))

    report = [f"Flatten run {datetime.now().isoformat()}\n", "-" * 50 + "\n"]
    ok_count = fail_count = 0

    for raw in raw_files:
        match_id = os.path.basename(raw).split("_")[0]
        csv_path = os.path.join(FLATTENED_DIR, f"{match_id}_events.csv")

        if os.path.exists(csv_path):
            report.append(f"[{match_id}]  SKIP  already exists\n")
            ok_count += 1
            continue

        success = flatten_single(raw, csv_path, meta_df, report)
        if success:
            ok_count += 1
        else:
            fail_count += 1

    # Write flatten report
    report.append("-" * 50 + "\n")
    report.append(f"Success: {ok_count}   Failures: {fail_count}\n")

    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.writelines(report)

    if fail_count:
        print("Flatten completed with failures — see report for details.")
        return

    # Combine all valid CSVs
    all_csvs = glob.glob(os.path.join(FLATTENED_DIR, "*.csv"))
    combined_df = pd.concat([pd.read_csv(p) for p in all_csvs], ignore_index=True)
    combined_df.to_csv(COMBINED_CSV, index=False)
    print(f"Combined CSV written to: {COMBINED_CSV}")


if __name__ == "__main__":
    main()
