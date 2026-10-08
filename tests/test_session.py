"""Модульные тесты для emulator.session."""
import unittest

from emulator.session import Session
from emulator.vfs import VfsError, parse_vfs


class SessionTest(unittest.TestCase):
    """Проверка состояния сеанса."""

    def setUp(self):
        """Создать сеанс с каталогом /a и файлом /a/b.txt."""
        vfs = parse_vfs("path,type,content\n/a/b.txt,file,\n")
        self.session = Session(vfs)

    def test_defaults(self):
        """Новый сеанс начинается в корне, параметров нет."""
        session = Session()
        self.assertEqual(session.cwd_path(), "/")
        self.assertEqual(session.config, {})
        self.assertIsNone(session.prev_cwd)

    def test_lookup_relative(self):
        """Путь ищется относительно текущего каталога."""
        self.session.cwd = ["a"]
        parts, node = self.session.lookup("b.txt")
        self.assertEqual(parts, ["a", "b.txt"])
        self.assertFalse(node.is_dir)

    def test_lookup_file_with_trailing_slash(self):
        """Путь к файлу со слешем на конце — ошибка, как в UNIX."""
        with self.assertRaises(VfsError):
            self.session.lookup("/a/b.txt/")

    def test_change_dir_remembers_previous(self):
        """change_dir запоминает предыдущий каталог."""
        self.session.change_dir(["a"])
        self.assertEqual(self.session.cwd_path(), "/a")
        self.assertEqual(self.session.prev_cwd, [])


if __name__ == "__main__":
    unittest.main()
