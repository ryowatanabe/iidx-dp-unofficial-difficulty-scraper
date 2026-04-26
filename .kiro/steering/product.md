# Product Overview

beatmania IIDX の DP (ダブルプレー) プレイヤー向けに、複数の非公式難易度情報源からデータを収集・統合し、ローカルデータベースおよびCSVとして提供するスクレイピングツール。

## Core Capabilities

- **データ収集**: 2つの外部サイト（ereter.net、zasa.sakura.ne.jp）から非公式難易度データをスクレイピング
- **データ永続化**: SQLite データベース (`data/data.db`) へのアップサート保存
- **CSV エクスポート**: 3種類のCSVファイル（unofficial_difficulty, ereternet_difficulty, ereternet_difficulty_diffonly）へのエクスポート
- **差分更新**: 既存レコードを `REPLACE INTO` で更新することで最新データを維持

## Target Use Cases

- IIDX DP の選曲・練習計画のため、難易度情報をオフラインで参照したい
- 複数の難易度評価源（ereter.net の統計難易度、非公式難易度表）を一元管理したい
- 難易度データをスプレッドシートなど外部ツールで活用したい

## Value Proposition

公式難易度表にないDP譜面の非公式難易度を、複数のコミュニティソースから自動収集して一元管理できる唯一のツール。手動収集の手間を排除し、最新データへの定期更新を `scrapy crawl` コマンド1つで実現する。

---
_Focus on patterns and purpose, not exhaustive feature lists_
