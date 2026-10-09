"""Модульные тесты для emulator.parser."""
import unittest

from emulator.parser import ParserError, parse_line, split_command


class TestParseLine(unittest.TestCase):
    """Проверка разбора строки на токены."""

    def test_simple_command(self):
        """Команда без аргументов даёт один токен."""
        self.assertEqual(parse_line("ls"), ["ls"])

    def test_command_with_args(self):
        """Аргументы разделяются пробелами."""
        self.assertEqual(parse_line("ls -l file.txt"),
                         ["ls", "-l", "file.txt"])

    def test_double_quotes(self):
        """Двойные кавычки объединяют слова в один аргумент."""
        self.assertEqual(parse_line('cd "my folder"'),
                         ["cd", "my folder"])

    def test_single_quotes(self):
        """Одинарные кавычки объединяют слова в один аргумент."""
        self.assertEqual(parse_line("cd 'папка с пробелом'"),
                         ["cd", "папка с пробелом"])

    def test_empty_line(self):
        """Строка из пробелов не содержит токенов."""
        self.assertEqual(parse_line("   "), [])

    def test_unclosed_quote(self):
        """Незакрытая кавычка приводит к ParserError."""
        with self.assertRaises(ParserError):
            parse_line('cd "unclosed')


class TestSplitCommand(unittest.TestCase):
    """Проверка разделения токенов на команду и аргументы."""

    def test_split_with_args(self):
        """Первый токен — команда, остальные — аргументы."""
        self.assertEqual(split_command(["ls", "-l", "file"]),
                         ("ls", ["-l", "file"]))

    def test_split_without_args(self):
        """Команда без аргументов даёт пустой список."""
        self.assertEqual(split_command(["ls"]), ("ls", []))

    def test_empty_tokens(self):
        """Пустой список токенов приводит к ParserError."""
        with self.assertRaises(ParserError):
            split_command([])


if __name__ == "__main__":
    unittest.main()
