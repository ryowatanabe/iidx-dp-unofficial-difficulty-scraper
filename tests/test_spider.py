"""
UnofficialDiffSpider.parsePost() の VERSION_MAP マッピングと
内側ループ変更をテストする。

Scrapy が実行環境にインストールされていない場合でも動作するよう、
scrapy モジュールのスタブを sys.modules に挿入してテストする。
"""
import sys
import types
import unittest


def _install_scrapy_stub():
    """scrapy モジュールがなければ最小限のスタブを挿入する。
    すでに挿入済みでも Spider / FormRequest 属性が欠ければ追加する。"""

    class Field(dict):
        """scrapy.Field のスタブ"""
        pass

    class ItemMeta(type):
        """scrapy.Item のメタクラス風スタブ（fields を収集する）"""
        def __new__(mcs, name, bases, namespace):
            fields = {}
            for base in bases:
                if hasattr(base, 'fields'):
                    fields.update(base.fields)
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

    class Spider:
        """scrapy.Spider のスタブ"""
        pass

    class FormRequest:
        """scrapy.FormRequest のスタブ"""
        @staticmethod
        def from_response(*args, **kwargs):
            return None

    if 'scrapy' not in sys.modules:
        scrapy_stub = types.ModuleType('scrapy')
        scrapy_stub.Item = Item
        scrapy_stub.Field = Field
        scrapy_stub.Spider = Spider
        scrapy_stub.FormRequest = FormRequest

        http_stub = types.ModuleType('scrapy.http')
        scrapy_stub.http = http_stub
        sys.modules['scrapy'] = scrapy_stub
        sys.modules['scrapy.http'] = http_stub
    else:
        # すでにスタブ挿入済み: Spider / FormRequest が欠けていれば補完する
        scrapy_stub = sys.modules['scrapy']
        if not hasattr(scrapy_stub, 'Spider'):
            scrapy_stub.Spider = Spider
        if not hasattr(scrapy_stub, 'FormRequest'):
            scrapy_stub.FormRequest = FormRequest
        if 'scrapy.http' not in sys.modules:
            http_stub = types.ModuleType('scrapy.http')
            scrapy_stub.http = http_stub
            sys.modules['scrapy.http'] = http_stub


_install_scrapy_stub()


class MockSelector:
    """CSS セレクタの呼び出しをシミュレートする最小限のスタブ"""

    def __init__(self, data):
        """
        data: list of dicts または None
              各 dict は css() 呼び出しのキーに対する戻り値を持つ
        """
        self._data = data if data is not None else []

    def css(self, selector):
        # セレクタに応じた結果を返す
        results = []
        for item in self._data:
            if selector in item:
                val = item[selector]
                if isinstance(val, list):
                    results.extend(val)
                else:
                    results.append(val)
        return MockSelectorList(results)

    def extract_first(self):
        return self._data[0] if self._data else None


class MockSelectorList:
    """css() の戻り値となるセレクタリストのスタブ"""

    def __init__(self, items):
        self._items = items

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def extract_first(self):
        return self._items[0] if self._items else None

    def css(self, selector):
        results = []
        for item in self._items:
            if hasattr(item, 'css'):
                sub = item.css(selector)
                results.extend(list(sub))
        return MockSelectorList(results)


class MockResponse:
    """
    parsePost() が受け取る Scrapy レスポンスのスタブ。
    HTML 構造を模倣するためにネストした MockSelector を組み立てる。
    """

    def __init__(self, songs_by_version):
        """
        songs_by_version: list of (version_str, list of (song_id, span_text))
            例: [("GOLD", [("14029-7-0", "op.31 叙情 [A]")]),
                 ("RA",   [("18055-7-0", "Kailua [A]")])]
        """
        self._songs_by_version = songs_by_version

    def css(self, selector):
        if selector == '.rank_form > tr:nth-child(3) > td > input[type=radio]:checked::attr(value)':
            return MockSelectorList(['12'])

        if selector == '.rank_p2 > tr':
            return MockSelectorList(self._build_outer_rows())

        return MockSelectorList([])

    def _build_outer_rows(self):
        """rank_p2 の外側行を生成する（diff="☆12" の1行のみ）"""
        return [OuterRow('☆12', self._songs_by_version)]


class InnerRow:
    """rank_p2_inner の内側行（<tr><th>VERSION</th><td><a>...</a></td></tr>）のスタブ"""

    def __init__(self, version_str, song_id, span_text):
        self._version_str = version_str
        self._song_id = song_id
        self._span_text = span_text

    def css(self, selector):
        if selector == 'th::text':
            if self._version_str is not None:
                return MockSelectorList([self._version_str])
            return MockSelectorList([])

        if selector == 'a.music':
            return MockSelectorList([SongElement(self._song_id, self._span_text)])

        return MockSelectorList([])


