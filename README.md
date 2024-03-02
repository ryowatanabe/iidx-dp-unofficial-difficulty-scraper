# overview

for beatmania IIDX DP players : 

this tool retrieves  unofficial difficulty from below 2 sites

- [ereter.net](http://ereter.net/)
- [IIDX DP unofficial difficulty](https://zasa.sakura.ne.jp/dp/rank.php)

# requirements 

- python 3.12+
- poetry

# setup

> poetry install

# usage

> poetry shell
> 
> \# retrieve latest data and merge them into local database  
> scrapy crawl ereternet  
> scrapy crawl unofficial_diff
> 
> \# export into csv  
> ./export_csv.sh
