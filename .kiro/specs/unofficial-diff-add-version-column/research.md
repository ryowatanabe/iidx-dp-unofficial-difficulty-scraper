# Research & Design Decisions

## Summary
- **Feature**: `unofficial-diff-add-version-column`
- **Discovery Scope**: Extension（既存 Scrapy パイプラインへのカラム追加）
- **Key Findings**:
  - HTML 上のバージョン略称は `<th>` 要素に格納され、ドロップダウンの表示名と異なる独自略称（例: `RDT` = RESIDENT、`HSKY` = HAPPY SKY）を使用している
  - `export_csv.py` は `SELECT *` を使用するため、テーブルスキーマ拡張のみで CSV への反映が自動化される
  - SQLite の `ALTER TABLE ADD COLUMN IF NOT EXISTS` は非サポートのため、`OperationalError` catch による べき等マイグレーションを採用

## Research Log

### HTML バージョン略称の調査
- **Context**: 難易度表の各楽曲にバージョン情報がどのように記述されているか不明だった
- **Sources Consulted**: Playwright ブラウザで `https://zasa.sakura.ne.jp/dp/rank.php` に POST リクエストを送信し、レスポンス HTML を直接解析
- **Findings**:
  - `.rank_p2_inner tr > th` に各楽曲のバージョン略称が格納される
  - 略称は env ドロップダウンの表示名と異なる（例: `DistorteD` → `DD`、`RESIDENT` → `RDT`）
  - env=a330 (Sparkle Shower) までの全バージョンで 34 種類の略称を確認
- **Implications**: Spider の内側ループを `.rank_p2_inner a.music` から `.rank_p2_inner tr` に変更し、`th::text` でバージョン略称を取得する必要がある

### SQLite マイグレーション方式の検討
- **Context**: 既存 DB（`version` カラムなし）と新規 DB の両方に対応する必要がある
- **Findings**:
  - SQLite は `ALTER TABLE ADD COLUMN IF NOT EXISTS` を非サポート
  - `PRAGMA table_info()` でカラム存在確認も可能だが、コードが複雑になる
- **Implications**: `try/except OperationalError` による catch が最もシンプルかつ既存コードパターンと一貫性がある

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations |
|--------|-------------|-----------|---------------------|
| try/except catch | ALTER TABLE を実行し duplicate column エラーを無視 | シンプル、既存パターンと一貫 | エラーを握りつぶすため他の OperationalError を見逃す可能性 |
| PRAGMA table_info | カラム存在を事前確認 | 明示的 | コードが複雑、毎 item 呼び出しのオーバーヘッド |

**採用**: try/except catch。`OperationalError` はこのコンテキストではカラム重複のみ発生するため許容。

## Design Decisions

### Decision: inner row イテレーションへの変更
- **Context**: バージョン略称は `.rank_p2_inner` の各 `<tr>` の `<th>` に存在する。現在のコードは `a.music` を直接イテレートするため `<th>` にアクセスできない
- **Selected Approach**: `.rank_p2_inner tr` を外側ループとし、`th::text` でバージョン取得後に `a.music` を内側ループ
- **Rationale**: HTML 構造に忠実で、既存の CSS セレクタパターンと一貫している
- **Trade-offs**: コードの入れ子が1段増えるが、ロジックは単純なまま

### Decision: VERSION_MAP の配置
- **Context**: バージョン略称 → 数値マッピングの管理場所
- **Selected Approach**: `difficulty_scraper/version_map.py` に Python dict として配置
- **Rationale**: Scrapy プロジェクトパッケージ内に配置することで import が簡潔。コードとして管理され、型ヒントも利用可能
- **Trade-offs**: JSON/YAML ファイルと比べてコード的だが、Python プロジェクトとして自然

## Risks & Mitigations
- サイト HTML 構造変更（`.rank_p2_inner th` が消える）→ バージョンが全 NULL になるため気づきやすい
- 新バージョン追加時の VERSION_MAP 更新漏れ → NULL レコードが増えるが処理は継続する
