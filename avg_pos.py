import pandas as pd
import json
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# === LOAD DATA ===
df = pd.read_csv('data_euro24_statsbomb.csv')
df['location'] = df['location'].apply(json.loads)

# Filter just to Scotland team to find matches
scotland_df = df[df['team'] == 'Scotland'].copy()

# Get all match IDs where Scotland played
match_ids = scotland_df['match_id'].unique()

# === ACTION TYPES WE WANT TO ANALYZE ===
relevant_types = ['Pass', 'Carry', 'Pressure', 'Ball Receipt*']

for match_id in match_ids:
    match_df = df[(df['match_id'] == match_id) &
                  (df['team'] == 'Scotland') &
                  (df['type'].isin(relevant_types))]

    # If not enough events, skip
    if match_df.empty:
        print(f"⚠️ No relevant actions for Scotland in match {match_id}. Skipping.")
        continue

    # === IDENTIFY STARTING XI ===
    player_counts = match_df['player'].value_counts().head(11)
    starting_players = player_counts.index.tolist()

    if len(starting_players) < 11:
        print(f"⚠️ Only found {len(starting_players)} players for match {match_id}")
        continue

    starting_df = match_df[match_df['player'].isin(starting_players)]

    avg_positions = (
        starting_df.groupby('player')['location']
        .apply(lambda locs: pd.DataFrame(locs.tolist()).mean())
        .reset_index()
    )
    avg_positions.columns = ['player', 'x', 'y']

    # === PLOT ===
    pitch = VerticalPitch(pitch_type='statsbomb')
    fig, ax = pitch.draw(figsize=(10, 7))

    pitch.scatter(
        x=avg_positions['x'],
        y=avg_positions['y'],
        ax=ax,
        color='blue',
        s=300,
        edgecolors='black',
        zorder=3
    )

    for _, row in avg_positions.iterrows():
        ax.text(row['x'], row['y'], row['player'], color='white',
                fontsize=8, ha='center', va='center')

    plt.title(f'Scotland Starting XI – Match {match_id}', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'scotland_avg_positions_match_{match_id}.png', dpi=300)
    plt.close()

print("✅ All Scotland average position maps generated.")
