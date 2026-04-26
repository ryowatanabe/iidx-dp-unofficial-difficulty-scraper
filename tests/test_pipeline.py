"""
DifficultyScraperPipeline の version カラム対応をテストする。

- 新規 DB 作成時に version REAL カラムが存在すること
- 既存 DB（version カラムなし）へのマイグレーションがべき等に完了すること
- save_unofficial_difficulty() が version 値を正しく保存すること
- save_unofficial_difficulty() が NULL の version を正しく保存すること

要件: 1.1, 4.1, 4.2
"""
import sqlite3
import sys
import types
import unittest


def _install_scrapy_stub():
    """scrapy モジュールがなければ最小限のスタブを挿入する"""
    if 'scrapy' in sys.modules:
        return

    class Field(dict):
        pass

    class ItemMeta(type):
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


def _install_itemadapter_stub():
    """itemadapter モジュールがなければ最小限のスタブを挿入する"""
    if 'itemadapter' not in sys.modules:
        stub = types.ModuleType('itemadapter')

        class ItemAdapter:
            def __init__(self, item):
                self._item = item

            def __getitem__(self, key):
                return self._item[key]

        stub.ItemAdapter = ItemAdapter
        sys.modules['itemadapter'] = stub


_install_scrapy_stub()
_install_itemadapter_stub()


def _get_column_names(conn):
    """PRAGMA table_info で unofficial_difficulty のカラム名一覧を返す"""
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(unofficial_difficulty)')
    return [row[1] for row in cursor.fetchall()]


def _make_pipeline_with_in_memory_db():
    """DifficultyScraperPipeline のクラスを取得し、インメモリ DB を割り当てて返す"""
    # モジュールキャッシュをクリアして再インポート（_db のクラス変数リセットのため）
    for mod in list(sys.modules.keys()):
        if 'pipelines' in mod:
            del sys.modules[mod]

    from difficulty_scraper.pipelines import DifficultyScraperPipeline

    # インメモリ DB を作成してクラス変数に直接注入
    conn = sqlite3.connect(':memory:')
    DifficultyScraperPipeline._db = conn
    return DifficultyScraperPipeline, conn


class TestFreshDbHasVersionColumn(unittest.TestCase):
    """新規 DB 作成時に version REAL カラムが unofficial_difficulty テーブルに含まれること (要件 4.1)"""

    def test_fresh_db_has_version_column(self):
        """CREATE TABLE 時に version カラムが含まれること"""
        for mod in list(sys.modules.keys()):
            if 'pipelines' in mod:
                del sys.modules[mod]

        from difficulty_scraper.pipelines import DifficultyScraperPipeline

        # インメモリ DB を新規作成して get_database() を呼び出す前に注入
        # get_database() が sqlite3.connect() を呼ぶため、そこをパッチする
        original_connect = sqlite3.connect
        in_memory_conn = original_connect(':memory:')

        def mock_connect(*args, **kwargs):
            return in_memory_conn

        import unittest.mock as mock
        with mock.patch('sqlite3.connect', side_effect=mock_connect):
            DifficultyScraperPipeline._db = None
            db = DifficultyScraperPipeline.get_database()

        columns = _get_column_names(in_memory_conn)
        self.assertIn(
            'version', columns,
            f'version カラムが存在しない。実際のカラム: {columns}'
        )


