import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt

# === Load Combined Event Data ===
@st.cache_data
def load_data():
    path = "data/euro24_all_events_combined.csv"
    df = pd.read_csv(path)
    return df

df = load_data()

st.title("⚽ Euro 2024 Event Viewer (StatsBomb Free Data)")
st.markdown("Browse and visualize event data by match, team, player, and event type.")

# === Sidebar Filters ===
match = st.selectbox("Select Match", sorted(df['match_name'].dropna().unique()), index=0)
filtered_df = df[df['match_name'] == match]

team = st.selectbox("Select Team", sorted(filtered_df['team'].dropna().unique()), index=0)
filtered_df = filtered_df[filtered_df['team'] == team]

player = st.selectbox("Select Player", sorted(filtered_df['player'].dropna().unique()), index=0)
filtered_df = filtered_df[filtered_df['player'] == player]

etype = st.selectbox("Select Event Type", sorted(filtered_df['type'].dropna().unique()), index=0)
filtered_df = filtered_df[filtered_df['type'] == etype]

# === Display Available Columns for Reference ===
#st.markdown("### Available Columns")
#st.text(", ".join(filtered_df.columns[:30]) + ("..." if len(filtered_df.columns) > 30 else ""))

# === Display Filtered Event Table ===
st.markdown("### Filtered Events Table")

# Safely select only available columns
columns_to_show = ['minute', 'second', 'type', 'player', 'team']
for optional in ['location', 'x', 'y', 'pass.outcome.name', 'outcome.name', 'shot.statsbomb_xg']:
    if optional in filtered_df.columns:
        columns_to_show.append(optional)

st.dataframe(filtered_df[columns_to_show].head(20))

# === Optional Pitch Plot ===
st.markdown("### Plot Event Locations (if available)")

if 'x' in filtered_df.columns and 'y' in filtered_df.columns and not filtered_df[['x', 'y']].isna().all().all():
    pitch = VerticalPitch(pitch_type='statsbomb')
    fig, ax = pitch.draw(figsize=(9, 6))

    pitch.scatter(
        x=filtered_df['x'],
        y=filtered_df['y'],
        ax=ax,
        s=100,
        color='red',
        edgecolors='black'
    )

    for _, row in filtered_df.head(10).iterrows():
        if pd.notna(row['x']) and pd.notna(row['y']):
            ax.text(row['x'], row['y'], row['player'], fontsize=7, ha='center', color='white')

    st.pyplot(fig)
else:
    st.warning("No valid location data available for plotting.")
