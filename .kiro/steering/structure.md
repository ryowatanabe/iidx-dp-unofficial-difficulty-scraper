# Project Structure

## Organization Philosophy

Scrapy の規約に従ったフラットなレイヤー構成。スパイダー・アイテム定義・パイプライン・設定が `difficulty_scraper/` パッケージに集約され、データとエクスポートスクリプトはルートに配置される。

## Directory Patterns

### Scrapy プロジェクトパッケージ
**Location**: `difficulty_scraper/`  
**Purpose**: Scrapy の全コンポーネント（Spider・Item・Pipeline・Settings）  
**Example**: `difficulty_scraper/spiders/ereternet.py`（Spider定義）

### スパイダー
**Location**: `difficulty_scraper/spiders/`  
**Purpose**: 各データソースに対応する Spider クラス（1スパイダー = 1外部サイト）  
**Pattern**: スパイダー名はドメイン/サービス名をスネークケースで命名（`ereternet`, `unofficial_diff`）

### データストレージ
**Location**: `data/`  
**Purpose**: SQLite DB とエクスポートCSVファイルの出力先  
**Example**: `data/data.db`（SQLite）、`data/unofficial_difficulty.csv`

### エクスポートスクリプト
**Location**: プロジェクトルート  
**Purpose**: SQLite → CSV 変換の単発スクリプト  
**Example**: `export_csv.py`

## Naming Conventions

- **Spiders**: スネークケース（`ereternet.py`, `unofficial_diff.py`）
- **Item classes**: PascalCase + 意味的サフィックス（`EreterNetDifficulty`, `UnofficialDifficulty`）
- **Pipeline class**: `{ProjectName}Pipeline` の単一クラス（`DifficultyScraperPipeline`）
- **DB tables**: スネークケース、Spider 名と対応（`ereternet_difficulty`, `unofficial_difficulty`）

## Import Organization

```python
# 標準ライブラリ
import os, re, sqlite3

# サードパーティ (Scrapy)
import scrapy
from itemadapter import ItemAdapter

# プロジェクト内
from difficulty_scraper.items import EreterNetDifficulty
```

## Code Organization Principles

- **1スパイダー = 1データソース**: 各スパイダーは単一の外部サイトのみを担当
- **Pipeline でアイテム振り分け**: アイテム型判定ロジックは Pipeline に集中させ、Scrapy 設定はシンプルに保つ
- **ステートレスなスパイダー**: スパイダーはデータ収集のみ、永続化は Pipeline の責務
- **データはルートの `data/` に集約**: DB・CSVともに同一ディレクトリ、パス管理をシンプルに

---
_Document patterns, not file trees. New files following patterns shouldn't require updates_
