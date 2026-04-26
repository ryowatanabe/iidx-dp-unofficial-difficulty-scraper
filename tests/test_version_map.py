"""
VERSION_MAP の変換ロジックをユニットテストで検証する

要件:
  3.1 VERSION_MAP による数値変換（登録済みキー）
  3.2 変換表に存在しないキーは None を返す
  3.3 変換表はコード変更なしに更新できる設定ファイルとして管理される
"""
import unittest


class TestVersionMapRegisteredKey(unittest.TestCase):
    """登録済みキーが正しい float 値を返すこと (要件 3.1)"""

    def test_gold_returns_14_float(self):
        """VERSION_MAP.get("GOLD") が 14.0 を返すこと"""
        from difficulty_scraper.version_map import VERSION_MAP
        result = VERSION_MAP.get("GOLD")
        self.assertIsNotNone(result, '"GOLD" が VERSION_MAP に登録されていない')
        self.assertIsInstance(result, (int, float), f'"GOLD" の値が数値でない: {result!r}')
        self.assertEqual(result, 14.0, f'"GOLD" の値が 14.0 でない: {result!r}')

    def test_registered_keys_return_numeric_values(self):
        """VERSION_MAP の全登録済みキーが数値（int または float）を返すこと"""
        from difficulty_scraper.version_map import VERSION_MAP
        for key, value in VERSION_MAP.items():
            with self.subTest(key=key):
                if value is not None:
                    self.assertIsInstance(
                        value,
                        (int, float),
                        f'KEY "{key}" の値 {value!r} が数値でない'
                    )


class TestVersionMapUnregisteredKey(unittest.TestCase):
    """未登録キーが None を返すこと (要件 3.2)"""

    def test_unknown_key_returns_none(self):
        """VERSION_MAP.get("UNKNOWN") が None を返すこと（dict.get() のデフォルト）"""
        from difficulty_scraper.version_map import VERSION_MAP
        result = VERSION_MAP.get("UNKNOWN")
        self.assertIsNone(result, f'"UNKNOWN" の get() が None でない: {result!r}')

    def test_empty_string_key_returns_none(self):
        """VERSION_MAP.get("") が None を返すこと"""
        from difficulty_scraper.version_map import VERSION_MAP
        result = VERSION_MAP.get("")
        self.assertIsNone(result, f'空文字列キーの get() が None でない: {result!r}')

    def test_numeric_string_key_returns_none(self):
        """VERSION_MAP.get("999") が None を返すこと（存在しない数値文字列）"""
        from difficulty_scraper.version_map import VERSION_MAP
        result = VERSION_MAP.get("999")
        self.assertIsNone(result, f'"999" の get() が None でない: {result!r}')


class TestVersionGuardLogic(unittest.TestCase):
    """Spider の version_str ガードロジックを検証する

    unofficial_diff.py のガードロジック:
        version = VERSION_MAP.get(version_str.strip()) if version_str else None
    """

    def _apply_guard(self, version_str):
        """Spider と同一のガードロジックを適用して version を返す"""
        from difficulty_scraper.version_map import VERSION_MAP
        return VERSION_MAP.get(version_str.strip()) if version_str else None

    def test_none_version_str_returns_none(self):
        """version_str = None のとき、ガードロジックにより version = None となること"""
        version = self._apply_guard(None)
        self.assertIsNone(version, f'version_str が None のとき version が None でない: {version!r}')

    def test_empty_string_version_str_returns_none(self):
        """version_str = "" のとき、空文字列は falsy なので version = None となること"""
        version = self._apply_guard("")
        self.assertIsNone(version, f'version_str が空文字列のとき version が None でない: {version!r}')

    def test_whitespace_only_version_str_returns_none(self):
        """version_str = "  "（空白のみ）のとき、strip() 後も空文字列なので VERSION_MAP に存在せず None となること"""
        version = self._apply_guard("  ")
        # "  ".strip() = "" → VERSION_MAP.get("") = None
        self.assertIsNone(
            version,
            f'version_str が空白のみのとき version が None でない: {version!r}'
        )

    def test_valid_version_str_returns_float(self):
        """version_str = "GOLD" のとき、ガードロジックが 14.0 を返すこと"""
        version = self._apply_guard("GOLD")
        self.assertEqual(version, 14.0, f'version_str = "GOLD" のとき version が 14.0 でない: {version!r}')

    def test_version_str_with_surrounding_whitespace(self):
        """version_str に前後の空白がある場合、strip() により正しく変換されること"""
        version = self._apply_guard("  GOLD  ")
        self.assertEqual(
            version, 14.0,
            f'前後空白つき version_str のとき version が 14.0 でない: {version!r}'
        )

    def test_unknown_version_str_returns_none(self):
        """version_str = "UNKNOWN" のとき、VERSION_MAP に存在しないので version = None となること"""
        version = self._apply_guard("UNKNOWN")
        self.assertIsNone(version, f'version_str = "UNKNOWN" のとき version が None でない: {version!r}')


class TestVersionMapAsConfigFile(unittest.TestCase):
    """VERSION_MAP が設定ファイルとしてモジュールレベル dict でインポートできること (要件 3.3)"""

    def test_version_map_importable_from_module(self):
        """difficulty_scraper.version_map から VERSION_MAP が dict としてインポートできること"""
        from difficulty_scraper.version_map import VERSION_MAP
        self.assertIsInstance(
            VERSION_MAP, dict,
            f'VERSION_MAP が dict でない: {type(VERSION_MAP)}'
        )

    def test_version_map_is_module_level_attribute(self):
        """VERSION_MAP が difficulty_scraper.version_map モジュールのトップレベル属性であること"""
        import difficulty_scraper.version_map as vm
        self.assertTrue(
            hasattr(vm, 'VERSION_MAP'),
            'difficulty_scraper.version_map に VERSION_MAP 属性が存在しない'
        )

    def test_version_map_all_values_are_float_or_none(self):
        """VERSION_MAP の全値が float（または None）であること（型注釈 dict[str, float | None]）"""
        from difficulty_scraper.version_map import VERSION_MAP
        for key, value in VERSION_MAP.items():
            with self.subTest(key=key):
                self.assertTrue(
                    value is None or isinstance(value, (int, float)),
                    f'KEY "{key}" の値 {value!r} が float でも None でもない'
                )

    def test_version_map_keys_are_strings(self):
        """VERSION_MAP の全キーが str であること（型注釈 dict[str, ...]）"""
        from difficulty_scraper.version_map import VERSION_MAP
        for key in VERSION_MAP.keys():
            with self.subTest(key=key):
                self.assertIsInstance(
                    key, str,
                    f'キー {key!r} が str でない: {type(key)}'
                )


if __name__ == '__main__':
    unittest.main()
