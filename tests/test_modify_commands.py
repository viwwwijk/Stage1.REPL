"""Модульные тесты для команды rmdir (emulator.modify_commands)."""
import unittest

from emulator.commands import CommandError, execute
from emulator.modify_commands import parent_chain
from emulator.session import Session
from emulator.vfs import VfsError, parse_vfs

VFS_TEXT = "\n".join([
    "path,type,content",
    "/file.txt,file,",
    "/empty,dir,",
    "/other,dir,",
    "/a/b/c,dir,",
    "/full/keep.txt,file,",
    "/full/sub,dir,",
    "/my dir,dir,",
]) + "\n"


class RmdirTest(unittest.TestCase):
    """Общая подготовка: сеанс с тестовой VFS в корне."""

    def setUp(self):
        """Создать сеанс с тестовой VFS."""
        self.session = Session(parse_vfs(VFS_TEXT))

    def rmdir(self, *args):
        """Выполнить rmdir с аргументами args."""
        return execute("rmdir", list(args), self.session)

    def exists(self, path):
        """Проверить, что путь есть в VFS."""
        try:
            self.session.lookup(path)
        except VfsError:
            return False
        return True

    def assert_error(self, args, text):
        """Проверить, что rmdir args завершается ошибкой с текстом text."""
        with self.assertRaisesRegex(CommandError, text):
            self.rmdir(*args)


class RmdirModesTest(RmdirTest):
    """Проверка режимов rmdir."""

    def test_remove_empty_dir(self):
        """Пустой каталог удаляется, вывод пустой."""
        self.assertEqual(self.rmdir("empty"), "")
        self.assertFalse(self.exists("/empty"))
        self.assertEqual(execute("ls", [], self.session),
                         "a  file.txt  full  'my dir'  other")

    def test_absolute_relative_and_trailing_slash(self):
        """Абсолютный, относительный путь и слеш на конце."""
        self.session.cwd = ["full"]
        self.rmdir("sub/")
        self.rmdir("/other")
        self.rmdir("../my dir")
        for path in ("/full/sub", "/other", "/my dir"):
            self.assertFalse(self.exists(path))

    def test_several_dirs(self):
        """Несколько каталогов удаляются за один вызов."""
        self.rmdir("empty", "other")
        self.assertFalse(self.exists("/empty"))
        self.assertFalse(self.exists("/other"))

    def test_verbose(self):
        """-v сообщает о каждом удалённом каталоге."""
        self.assertEqual(self.rmdir("-v", "empty", "other"),
                         "rmdir: удалён каталог 'empty'\n"
                         "rmdir: удалён каталог 'other'")

    def test_parents(self):
        """-p удаляет каталог и его родителей из записи пути."""
        self.assertEqual(self.rmdir("-p", "a/b/c"), "")
        self.assertFalse(self.exists("/a"))

    def test_parents_verbose_absolute(self):
        """-pv с абсолютным путём доходит до корня, не трогая его."""
        self.assertEqual(self.rmdir("-pv", "/a/b/c/"),
                         "rmdir: удалён каталог '/a/b/c'\n"
                         "rmdir: удалён каталог '/a/b'\n"
                         "rmdir: удалён каталог '/a'")

    def test_parents_stop_at_non_empty(self):
        """-p останавливается на непустом родителе с ошибкой.

        Уже удалённые каталоги остаются удалёнными, а вывод -v
        сохраняется в ошибке.
        """
        with self.assertRaises(CommandError) as context:
            self.rmdir("-p", "-v", "full/sub")
        self.assertEqual(str(context.exception),
                         "rmdir: не удалось удалить 'full': Каталог не пуст")
        self.assertEqual(context.exception.output,
                         "rmdir: удалён каталог 'full/sub'")
        self.assertFalse(self.exists("/full/sub"))
        self.assertTrue(self.exists("/full"))

    def test_continues_after_error(self):
        """Как GNU rmdir, команда обрабатывает все операнды."""
        with self.assertRaises(CommandError) as context:
            self.rmdir("-v", "empty", "nope", "full", "other")
        self.assertEqual(str(context.exception).split("\n"), [
            "rmdir: не удалось удалить 'nope': "
            "Нет такого файла или каталога",
            "rmdir: не удалось удалить 'full': Каталог не пуст",
        ])
        self.assertEqual(context.exception.output,
                         "rmdir: удалён каталог 'empty'\n"
                         "rmdir: удалён каталог 'other'")
        self.assertFalse(self.exists("/other"))

    def test_other_commands_see_changes(self):
        """После rmdir find и vfs-tree видят изменённую VFS."""
        self.rmdir("-p", "a/b/c")
        result = execute("find", ["/", "-type", "d"], self.session)
        self.assertNotIn("/a", result.split("\n"))


class RmdirErrorsTest(RmdirTest):
    """Проверка ошибок rmdir."""

    def test_errors(self):
        """Типичные ошибки rmdir с сообщениями в стиле GNU."""
        cases = [
            ([], "rmdir: пропущен операнд"),
            (["-v"], "rmdir: пропущен операнд"),
            (["nope"], "'nope': Нет такого файла или каталога"),
            (["file.txt"], "'file.txt': Это не каталог"),
            (["file.txt/"], "'file.txt/': Это не каталог"),
            (["full"], "'full': Каталог не пуст"),
            (["/"], "'/': Устройство или ресурс занято"),
            (["."], "'.': Недопустимый аргумент"),
            (["empty/."], "'empty/.': Недопустимый аргумент"),
            (["-x", "empty"], "rmdir: неверный ключ — «x»"),
        ]
        for args, text in cases:
            with self.subTest(args=args):
                self.assert_error(args, text)
        self.assertTrue(self.exists("/empty"))

    def test_current_dir(self):
        """Текущий каталог удалить нельзя, даже если он пуст."""
        self.session.cwd = ["empty"]
        self.assert_error(["/empty"], "Устройство или ресурс занято")
        self.assertTrue(self.exists("/empty"))

    def test_cd_to_removed_previous_dir(self):
        """cd - в удалённый каталог сообщает об ошибке."""
        execute("cd", ["empty"], self.session)
        execute("cd", ["/"], self.session)
        self.rmdir("empty")
        with self.assertRaisesRegex(CommandError,
                                    "cd: /empty: Нет такого файла"):
            execute("cd", ["-"], self.session)
        self.assertEqual(self.session.cwd_path(), "/")


class ParentChainTest(unittest.TestCase):
    """Проверка построения цепочки родителей для rmdir -p."""

    def test_chains(self):
        """Родители берутся из записи пути, корень не входит."""
        cases = [
            ("a", ["a"]),
            ("a/b/c", ["a/b/c", "a/b", "a"]),
            ("a//b/", ["a//b", "a"]),
            ("/a/b", ["/a/b", "/a"]),
            ("/", ["/"]),
        ]
        for path, expected in cases:
            with self.subTest(path=path):
                self.assertEqual(parent_chain(path), expected)


if __name__ == "__main__":
    unittest.main()
