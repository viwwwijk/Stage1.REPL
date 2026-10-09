"""Модульные тесты для emulator.commands."""
import unittest

from emulator.commands import EXIT_RESULT, CommandError, execute
from emulator.session import Session
from emulator.vfs import parse_vfs


class ExecuteTest(unittest.TestCase):
    """Проверка функции execute."""

    def test_default_session(self):
        """Без сеанса команды работают с пустой VFS."""
        self.assertEqual(execute("ls", []), "")

    def test_exit(self):
        """Команда exit возвращает признак завершения."""
        self.assertEqual(execute("exit", []), EXIT_RESULT)

    def test_exit_with_arguments(self):
        """Команда exit не принимает аргументов."""
        with self.assertRaises(CommandError):
            execute("exit", ["now"])

    def test_unknown_command(self):
        """Неизвестная команда приводит к ошибке."""
        with self.assertRaises(CommandError):
            execute("mkdir", [])

    def test_conf_dump_with_config(self):
        """conf-dump выводит параметры в формате ключ-значение."""
        config = {"vfs-path": "vfs.csv", "script-path": "start.txt"}
        result = execute("conf-dump", [], Session(config=config))
        self.assertEqual(result, "vfs-path=vfs.csv\nscript-path=start.txt")

    def test_conf_dump_without_config(self):
        """Без переданного config значения параметров считаются пустыми."""
        result = execute("conf-dump", [])
        self.assertEqual(result, "vfs-path=\nscript-path=")

    def test_conf_dump_with_arguments(self):
        """conf-dump не принимает аргументов."""
        with self.assertRaises(CommandError):
            execute("conf-dump", ["extra"])

    def test_vfs_tree(self):
        """vfs-tree выводит дерево загруженной VFS."""
        vfs = parse_vfs("path,type,content\n/a.txt,file,\n")
        result = execute("vfs-tree", [], Session(vfs))
        self.assertEqual(result, "/\n  a.txt (0 байт)")

    def test_vfs_tree_with_arguments(self):
        """vfs-tree не принимает аргументов."""
        with self.assertRaises(CommandError):
            execute("vfs-tree", ["/home"])

    def test_vfs_tree_empty(self):
        """Для пустой VFS vfs-tree выводит только корень."""
        self.assertEqual(execute("vfs-tree", []), "/")


class CommandErrorTest(unittest.TestCase):
    """Проверка исключения CommandError."""

    def test_output_defaults_to_empty(self):
        """По умолчанию частичного вывода нет."""
        self.assertEqual(CommandError("ошибка").output, "")

    def test_output_is_kept(self):
        """Частичный вывод сохраняется отдельно от текста ошибки."""
        error = CommandError("строка 1\nстрока 2", "готово")
        self.assertEqual(str(error), "строка 1\nстрока 2")
        self.assertEqual(error.output, "готово")


if __name__ == "__main__":
    unittest.main()
