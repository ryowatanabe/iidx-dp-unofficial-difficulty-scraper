# overview

for beatmania IIDX DP players : 

this tool retrieves  unofficial difficulty from below 2 sites

- [ereter.net](http://ereter.net/)
- [IIDX DP unofficial difficulty](https://zasa.sakura.ne.jp/dp/rank.php)

# requirements 

- python 3.13+

# setup

## setup venv

```
python -m venv venv
venv\Scripts\Activate
```

## install dependencies

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

# usage

```
# retrieve latest data and merge them into local database  
scrapy crawl ereternet  
scrapy crawl unofficial_diff

# export into csv  
./export_csv.py
```