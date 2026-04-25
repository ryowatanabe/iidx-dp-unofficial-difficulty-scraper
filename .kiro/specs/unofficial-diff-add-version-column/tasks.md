# Implementation Plan

- [x] 1. UnofficialDifficulty アイテムに version フィールドを追加する
  - `difficulty_scraper/version_map.py` が存在し `VERSION_MAP` がインポート可能であることを確認する（前提条件: 作成済み）
  - `items.py` の `UnofficialDifficulty` クラスに `version = scrapy.Field()` を追加する
  - 完了条件: `UnofficialDifficulty` アイテムに `version` フィールドが定義されている
  - _Requirements: 1.2_

- [x] 2. Spider と Pipeline でバージョン取得・保存を実装する
- [x] 2.1 (P) parsePost() をバージョン略称の抽出と VERSION_MAP マッピングに対応させる
  - `difficulty_scraper/version_map` から `VERSION_MAP` をインポートする
  - `row.css('.rank_p2_inner a.music')` のイテレーションを `row.css('.rank_p2_inner tr')` に変更し、外側ループでバージョンを取得してから内側ループで楽曲を処理する
  - 各内側行の `th::text` からバージョン略称を取得し、`VERSION_MAP.get(version_str.strip()) if version_str else None` でマッピングする
  - 取得した `version` を `UnofficialDifficulty` アイテムに設定して yield する
  - 完了条件: `scrapy crawl unofficial_diff` を実行したとき、各アイテムに `VERSION_MAP` の値と一致する `version`（または変換表に未登録のキーに対する `None`）が設定されること
  - _Requirements: 1.1, 1.2, 1.3, 3.1, 3.2_
  - _Boundary: UnofficialDiffSpider_

- [x] 2.2 (P) unofficial_difficulty テーブルに version カラムを追加し、既存 DB マイグレーションを実装する
  - `get_database()` の `CREATE TABLE IF NOT EXISTS unofficial_difficulty` 定義末尾に `version REAL` を追加する（新規 DB 用）
  - `CREATE TABLE IF NOT EXISTS` の直後に `ALTER TABLE unofficial_difficulty ADD COLUMN version REAL` を実行し、`sqlite3.OperationalError` を `pass` で catch してべき等に動作させる
  - `save_unofficial_difficulty()` の `REPLACE INTO` カラムリストとパラメータタプルに `version` を追加する
  - 完了条件: 新規 DB を作成した場合は `CREATE TABLE` に `version REAL` が含まれ、既存 DB に対して実行した場合は `OperationalError` を発生させずに完了し `PRAGMA table_info(unofficial_difficulty)` で `version` カラムが存在すること
  - _Requirements: 1.1, 4.1, 4.2_
  - _Boundary: DifficultyScraperPipeline_

- [x] 3. 動作を検証する
- [x] 3.1 VERSION_MAP の変換ロジックをユニットテストで検証する
  - 登録済みキー（例: `"GOLD"`）が正しい `float` 値を返すことをアサートする
  - 未登録キー（例: `"UNKNOWN"`）が `None` を返すことをアサートする
  - `version_str = None` のとき `version = None` となるガードロジックを確認する
  - `version_str = ""`（空文字列）のとき `version = None` となることを確認する
  - 完了条件: テスト実行で全アサーションが PASS すること
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 3.2 統合テストとマイグレーションテストで全体動作を検証する
  - `scrapy crawl unofficial_diff` を実行し、`unofficial_difficulty` テーブルに `version IS NOT NULL` のレコードが存在することを確認する（バージョン登録済み楽曲）
  - `version IS NULL` のレコードも正常に保存されていることを確認する（バージョン未登録または変換表未登録の楽曲）
  - `export_csv.py` を実行し、`unofficial_difficulty.csv` に `version` 列が含まれ `float` 値（または空）が出力されることを確認する
  - `version` カラムのない既存 DB を用意して `scrapy crawl unofficial_diff` を実行し、エラーなく完了して `version` カラムが追加されていることを確認する
  - 完了条件: 上記すべての確認が PASS すること
  - _Requirements: 1.1, 1.3, 2.1, 2.2, 4.1, 4.2_
