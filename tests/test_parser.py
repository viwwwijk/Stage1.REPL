"""Модульные тесты для emulator.parser."""
import unittest

from emulator.parser import ParserError, parse_line, split_command


class TestParseLine(unittest.TestCase):
    """Проверка разбора строки на токены."""

    def test_simple_command(self):
        self.assertEqual(parse_line("ls"), ["ls"])

    def test_command_with_args(self):
        self.assertEqual(parse_line("ls -l file.txt"),
                         ["ls", "-l", "file.txt"])

    def test_double_quotes(self):
        self.assertEqual(parse_line('cd "my folder"'),
                         ["cd", "my folder"])

    def test_single_quotes(self):
        self.assertEqual(parse_line("cd 'папка с пробелом'"),
                         ["cd", "папка с пробелом"])

    def test_empty_line(self):
        self.assertEqual(parse_line("   "), [])

    def test_unclosed_quote(self):
        with self.assertRaises(ParserError):
            parse_line('cd "unclosed')


class TestSplitCommand(unittest.TestCase):
    """Проверка разделения токенов на команду и аргументы."""

    def test_split_with_args(self):
        self.assertEqual(split_command(["ls", "-l", "file"]),
                         ("ls", ["-l", "file"]))

    def test_split_without_args(self):
        self.assertEqual(split_command(["ls"]), ("ls", []))

    def test_empty_tokens(self):
        with self.assertRaises(ParserError):
            split_command([])


if __name__ == "__main__":
    unittest.main()
