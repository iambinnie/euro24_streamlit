import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt

# === Load Combined Event Data ===
@st.cache_data
def load_data():
    path = "data/euro24_all_events_combined.csv"
    df = pd.read_csv(path, low_memory=False)
    return df

df = load_data()

st.title("⚽ Euro 2024 Event Viewer")
st.markdown("Explore StatsBomb event data by match, team, player, and event type.")

# === Sidebar Filters ===
match = st.selectbox("Select Match", sorted(df['match_name'].dropna().unique()), index=0)
filtered_df = df[df['match_name'] == match]

team = st.selectbox("Select Team", sorted(filtered_df['team'].dropna().unique()), index=0)
filtered_df = filtered_df[filtered_df['team'] == team]

player = st.selectbox("Select Player", sorted(filtered_df['player'].dropna().unique()), index=0)
filtered_df = filtered_df[filtered_df['player'] == player]

etype = st.selectbox("Select Event Type", sorted(filtered_df['type'].dropna().unique()), index=0)
filtered_df = filtered_df[filtered_df['type'] == etype]

# === Display Filtered Table ===
st.markdown("### 📋 Filtered Events")
columns_to_show = ['minute', 'second', 'type', 'player', 'team']
for optional in ['location', 'x', 'y', 'end_x', 'end_y', 'pass.outcome.name', 'outcome.name', 'shot.statsbomb_xg']:
    if optional in filtered_df.columns:
        columns_to_show.append(optional)

st.dataframe(filtered_df[columns_to_show].head(20))

st.write("Checking coordinates:")
st.write(filtered_df[['x', 'y', 'end_x', 'end_y']].dropna().head())

# === Timeline: Event Frequency Over Time ===
st.markdown("### ⏱ Event Timeline Chart")
if not filtered_df.empty:
    minute_counts = filtered_df['minute'].value_counts().sort_index()
    fig_time, ax_time = plt.subplots(figsize=(8, 2.5))
    ax_time.bar(minute_counts.index, minute_counts.values, color='skyblue')
    ax_time.set_xlabel("Minute")
    ax_time.set_ylabel("Number of Events")
    ax_time.set_title(f"Event Frequency by Minute: {etype}")
    st.pyplot(fig_time)
else:
    st.warning("No events to show for this selection.")

# === Pitch Plot ===
st.markdown("### 🗺️ Event Location Plot")

if {'x', 'y'}.issubset(filtered_df.columns) and not filtered_df[['x', 'y']].isna().all().all():
    pitch = VerticalPitch(pitch_type='statsbomb')
    fig, ax = pitch.draw(figsize=(9, 6))

    if etype in ['Pass', 'Carry'] and {'end_x', 'end_y'}.issubset(filtered_df.columns):
        for _, row in filtered_df.iterrows():
            if pd.notna(row['x']) and pd.notna(row['y']) and pd.notna(row['end_x']) and pd.notna(row['end_y']):
                if 'pass.outcome.name' in row and pd.notna(row['pass.outcome.name']):
                    color = 'red'  # incomplete
                else:
                    color = 'green'  # completed

                pitch.arrows(
                    row['x'], row['y'], row['end_x'], row['end_y'],
                    ax=ax, width=1.5, headwidth=6,
                    color=color, alpha=0.8, zorder=2
                )
        st.caption("🟩 Green = completed | 🟥 Red = incomplete passes/carries")
    else:
        # Just show dots
        pitch.scatter(
            x=filtered_df['x'],
            y=filtered_df['y'],
            ax=ax,
            s=100,
            color='red',
            edgecolors='black'
        )
        st.caption("🔴 Showing event locations as points (no end location available).")

    # Optional player names
    for _, row in filtered_df.head(10).iterrows():
        if pd.notna(row['x']) and pd.notna(row['y']):
            ax.text(row['x'], row['y'], row['player'], fontsize=7, ha='center', color='white')

    st.pyplot(fig)
else:
    st.warning("No valid location data available for plotting.")
