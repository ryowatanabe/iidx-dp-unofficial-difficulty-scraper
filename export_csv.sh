#! /bin/sh

sqlite3 -header -csv ./data/data.db "select * from unofficial_difficulty order by song_id" > ./data/unofficial_difficulty.csv
sqlite3 -header -csv ./data/data.db "select * from ereternet_difficulty order by song_id" > ./data/ereternet_difficulty.csv
sqlite3 -header -csv ./data/data.db "select name, difficulty, unofficial_diff, ec_diff, hc_diff, exh_diff from ereternet_difficulty order by song_id" > ./data/ereternet_difficulty_diffonly.csv
