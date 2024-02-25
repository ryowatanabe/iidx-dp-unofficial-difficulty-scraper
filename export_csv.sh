#! /bin/sh

sqlite3 -header -csv ./data/data.db "select * from ereternet_difficulty" > ./data/ereternet_difficulty.csv
sqlite3 -header -csv ./data/data.db "select * from unofficial_difficulty" > ./data/unofficial_difficulty.csv