class SongElement:
    """<a class="music"> 要素のスタブ"""

    def __init__(self, song_id, span_text):
        self._song_id = song_id
        self._span_text = span_text

    def css(self, selector):
        if selector == 'a::attr(href)':
            return MockSelectorList([f'music.php?id={self._song_id}'])
        if selector == 'span::text':
            return MockSelectorList([self._span_text])
        return MockSelectorList([])


class OuterRow:
    """rank_p2 の外側行のスタブ"""

    def __init__(self, diff_text, songs_by_version):
        self._diff_text = diff_text
        self._songs_by_version = songs_by_version

    def css(self, selector):
        if selector == 'td:first-child::text':
            return MockSelectorList([self._diff_text])

        if selector == '.rank_p2_inner tr':
            rows = []
            for version_str, songs in self._songs_by_version:
                for song_id, span_text in songs:
                    rows.append(InnerRow(version_str, song_id, span_text))
            return MockSelectorList(rows)

        # 古いセレクタ（フラグ OFF 時の古い実装用）
        if selector == '.rank_p2_inner a.music':
            songs = []
            for _version_str, song_list in self._songs_by_version:
                for song_id, span_text in song_list:
                    songs.append(SongElement(song_id, span_text))
            return MockSelectorList(songs)

        return MockSelectorList([])


class TestParsePostVersionMapping(unittest.TestCase):
    """parsePost() が VERSION_MAP を使ってバージョンを正しくマッピングすること"""

    def _make_spider(self):
        """テスト用の UnofficialDiffSpider インスタンスを生成する"""
        import importlib
        # キャッシュを無効化して再インポート
        for mod in list(sys.modules.keys()):
            if 'unofficial_diff' in mod:
                del sys.modules[mod]
        from difficulty_scraper.spiders.unofficial_diff import UnofficialDiffSpider
        spider = object.__new__(UnofficialDiffSpider)
        spider.difficulty_map = {
            'N': 'NORMAL',
            'H': 'HYPER',
            'A': 'ANOTHER',
            'L': 'LEGGENDARIA'
        }
        import logging
        spider.logger = logging.getLogger('test_spider')
        return spider

    def test_version_mapped_from_version_map(self):
        """VERSION_MAP に登録済みのバージョン略称が正しく数値にマッピングされること (要件 3.1)"""
        spider = self._make_spider()
        response = MockResponse([
            ('GOLD', [('14029-7-0', 'op.31 叙情 [A]')]),
        ])

        items = list(spider.parsePost(response))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['version'], 14.0)

    def test_version_none_for_unknown_key(self):
        """VERSION_MAP に未登録のバージョン略称の場合、version が None になること (要件 3.2)"""
        spider = self._make_spider()
        response = MockResponse([
            ('UNKNOWN_VER', [('99999-7-0', 'Unknown Song [A]')]),
        ])

        items = list(spider.parsePost(response))
        self.assertEqual(len(items), 1)
        self.assertIsNone(items[0]['version'])

    def test_version_none_when_th_is_missing(self):
        """th::text が None（バージョン行なし）の場合、version が None になること (要件 1.3)"""
        spider = self._make_spider()
        response = MockResponse([
            (None, [('12345-7-0', 'No Version Song [H]')]),
        ])

        items = list(spider.parsePost(response))
        self.assertEqual(len(items), 1)
        self.assertIsNone(items[0]['version'])

    def test_multiple_versions_in_same_diff(self):
        """複数のバージョン略称が同一の diff 行に存在する場合、それぞれ正しくマッピングされること"""
        spider = self._make_spider()
        response = MockResponse([
            ('GOLD', [('14029-7-0', 'op.31 叙情 [A]')]),
            ('RA',   [('18055-7-0', 'Kailua [A]')]),
        ])

        items = list(spider.parsePost(response))
        self.assertEqual(len(items), 2)

        versions = [item['version'] for item in items]
        self.assertIn(14.0, versions)
        self.assertIn(18.0, versions)

    def test_existing_fields_still_set(self):
        """既存フィールド（song_id, name, difficulty, level, unofficial_diff）が引き続き設定されること"""
        spider = self._make_spider()
        response = MockResponse([
            ('GOLD', [('14029-7-0', 'op.31 叙情 [A]')]),
        ])

        items = list(spider.parsePost(response))
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item['song_id'], '14029-7-0')
        self.assertEqual(item['name'], 'op.31 叙情')
        self.assertEqual(item['difficulty'], 'ANOTHER')
        self.assertEqual(item['level'], '12')
        self.assertIsNotNone(item['unofficial_diff'])



if __name__ == '__main__':
    unittest.main()
