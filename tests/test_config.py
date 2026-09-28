"""Модульные тесты для emulator.config."""
import unittest

from emulator.config import parse_args


class ParseArgsTest(unittest.TestCase):
    """Проверка функции parse_args."""

    def test_no_arguments(self):
        """Без параметров оба пути равны None."""
        args = parse_args([])
        self.assertIsNone(args.vfs_path)
        self.assertIsNone(args.script_path)

    def test_vfs_path_only(self):
        """Параметр --vfs-path сохраняется в vfs_path."""
        args = parse_args(["--vfs-path", "/tmp/vfs.csv"])
        self.assertEqual(args.vfs_path, "/tmp/vfs.csv")
        self.assertIsNone(args.script_path)

    def test_script_path_only(self):
        """Параметр --script-path сохраняется в script_path."""
        args = parse_args(["--script-path", "start.txt"])
        self.assertIsNone(args.vfs_path)
        self.assertEqual(args.script_path, "start.txt")

    def test_both_parameters(self):
        """Оба параметра можно задать одновременно, в любом порядке."""
        args = parse_args(
            ["--script-path", "start.txt", "--vfs-path", "vfs.csv"])
        self.assertEqual(args.vfs_path, "vfs.csv")
        self.assertEqual(args.script_path, "start.txt")


if __name__ == "__main__":
    unittest.main()
