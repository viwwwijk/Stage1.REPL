"""Модульные тесты для emulator.commands."""
import unittest

from emulator.commands import EXIT_RESULT, CommandError, execute


class ExecuteTest(unittest.TestCase):
    """Проверка функции execute."""

    def test_stub_without_arguments(self):
        """Заглушка сообщает об отсутствии аргументов."""
        self.assertEqual(execute("ls", []), "ls: аргументы отсутствуют")

    def test_stub_with_arguments(self):
        """Заглушка выводит своё имя и аргументы."""
        result = execute("cd", ["my dir", "-f"])
        self.assertEqual(result, "cd: аргументы: my dir, -f")

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
        result = execute("conf-dump", [], config)
        self.assertEqual(result, "vfs-path=vfs.csv\nscript-path=start.txt")

    def test_conf_dump_without_config(self):
        """Без переданного config значения параметров считаются пустыми."""
        result = execute("conf-dump", [])
        self.assertEqual(result, "vfs-path=\nscript-path=")

    def test_conf_dump_with_arguments(self):
        """conf-dump не принимает аргументов."""
        with self.assertRaises(CommandError):
            execute("conf-dump", ["extra"], {})


if __name__ == "__main__":
    unittest.main()
