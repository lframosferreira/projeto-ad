#!/bin/bash

if [ ! -d "data/" ]; then
    mkdir data
fi

if [ ! -d "data/wyscout" ]; then
    mkdir data/wyscout
fi

mkdir \
    data/wyscout/competitions \
    data/wyscout/events \
    data/wyscout/matches \
    data/wyscout/playeranks \
    data/wyscout/teams \
    data/wyscout/players \
    data/wyscout/referees \
    data/wyscout/coaches \
    data/wyscout/tagId2name \
    data/wyscout/eventId2name \
    data/wyscout/minutes_played

# downloads the datasets stored in https://figshare.com/collections/Soccer_match_event_dataset/4415000/5
# already unzip content and rename the files to be more readable
wget -P data/wyscout/competitions https://figshare.com/ndownloader/files/15073685
mv data/wyscout/competitions/15073685 data/wyscout/competitions/competitions.json

wget -P data/wyscout/events https://figshare.com/ndownloader/files/14464685
unzip data/wyscout/events/14464685 -d data/wyscout/events/
rm data/wyscout/events/14464685

wget -P data/wyscout/matches https://figshare.com/ndownloader/files/14464622
unzip data/wyscout/matches/14464622 -d data/wyscout/matches/
rm data/wyscout/matches/14464622

wget -P data/wyscout/playeranks https://figshare.com/ndownloader/files/16972010
mv data/wyscout/playeranks/16972010 data/wyscout/playeranks/playeranks.json

wget -P data/wyscout/players https://figshare.com/ndownloader/files/15073721
mv data/wyscout/players/15073721 data/wyscout/players/players.json

wget -P data/wyscout/teams https://figshare.com/ndownloader/files/15073697
mv data/wyscout/teams/15073697 data/wyscout/teams/teams.json

wget -P data/wyscout/referees https://figshare.com/ndownloader/files/15074030
mv data/wyscout/referees/15074030 data/wyscout/referees/referees.json

wget -P data/wyscout/coaches https://figshare.com/ndownloader/files/15073868
mv data/wyscout/coaches/15073868 data/wyscout/coaches/coaches.json

wget -P data/wyscout/tagId2name https://figshare.com/ndownloader/files/21385239
mv data/wyscout/tagId2name/21385239 data/wyscout/tagId2name/tagId2name.csv

wget -P data/wyscout/eventId2name https://figshare.com/ndownloader/files/21385245
mv data/wyscout/eventId2name/21385245 data/wyscout/eventId2name/eventId2name.csv

# link for minutes per game data: https://github.com/soccermatics/Soccermatics/tree/main/course/lessons/minutes_played

wget -P data/wyscout/minutes_played/ https://raw.githubusercontent.com/soccermatics/Soccermatics/main/course/lessons/minutes_played/minutes_played_per_game_England.json
wget -P data/wyscout/minutes_played/ https://raw.githubusercontent.com/soccermatics/Soccermatics/main/course/lessons/minutes_played/minutes_played_per_game_Spain.json
wget -P data/wyscout/minutes_played/ https://raw.githubusercontent.com/soccermatics/Soccermatics/main/course/lessons/minutes_played/minutes_played_per_game_France.json
wget -P data/wyscout/minutes_played/ https://raw.githubusercontent.com/soccermatics/Soccermatics/main/course/lessons/minutes_played/minutes_played_per_game_Germany.json
wget -P data/wyscout/minutes_played/ https://raw.githubusercontent.com/soccermatics/Soccermatics/main/course/lessons/minutes_played/minutes_played_per_game_Italy.json