class TestMigrationAddsVersionColumn(unittest.TestCase):
    """既存 DB（version カラムなし）に対してマイグレーションが正常完了すること (要件 4.1, 4.2)"""

    def test_migration_adds_version_column_without_error(self):
        """version カラムがない既存 DB に get_database() を実行してもエラーが発生しないこと"""
        for mod in list(sys.modules.keys()):
            if 'pipelines' in mod:
                del sys.modules[mod]

        from difficulty_scraper.pipelines import DifficultyScraperPipeline

        # version カラムなしの既存 DB を作成
        conn = sqlite3.connect(':memory:')
        conn.execute(
            'CREATE TABLE IF NOT EXISTS unofficial_difficulty('
            '    song_id TEXT PRIMARY KEY, '
            '    name TEXT NOT NULL, '
            '    difficulty TEXT NOT NULL, '
            '    level INT NOT NULL, '
            '    unofficial_diff REAL NOT NULL'
            ');'
        )
        conn.commit()

        # version カラムがないことを確認
        columns_before = _get_column_names(conn)
        self.assertNotIn('version', columns_before)

        # get_database() を呼び出す（マイグレーション実行）
        original_connect = sqlite3.connect
        in_memory_conn = conn

        def mock_connect(*args, **kwargs):
            return in_memory_conn

        import unittest.mock as mock
        with mock.patch('sqlite3.connect', side_effect=mock_connect):
            DifficultyScraperPipeline._db = None
            # OperationalError が発生しないこと
            try:
                db = DifficultyScraperPipeline.get_database()
            except sqlite3.OperationalError as e:
                self.fail(f'マイグレーション中に OperationalError が発生: {e}')

        # version カラムが追加されていること
        columns_after = _get_column_names(conn)
        self.assertIn(
            'version', columns_after,
            f'マイグレーション後も version カラムが存在しない。実際のカラム: {columns_after}'
        )

    def test_migration_is_idempotent(self):
        """version カラムがすでに存在する DB に get_database() を2回実行してもエラーが発生しないこと"""
        for mod in list(sys.modules.keys()):
            if 'pipelines' in mod:
                del sys.modules[mod]

        from difficulty_scraper.pipelines import DifficultyScraperPipeline

        original_connect = sqlite3.connect
        in_memory_conn = original_connect(':memory:')

        def mock_connect(*args, **kwargs):
            return in_memory_conn

        import unittest.mock as mock
        with mock.patch('sqlite3.connect', side_effect=mock_connect):
            DifficultyScraperPipeline._db = None
            DifficultyScraperPipeline.get_database()
            # 2回目: version カラムが既存のため ALTER TABLE は OperationalError を発生させるが
            # それを catch して pass するべき
            DifficultyScraperPipeline._db = None
            try:
                DifficultyScraperPipeline.get_database()
            except sqlite3.OperationalError as e:
                self.fail(f'2回目の get_database() で OperationalError が発生: {e}')


class TestSaveUnofficialDifficultyWithVersion(unittest.TestCase):
    """save_unofficial_difficulty() が version 値を正しく保存すること (要件 1.1, 4.2)"""

    def _make_conn_and_pipeline(self):
        """インメモリ DB とパイプラインを準備し、pipelines モジュールの sqlite3.connect をパッチしたまま返す"""
        import unittest.mock as mock

        for mod in list(sys.modules.keys()):
            if 'pipelines' in mod:
                del sys.modules[mod]

        from difficulty_scraper.pipelines import DifficultyScraperPipeline

        in_memory_conn = sqlite3.connect(':memory:')

        def mock_connect(*args, **kwargs):
            return in_memory_conn

        # pipelines モジュール内の sqlite3.connect をパッチして、
        # get_database() が常にインメモリ DB を返すようにする
        patcher = mock.patch(
            'difficulty_scraper.pipelines.sqlite3.connect',
            side_effect=mock_connect
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        DifficultyScraperPipeline._db = None
        DifficultyScraperPipeline.get_database()

        pipeline = DifficultyScraperPipeline()
        return pipeline, in_memory_conn, DifficultyScraperPipeline

    def test_save_with_float_version(self):
        """version に float 値を指定して保存し、正しく取得できること"""
        pipeline, conn, PipelineClass = self._make_conn_and_pipeline()

        from difficulty_scraper.items import UnofficialDifficulty
        item = UnofficialDifficulty(
            song_id='14029-7-0',
            name='op.31 叙情',
            difficulty='ANOTHER',
            level=12,
            unofficial_diff=11.5,
            version=14.0,
        )
        # save_unofficial_difficulty() の中で get_database() が呼ばれるため
        # パッチが有効な状態でインメモリ DB が使われる
        PipelineClass._db = None
        pipeline.save_unofficial_difficulty(item)

        cursor = conn.cursor()
        cursor.execute(
            'SELECT version FROM unofficial_difficulty WHERE song_id = ?',
            ('14029-7-0',)
        )
        row = cursor.fetchone()
        self.assertIsNotNone(row, 'レコードが保存されていない')
        self.assertEqual(
            row[0], 14.0,
            f'version の値が正しくない。期待: 14.0, 実際: {row[0]}'
        )

    def test_save_with_none_version(self):
        """version に None を指定して保存し、NULL として取得できること"""
        pipeline, conn, PipelineClass = self._make_conn_and_pipeline()

        from difficulty_scraper.items import UnofficialDifficulty
        item = UnofficialDifficulty(
            song_id='99999-7-0',
            name='Unknown Version Song',
            difficulty='HYPER',
            level=11,
            unofficial_diff=10.5,
            version=None,
        )
        PipelineClass._db = None
        pipeline.save_unofficial_difficulty(item)

        cursor = conn.cursor()
        cursor.execute(
            'SELECT version FROM unofficial_difficulty WHERE song_id = ?',
            ('99999-7-0',)
        )
        row = cursor.fetchone()
        self.assertIsNotNone(row, 'レコードが保存されていない')
        self.assertIsNone(
            row[0],
            f'version が NULL でない。実際: {row[0]}'
        )


if __name__ == '__main__':
    unittest.main()
