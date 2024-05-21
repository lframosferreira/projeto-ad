#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


# constants

PATH: str = "data/spadl_format/"
RANDOM_STATE: int = 42


# In[3]:


df: pd.DataFrame = pd.read_csv(f"{PATH}England.csv", index_col=0)
df.head(10)


# In[4]:


df = pd.DataFrame()

for country in ["England", "Spain", "Italy", "France", "Germany"]:
    c_df = pd.read_csv(f"{PATH}{country}.csv", index_col=0)
    df = pd.concat([df, c_df])

df.head()


# In[5]:


sorted_df = (
    df.groupby(["game_id", "period_id"])
    .apply(lambda x: x.sort_values(by="time_seconds"))
    .reset_index(drop=True)
)


# In[6]:


type_id_list = (
    sorted_df.groupby(["game_id", "period_id"])["type_id"].apply(list).reset_index(name="type_id_list")
)
type_id_list


# In[7]:


# sequencias de jogadas de todos os jogos
# a ideia é filtrar depois para sequencias que precedem um gol
sequences = type_id_list["type_id_list"].to_list()
sequences = [sequences]


# In[9]:


from sequence_mining.spam import SpamAlgo

algo = SpamAlgo(0.7)
algo.spam(sequences)
# print mined sequences

with open("saida1.txt", "w") as f:
    f.write(algo.frequent_items)


# In[10]:


grouped = sorted_df.groupby(["game_id", "period_id"])

result_list = []

# Iterate over each group
for (game_id, period_id), group in grouped:
    # Sort the group by time_seconds
    group = group.sort_values(by="time_seconds")

    # Find rows where type_name is 'shot' and result_name is 'success'
    success_shots = group[
        (group["type_name"] == "shot") & (group["result_name"] == "success")
    ]

    for idx, success_row in success_shots.iterrows():
        # Find rows of the same team before the successful shot
        team_id = success_row["team_id"]
        time_seconds = success_row["time_seconds"]

        prior_events = group[group["time_seconds"] <= time_seconds][::-1]

        type_ids = []
        for _, event in prior_events.iterrows():
            if event["team_id"] != team_id:
                break
            type_ids.append(
                event["type_id"]
            )  # Filter rows of the same team before the successful shot
        prior_events = group[
            (group["team_id"] == team_id) & (group["time_seconds"] < time_seconds)
        ]

        # Extract the type_ids
        type_ids = prior_events["type_id"].tolist()
        result_list.append(type_ids)


# In[11]:


algo = SpamAlgo(0.7)
algo.spam([result_list])
# print mined sequences

with open("saida2.txt", "w") as f:
    f.write(algo.frequent_items)

