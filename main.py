import json

import streamlit as st
import pandas as pd

from mplsoccer import VerticalPitch


st.title("Euros 2024 Shot Map")
st.subheader("Filter to any team then player to see all of their shots taken!")

df = pd.read_csv('data_euro24_statsbomb.csv')
df = df[df['type'] == 'Shot'].reset_index(drop=True)
df['location'] = df['location'].apply(json.loads)

team = st.selectbox('Select a team', df['team'].sort_values().unique(), index=None)
player = st.selectbox('Select a player', df[df['team'] == team]['player'].sort_values().unique(), index=None)

def filter_data(df, team, player):
    if team:
        df = df[df['team'] == team]
    if player:
        df = df[df['player'] == player]
    
    return df

filtered_df = filter_data(df, team, player)


pitch = VerticalPitch(pitch_type='statsbomb', half=True)
fig, ax = pitch.draw(figsize=(10, 10))

def plot_shots(df, ax, pitch):
    for x in df.to_dict(orient='records'):
        # Determine color based on shot_outcome
        if x['shot_outcome'] == 'Goal':
            color = 'green'
        elif x['shot_outcome'] == 'Off T':
            color = 'red'
        elif x['shot_outcome'] == 'Blocked':
            color = 'blue'
        elif x['shot_outcome'] == 'Saved
            color = 'black'
        else:
            color = 'white'

        pitch.scatter(
            x=float(x['location'][0]),
            y=float(x['location'][1]),
            ax=ax,
            s=1000 * x['shot_statsbomb_xg'],
            color=color,
            edgecolors='black',
            alpha=1 if x['shot_outcome'] == 'Goal' else 0.5,
            zorder=2 if x['shot_outcome'] == 'Goal' else 1
        )


plot_shots(filtered_df, ax, pitch)

st.pyplot(fig)
