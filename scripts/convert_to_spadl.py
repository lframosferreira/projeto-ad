#!/usr/bin/env python
# coding: utf-8

# In[8]:


import numpy as np
import pandas as pd
import socceraction.spadl as spd
from tqdm import tqdm
import os


# # Carregando os dados da WyScout

# In[9]:


def load_matches(path):
    matches = pd.read_json(path_or_buf=path)
    # as informações dos times de cada partida estão em um dicionário dentro da coluna 'teamsData', então vamos separar essas informações
    team_matches = []
    for i in range(len(matches)):
        match = pd.DataFrame(matches.loc[i, "teamsData"]).T
        match["matchId"] = matches.loc[i, "wyId"]
        team_matches.append(match)
    team_matches = pd.concat(team_matches).reset_index(drop=True)

    return team_matches


# In[10]:


def load_players(path):
    players = pd.read_json(path_or_buf=path)
    players["player_name"] = players["firstName"] + ' ' + players["lastName"]
    players = players[["wyId", "player_name"]].rename(columns={"wyId": "player_id"})

    return players


# In[11]:


def load_events(path):
    events = pd.read_json(path_or_buf=path)
    # pré processamento em colunas da tabela de eventos para facilitar a conversão p/ SPADL
    events = events.rename(columns={
        "id": "event_id",
        "eventId": "type_id",
        "subEventId": "subtype_id",
        "teamId": "team_id",
        "playerId": "player_id",
        "matchId": "game_id"
    })
    events["milliseconds"] = events["eventSec"] * 1000
    events["period_id"] = events["matchPeriod"].replace({"1H": 1, "2H": 2})

    return events


# In[12]:


def load_minutes_played_per_game(path):
    minutes = pd.read_json(path_or_buf=path)
    minutes = minutes.rename(columns={
        "playerId": "player_id",
        "matchId": "game_id",
        "teamId": "team_id",
        "minutesPlayed": "minutes_played"
    })
    minutes = minutes.drop(["shortName", "teamName", "red_card"], axis=1)

    return minutes


# In[13]:


leagues = ["England", "Spain", "France", "Germany", "Italy"]
events = {}
matches = {}
minutes = {}
for league in leagues:
    path = f"data/wyscout/matches/matches_{league}.json"
    matches[league] = load_matches(path)
    path = f"data/wyscout/events/events_{league}.json"
    events[league] = load_events(path)
    path = f"data/wyscout/minutes_played/minutes_played_per_game_{league}.json"
    minutes[league] = load_minutes_played_per_game(path)


# In[14]:


path = "data/wyscout/players/players.json"
players = load_players(path)
players["player_name"] = players["player_name"].str.decode("unicode-escape")


# # Conversão para o formato SPADL

# In[15]:


def spadl_transform(events, matches):
    spadl = []
    game_ids = events.game_id.unique().tolist()
    for g in tqdm(game_ids):
        match_events = events.loc[events.game_id == g]
        match_home_id = matches.loc[(matches.matchId == g) & (matches.side == "home"), "teamId"].values[0]
        match_actions = spd.wyscout.convert_to_actions(events=match_events, home_team_id=match_home_id)
        match_actions = spd.play_left_to_right(actions=match_actions, home_team_id=match_home_id)
        match_actions = spd.add_names(match_actions)
        spadl.append(match_actions)
    spadl = pd.concat(spadl).reset_index(drop=True)

    return spadl


# In[16]:


if not os.path.exists("data/spadl_format"):
    os.makedirs("data/spadl_format")
players: pd.DataFrame = pd.read_json("data/wyscout/players/players.json")
players["player_name"] = players["shortName"].str.decode("unicode-escape")
players = players[["wyId", "player_name"]].rename(columns={"wyId": "player_id"})

for league in leagues:
    df = spadl_transform(events=events[league], matches=matches[league])
    df = df.merge(players, on="player_id", how="left")
    df.to_csv(f"data/spadl_format/{league}.csv") 
    

