# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import sqlite3
import logging

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class EreternetScraperPipeline:
    _db = None

    @classmethod
    def get_database(cls):
        cls._db = sqlite3.connect(
            os.path.join(os.getcwd(), './data/data.db'))

        # テーブル作成
        cursor = cls._db.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS ereternet_difficulty(\
                song_id INTEGER PRIMARY KEY, \
                name TEXT NOT NULL, \
                difficulty TEXT NOT NULL, \
                unofficial_diff REAL NOT NULL, \
                ec_diff REAL NOT NULL, \
                hc_diff REAL NOT NULL, \
                exh_diff REAL NOT NULL, \
                ec_count INTEGER NOT NULL, \
                hc_count INTEGER NOT NULL, \
                exh_count INTEGER NOT NULL \
            );')

        return cls._db

    def process_item(self, item, spider):
        if type(item).__name__ == 'EreterNetDifficulty':
            self.save_ereternet_difficulty(item)

        return item

    def save_ereternet_difficulty(self, item):
        db = self.get_database()
        db.execute(
            'REPLACE INTO ereternet_difficulty( \
                song_id, name, difficulty, unofficial_diff, \
                ec_diff, hc_diff, exh_diff, ec_count, hc_count, exh_count \
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (
                item['song_id'],
                item['name'],
                item['difficulty'],
                item['unofficial_diff'],
                item['ec_diff'],
                item['hc_diff'],
                item['exh_diff'],
                item['ec_count'],
                item['hc_count'],
                item['exh_count']
            )
        )
        db.commit()
