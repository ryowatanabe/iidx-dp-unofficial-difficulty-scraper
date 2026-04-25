# Requirements Document

## Introduction
IIDX DP プレイヤーが各楽曲の収録バージョン（どの beatmania IIDX バージョンで追加されたか）を把握できるよう、unofficial-diff スパイダーが zasa.sakura.ne.jp から収集するデータに「収録バージョン」情報を追加する。

## Boundary Context
- **In scope**: zasa.sakura.ne.jp からの収録バージョン情報の取得・保存・CSV エクスポート
- **Out of scope**: ereter.net / ereternet_difficulty データへの変更
- **Adjacent expectations**: zasa.sakura.ne.jp の難易度表ページが各楽曲の収録バージョン情報を含んでいること

## Requirements

### Requirement 1: 収録バージョンの取得と保存

**Objective:** As a ツール利用者, I want スクレイパーが各楽曲の収録バージョンを収集・保存してほしい, so that データベース上で楽曲の収録バージョンを参照できる

#### Acceptance Criteria
1. When `scrapy crawl unofficial_diff` を実行したとき, the スクレイパー shall 各楽曲の収録バージョン情報を取得し、unofficial_difficulty テーブルに保存する
2. The スクレイパー shall 各楽曲レコードに収録バージョンを紐付けて保存する
3. If 収録バージョン情報がページ上に存在しない楽曲がある場合, the スクレイパー shall その楽曲の収録バージョンを空値として保存し、処理を継続する

### Requirement 2: CSV エクスポートへの反映

**Objective:** As a ツール利用者, I want エクスポートされる CSV に収録バージョンが含まれてほしい, so that スプレッドシートなど外部ツールで収録バージョンを活用できる

#### Acceptance Criteria
1. When `./export_csv.py` を実行したとき, the エクスポーター shall unofficial_difficulty.csv に収録バージョンカラムを含めて出力する
2. The unofficial_difficulty.csv shall 既存の全カラム（song_id, name, difficulty, level, unofficial_diff）に加えて収録バージョンカラムを含む

### Requirement 3: バージョン名の数値変換

**Objective:** As a ツール利用者, I want HTML 上のバージョン名文字列を数値に変換して保存してほしい, so that バージョンの順序比較やソートを数値で行える

#### Acceptance Criteria
1. The スクレイパー shall HTML から取得したバージョン名を、あらかじめ定義された変換表に基づいて数値に変換して保存する
2. If バージョン名が変換表に存在しない場合, the スクレイパー shall そのレコードの収録バージョンを NULL として保存し、処理を継続する
3. The 変換表 shall コード変更なしに更新できる設定ファイルとして管理される

### Requirement 4: 既存データベースとの互換性

**Objective:** As a ツール利用者, I want 収録バージョンカラムがない既存の DB に対してもスクレイパーを実行できる, so that 過去データを削除・再構築せずに済む

#### Acceptance Criteria
1. When 収録バージョンカラムが存在しない状態のデータベースに対して `scrapy crawl unofficial_diff` を実行したとき, the スクレイパー shall エラーを発生させずに完了する
2. When スクレイパーが正常完了したとき, the スクレイパー shall 既存レコードを収録バージョン情報を含む最新データに更新する

