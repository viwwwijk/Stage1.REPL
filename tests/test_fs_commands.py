"""Модульные тесты для команд ls, cd, find и wc (emulator.fs_commands)."""
import base64
import unittest

from emulator.commands import CommandError, execute
from emulator.session import Session
from emulator.vfs import parse_vfs


def encode(text):
    """Закодировать текст UTF-8 в base64 для строки CSV."""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


VFS_TEXT = "\n".join([
    "path,type,content",
    "/a.txt,file," + encode("one two\nthree\n"),
    "/docs/b.txt,file," + encode("x\n"),
    "/docs/sub/c.md,file,",
    "/my folder/d.txt,file," + encode("hi"),
    "/empty,dir,",
]) + "\n"


class FsCommandTest(unittest.TestCase):
    """Общая подготовка: сеанс с тестовой VFS в корне."""

    def setUp(self):
        """Создать сеанс с тестовой VFS."""
        self.session = Session(parse_vfs(VFS_TEXT))

    def run_command(self, line):
        """Выполнить команду, заданную списком слов через пробел."""
        command, *args = line.split(" ")
        return execute(command, args, self.session)

    def assert_error(self, command, args, text):
        """Проверить, что команда завершается ошибкой с текстом text."""
        with self.assertRaisesRegex(CommandError, text):
            execute(command, args, self.session)


class LsTest(FsCommandTest):
    """Проверка команды ls."""

    def test_current_dir(self):
        """Без аргументов выводится текущий каталог.

        Имена с пробелами заключаются в кавычки, как в GNU ls.
        """
        self.assertEqual(self.run_command("ls"),
                         "a.txt  docs  empty  'my folder'")

    def test_relative_and_absolute(self):
        """Относительный и абсолютный пути дают одинаковый результат."""
        self.session.cwd = ["docs"]
        self.assertEqual(self.run_command("ls sub"), "c.md")
        self.assertEqual(self.run_command("ls /docs/sub"), "c.md")
        self.assertEqual(self.run_command("ls .."),
                         "a.txt  docs  empty  'my folder'")

    def test_long_format(self):
        """ls -l выводит тип, права, размер и имя."""
        self.assertEqual(self.run_command("ls -l docs"),
                         "-rw-r--r--    2 b.txt\ndrwxr-xr-x 4096 sub")

    def test_file_operand(self):
        """Для файла выводится его имя в том виде, как задано."""
        self.assertEqual(self.run_command("ls -l docs/b.txt"),
                         "-rw-r--r-- 2 docs/b.txt")

    def test_empty_dir(self):
        """Пустой каталог даёт пустой вывод."""
        self.assertEqual(self.run_command("ls empty"), "")

    def test_several_paths(self):
        """Сначала выводятся файлы, затем каталоги с заголовками."""
        result = execute("ls", ["empty", "a.txt", "my folder"],
                         self.session)
        self.assertEqual(result, "a.txt\n\nempty:\n\nmy folder:\nd.txt")

    def test_errors(self):
        """Отсутствующий путь, файл как каталог, неверный ключ."""
        self.assert_error("ls", ["nope"], "невозможно получить доступ "
                          "к 'nope': Нет такого файла или каталога")
        self.assert_error("ls", ["a.txt/x"], "Это не каталог")
        self.assert_error("ls", ["a.txt/"], "Это не каталог")
        self.assert_error("ls", ["-a"], "неверный ключ — «a»")


class CdTest(FsCommandTest):
    """Проверка команды cd."""

    def test_relative_absolute_parent(self):
        """Переходы по относительным, абсолютным путям и через ..."""
        self.assertEqual(self.run_command("cd docs/sub"), "")
        self.assertEqual(self.session.cwd_path(), "/docs/sub")
        self.run_command("cd ../..")
        self.assertEqual(self.session.cwd_path(), "/")
        self.run_command("cd ..")
        self.assertEqual(self.session.cwd_path(), "/")
        execute("cd", ["/my folder"], self.session)
        self.assertEqual(self.session.cwd_path(), "/my folder")

    def test_no_arguments_goes_to_root(self):
        """cd без аргументов переходит в корень VFS."""
        self.session.cwd = ["docs", "sub"]
        self.run_command("cd")
        self.assertEqual(self.session.cwd_path(), "/")

    def test_previous_dir(self):
        """cd - возвращает в предыдущий каталог и выводит его путь."""
        self.run_command("cd docs")
        self.run_command("cd /empty")
        self.assertEqual(self.run_command("cd -"), "/docs")
        self.assertEqual(self.run_command("cd -"), "/empty")

    def test_errors_keep_current_dir(self):
        """Ошибки cd не меняют текущий каталог."""
        self.run_command("cd docs")
        self.assert_error("cd", ["nope"],
                          "cd: nope: Нет такого файла или каталога")
        self.assert_error("cd", ["b.txt"], "cd: b.txt: Это не каталог")
        self.assert_error("cd", ["a", "b"], "слишком много аргументов")
        self.assertEqual(self.session.cwd_path(), "/docs")

    def test_previous_dir_not_set(self):
        """cd - без предыдущего каталога — ошибка."""
        self.assert_error("cd", ["-"], "предыдущий каталог не задан")


