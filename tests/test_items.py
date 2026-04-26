"""
UnofficialDifficulty アイテムの version フィールドと
version_map.py のインポート可能性を検証するテスト

Scrapy が実行環境にインストールされていない場合でも動作するよう、
scrapy モジュールのスタブを sys.modules に挿入してテストする。
"""
import sys
import types
import unittest


def _install_scrapy_stub():
    """scrapy モジュールがなければ最小限のスタブを挿入する"""
    if 'scrapy' in sys.modules:
        return

    class Field(dict):
        """scrapy.Field のスタブ"""
        pass

    class ItemMeta(type):
        """scrapy.Item のメタクラス風スタブ（fields を収集する）"""
        def __new__(mcs, name, bases, namespace):
            fields = {}
            # 基底クラスの fields を継承
            for base in bases:
                if hasattr(base, 'fields'):
                    fields.update(base.fields)
            # 現クラスで定義された Field を収集
            for key, value in list(namespace.items()):
                if isinstance(value, Field):
                    fields[key] = value
            namespace['fields'] = fields
            return super().__new__(mcs, name, bases, namespace)

    class Item(metaclass=ItemMeta):
        """scrapy.Item のスタブ"""
        def __init__(self, **kwargs):
            self._data = {}
            for k, v in kwargs.items():
                if k not in self.__class__.fields:
                    raise KeyError(f'Item does not support field: {k}')
                self._data[k] = v

        def __getitem__(self, key):
            return self._data[key]

        def __setitem__(self, key, value):
            if key not in self.__class__.fields:
                raise KeyError(f'Item does not support field: {key}')
            self._data[key] = value

    scrapy_stub = types.ModuleType('scrapy')
    scrapy_stub.Item = Item
    scrapy_stub.Field = Field
    sys.modules['scrapy'] = scrapy_stub


_install_scrapy_stub()


class TestVersionMapImportable(unittest.TestCase):
    """前提条件: version_map.py が存在し VERSION_MAP がインポート可能であること"""

    def test_version_map_importable(self):
        """difficulty_scraper.version_map から VERSION_MAP がインポートできること"""
        from difficulty_scraper.version_map import VERSION_MAP
        self.assertIsInstance(VERSION_MAP, dict)

    def test_version_map_is_not_empty(self):
        """VERSION_MAP が少なくとも 1 件以上のエントリを持つこと"""
        from difficulty_scraper.version_map import VERSION_MAP
        self.assertGreater(len(VERSION_MAP), 0)


class TestUnofficialDifficultyVersionField(unittest.TestCase):
    """UnofficialDifficulty アイテムに version フィールドが定義されていること (要件 1.2)"""

    def test_version_field_exists(self):
        """UnofficialDifficulty に version フィールドが定義されていること"""
        from difficulty_scraper.items import UnofficialDifficulty
        self.assertIn('version', UnofficialDifficulty.fields)

    def test_version_field_can_be_set_to_float(self):
        """version フィールドに float 値を設定できること"""
        from difficulty_scraper.items import UnofficialDifficulty
        item = UnofficialDifficulty(
            song_id='test_song',
            name='Test Song',
            difficulty='DPA',
            level=12,
            unofficial_diff=11.5,
            version=14.0,
        )
        self.assertEqual(item['version'], 14.0)

    def test_version_field_can_be_set_to_none(self):
        """version フィールドに None を設定できること（バージョン未登録楽曲）"""
        from difficulty_scraper.items import UnofficialDifficulty
        item = UnofficialDifficulty(
            song_id='test_song',
            name='Test Song',
            difficulty='DPA',
            level=12,
            unofficial_diff=11.5,
            version=None,
        )
        self.assertIsNone(item['version'])

    def test_existing_fields_still_present(self):
        """既存フィールド（song_id, name, difficulty, level, unofficial_diff）が引き続き存在すること"""
        from difficulty_scraper.items import UnofficialDifficulty
        expected_fields = {'song_id', 'name', 'difficulty', 'level', 'unofficial_diff'}
        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(field, UnofficialDifficulty.fields)


if __name__ == '__main__':
    unittest.main()
