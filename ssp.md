```python
import pandas as pd
import os
import numpy as np
from math import sqrt
```

```python
pd.set_option("display.width", 220)
```

```python
PATH_ROOT = "./data"
PATH_SPADL = f"{PATH_ROOT}/spadl_format"
PATH_WYSCOUT = f"{PATH_ROOT}/wyscout"
PATH_PROCESSED = f"{PATH_ROOT}/processed"
```

```python
LEAGUES: list[str] = ["England", "Spain", "France", "Italy", "Germany"]
```

```python
teams_df = pd.read_json(f"{PATH_WYSCOUT}/teams/teams.json")
players_df = pd.read_json(f"{PATH_WYSCOUT}/players/players.json")
ranking_df = pd.read_json(f"{PATH_WYSCOUT}/playeranks/playeranks.json")
```

```python
df_dict = {}
if not os.path.exists(PATH_PROCESSED):
    os.mkdir(PATH_PROCESSED)
for league in LEAGUES:
    df = pd.read_csv(f"{PATH_SPADL}/{league}.csv", index_col=0)

    # remove not used columns
    df.drop(
        ["original_event_id", "result_name", "bodypart_id", "type_id"],
        inplace=True,
        axis=1,
    )

    df_dict[league] = df
all_df = pd.concat([df for df in df_dict.values()])
all_df
```

```python
print(all_df["type_name"].unique())
```

### Pre-Process

```python
GOAL_CENTER_X: int = 105
GOAL_CENTER_Y: int = 34

UPPER_CROSSBAR_X: int = 105
UPPER_CROSSBAR_Y: int = 38

LOWER_CROSSBAR_X: int = 105
LOWER_CROSSBAR_Y: int = 30
```

```python
def get_shot_angle(shot_pos_x: float, shot_pos_y: float) -> float:
    v1 = np.array([UPPER_CROSSBAR_X - shot_pos_x, UPPER_CROSSBAR_Y - shot_pos_y])
    v2 = np.array([LOWER_CROSSBAR_X - shot_pos_x, LOWER_CROSSBAR_Y - shot_pos_y])
    return np.arccos(np.dot(v1 / np.linalg.norm(v1), v2 / np.linalg.norm(v2)))
```

```python
def get_shot_distance(shot_pos_x: float, shot_pos_y: float) -> float:
    return sqrt((shot_pos_x - GOAL_CENTER_X) ** 2 + (shot_pos_y - GOAL_CENTER_Y) ** 2)
```

```python
actions = [
    "pass",  # 0
    "interception",  # 1
    "dribble",  # 2
    "take_on",  # 3
    "tackle",  # 4
    "foul",  # 5
    "freekick_short",  # 6
    "cross",  # 7
    "shot",  # 8
    "clearance",  # 9
    "throw_in",  # 10
    "goalkick",  # 11
    "corner_short",  # 12
    "corner_crossed",  # 13
    "keeper_save",  # 14
    "freekick_crossed",  # 15
    "shot_freekick",  # 16
    "bad_touch",  # 17
    "shot_penalty",  # 18
]
```

```python
def map_action_to_number(action: str) -> str:
    return str(actions.index(action))
```

```python
def generate_shots_with_counts_events(df: pd.DataFrame):
    shot_data = []
    result_ids = []
    grouped = df.groupby(["game_id", "period_id"])

    for (_, _), group in grouped:
        group = group.sort_values(by="time_seconds").reset_index(drop=True)
        i = 0

        while i < len(group):
            shot_indices = group[i:].index[group["type_name"][i:] == "shot"]
            if len(shot_indices) == 0:
                break
            shot_index = shot_indices[0]

            shot_row = group.loc[shot_index]
            play_events = group.loc[i:shot_index]

            # Encontrar o índice onde o time que fez o chute tomou posse da bola
            for j in play_events.index[::-1]:
                if play_events.loc[j, "team_id"] != shot_row["team_id"]:
                    i = j + 1
                    break
            else:
                i = play_events.index[0]

            play_events = group.loc[i:shot_index]

            shot_data.append(
                {
                    "actions": " ".join(
                        list(
                            map(
                                lambda x: map_action_to_number(x),
                                play_events["type_name"].to_list()[
                                    :-1  # remove the actual shot
                                ],
                            )
                        )
                    ),
                    "start_x": round(shot_row["start_x"], 2),
                    "start_y": round(shot_row["start_y"], 2),
                    "end_x": round(shot_row["end_x"], 2),
                    "end_y": round(shot_row["end_y"], 2),
                    "bodypart_name": shot_row["bodypart_name"],
                }
            )

            result_ids.append(shot_row["result_id"])

            # Atualizar o índice de início para a próxima jogada
            i = shot_index + 1

    shots_df = pd.DataFrame(shot_data)
    shots_df["shot_distance_from_goal"] = shots_df.apply(
        lambda pos: get_shot_distance(pos["start_x"], pos["start_y"]), axis=1
    )
    shots_df["shot_angle_from_goal"] = shots_df[["start_x", "start_y"]].apply(
        lambda pos: get_shot_angle(pos["start_x"], pos["start_y"]), axis=1
    )
    shots_df["result_id"] = result_ids
    return shots_df
```

```python
shots_df = generate_shots_with_counts_events(all_df)
```

```python
shots_df.head()
```

## XG

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
```

```python
RANDOM_STATE = 123
TEST_SIZE = 0.3
```

```python
shots_df_cp = shots_df.copy()
```

```python
rfc = RandomForestClassifier(random_state=RANDOM_STATE)
X = shots_df_cp[["bodypart_name", "shot_distance_from_goal", "shot_angle_from_goal"]]
X["bodypart_name"] = X["bodypart_name"].apply(
    lambda val: 0 if val == "foot_right" else 1 if val == "foot_left" else 2
)
y = shots_df_cp["result_id"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)
rfc.fit(X=X_train, y=y_train)
y_pred = rfc.predict(X=X_test)
classification_report(y_test, y_pred, output_dict=True)
```

```python
shots_df_cp["xg"] = rfc.predict(X=X)
```

```python
ssp_cols_df = pd.DataFrame()
ssp_cols_df["xg"] = shots_df_cp["xg"].map(lambda x: str(x) if x == 1 else "-1")
ssp_cols_df["actions"] = shots_df_cp["actions"]
ssp_cols_df.head()
```

```python
input_df = pd.DataFrame()
input_df["input"] = ssp_cols_df["xg"] + " " + ssp_cols_df["actions"]
input_df
```

```python
input_df.to_csv("mining_input_full.txt", header=None, index=False)
```
