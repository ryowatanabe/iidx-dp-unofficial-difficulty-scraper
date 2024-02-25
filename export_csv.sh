#! /bin/sh

sqlite3 -header -csv ./data/data.db "select * from ereternet_difficulty order by song_id" > ./data/ereternet_difficulty.csv
sqlite3 -header -csv ./data/data.db "select * from unofficial_difficulty order by song_id" > ./data/unofficial_difficulty.csv