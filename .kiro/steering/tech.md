# Technology Stack

## Architecture

Scrapy フレームワークをベースとしたバッチスクレイピングパイプライン。Spider がデータを収集し、共通 Pipeline がアイテム種別を判別して SQLite に保存する単方向フロー。

## Core Technologies

- **Language**: Python 3.13+
- **Framework**: Scrapy 2.14
- **Storage**: SQLite（`sqlite3` 標準ライブラリ、外部インストール不要）
- **Runtime**: venv（`requirements.txt` で依存管理）

## Key Libraries

- **Scrapy**: スパイダー・パイプライン・スケジューリングの全体フレームワーク
- **lxml / parsel / cssselect**: HTML パース・CSS セレクタ
- **itemadapter**: パイプライン内のアイテム型統一インターフェース
- **Twisted + asyncio**: 非同期I/O（`AsyncioSelectorReactor` 使用）

## Development Standards

### スクレイピング設定
- `CONCURRENT_REQUESTS = 1`、`DOWNLOAD_DELAY = 5`（サーバー負荷軽減のため直列・遅延必須）
- `ROBOTSTXT_OBEY = False`（対象サイトがrobots.txtを持たないため）
- BFO順（FIFO キュー）で深さ優先ではなく幅優先クロール

### データ整合性
- `REPLACE INTO` による upsert でべき等な更新を保証
- テーブル作成は `CREATE TABLE IF NOT EXISTS`（初回実行・再実行で安全）

### コード品質
- アイテム型は `type(item).__name__` で判別（isinstance ではなく文字列比較）
- CSS セレクタで HTML をパース、re でテキスト後処理

## Development Environment

### Required Tools
- Python 3.13+
- venv（標準ライブラリ）

### Common Commands
```bash
# 環境セットアップ
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# データ収集
scrapy crawl ereternet
scrapy crawl unofficial_diff

# CSV エクスポート
./export_csv.py
```

## Key Technical Decisions

- **SQLite を直接使用**: 外部DBサーバー不要でデプロイを単純化（`data/data.db` 1ファイル）
- **Poetry 廃止**: `requirements.txt` + venv に戻すことで、SQLite3 デバイスインストール不要化
- **単一 Pipeline クラス**: アイテム種別を Pipeline 内で振り分けることで、Scrapy 設定を最小化

---
_Document standards and patterns, not every dependency_
