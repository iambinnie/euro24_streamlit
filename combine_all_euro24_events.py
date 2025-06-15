import os
import pandas as pd

# === Paths ===
EVENTS_DIR = "data/events_csv"
OUTPUT_PATH = "data/euro24_all_events_combined.csv"

# === Get all CSV files in the folder ===
csv_files = [f for f in os.listdir(EVENTS_DIR) if f.endswith(".csv")]

# === Load and concatenate ===
all_events = []
for f in csv_files:
    full_path = os.path.join(EVENTS_DIR, f)
    df = pd.read_csv(full_path)

    # Optional: Add match name for context
    match_name = f.replace(".csv", "")
    df['match_name'] = match_name

    all_events.append(df)

# === Combine all into a single DataFrame ===
combined_df = pd.concat(all_events, ignore_index=True)

# === Save ===
combined_df.to_csv(OUTPUT_PATH, index=False)

print(f"✅ Combined {len(csv_files)} event files into {OUTPUT_PATH}")
print(f"📊 Total events: {len(combined_df)}")