class FindTest(FsCommandTest):
    """Проверка команды find."""

    def test_all_from_current_dir(self):
        """Без аргументов выводятся все элементы от текущего каталога."""
        self.session.cwd = ["docs"]
        self.assertEqual(self.run_command("find"),
                         ".\n./b.txt\n./sub\n./sub/c.md")

    def test_path_is_kept_as_given(self):
        """Выводимые пути начинаются с пути, заданного пользователем."""
        self.assertEqual(self.run_command("find /docs/"),
                         "/docs/\n/docs/b.txt\n/docs/sub\n/docs/sub/c.md")

    def test_name_and_type(self):
        """Условия -name и -type, в том числе вместе."""
        self.assertEqual(self.run_command("find / -name *.txt"),
                         "/a.txt\n/docs/b.txt\n/my folder/d.txt")
        self.assertEqual(self.run_command("find / -type d"),
                         "/\n/docs\n/docs/sub\n/empty\n/my folder")
        self.assertEqual(self.run_command("find docs -type f -name ?.*"),
                         "docs/b.txt\ndocs/sub/c.md")

    def test_file_and_several_paths(self):
        """Путь к файлу и несколько путей подряд."""
        self.assertEqual(self.run_command("find a.txt empty"),
                         "a.txt\nempty")

    def test_no_matches(self):
        """Если ничего не найдено, вывод пустой."""
        self.assertEqual(self.run_command("find -name *.png"), "")

    def test_errors(self):
        """Ошибки путей и выражения find."""
        self.assert_error("find", ["nope"], "find: 'nope': Нет такого")
        self.assert_error("find", ["-size", "1"], "неизвестный предикат")
        self.assert_error("find", ["-name"], "отсутствует аргумент")
        self.assert_error("find", ["-type", "x"], "неизвестный аргумент")
        self.assert_error("find", ["-type", "f", "docs"],
                          "пути должны предшествовать выражению")


class WcTest(FsCommandTest):
    """Проверка команды wc."""

    def test_all_counters(self):
        """Без ключей выводятся строки, слова и байты."""
        self.assertEqual(self.run_command("wc a.txt"), " 2  3 14 a.txt")

    def test_selected_counters(self):
        """Ключи выбирают счётчики, порядок вывода всегда l, w, c."""
        self.assertEqual(self.run_command("wc -l a.txt"), "2 a.txt")
        self.assertEqual(self.run_command("wc -cw a.txt"), " 3 14 a.txt")

    def test_several_files_total(self):
        """Для нескольких файлов добавляется строка «итого»."""
        result = execute("wc", ["a.txt", "/docs/b.txt", "my folder/d.txt"],
                         self.session)
        self.assertEqual(result, "\n".join([
            " 2  3 14 a.txt",
            " 1  1  2 /docs/b.txt",
            " 0  1  2 my folder/d.txt",
            " 3  5 18 итого",
        ]))

    def test_empty_file(self):
        """Пустой файл даёт нулевые счётчики."""
        self.assertEqual(self.run_command("wc docs/sub/c.md"),
                         "0 0 0 docs/sub/c.md")

    def test_errors(self):
        """Ошибки wc: нет файлов, нет файла, каталог, неверный ключ."""
        self.assert_error("wc", [], "не указаны файлы")
        self.assert_error("wc", ["-l"], "не указаны файлы")
        self.assert_error("wc", ["nope"], "wc: nope: Нет такого")
        self.assert_error("wc", ["docs"], "wc: docs: Это каталог")
        self.assert_error("wc", ["-x", "a.txt"], "неверный ключ — «x»")


if __name__ == "__main__":
    unittest.main()
