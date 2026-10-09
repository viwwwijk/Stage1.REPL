"""Модульные тесты для emulator.vfs."""
import os
import unittest

from emulator.vfs import (VfsError, count_nodes, format_path, load_vfs,
                          parse_vfs, render_tree, resolve_parts)

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), os.pardir,
                            "examples", "vfs")
HEADER = "path,type,content\n"


def example_path(name):
    """Вернуть путь к примеру VFS из каталога examples/vfs."""
    return os.path.join(EXAMPLES_DIR, name)


class ParseVfsTest(unittest.TestCase):
    """Проверка построения VFS по тексту CSV."""

    def test_header_only(self):
        """Файл из одного заголовка даёт пустой корневой каталог."""
        vfs = parse_vfs(HEADER)
        self.assertEqual(vfs.root.children, {})

    def test_file_content_is_decoded(self):
        """Содержимое файла декодируется из base64."""
        vfs = parse_vfs(HEADER + "/a.txt,file,dGV4dA==\n")
        self.assertEqual(vfs.root.children["a.txt"].content, b"text")

    def test_nested_path_creates_parents(self):
        """Недостающие родительские каталоги создаются автоматически."""
        vfs = parse_vfs(HEADER + "/a/b/c.txt,file,\n")
        node_b = vfs.root.children["a"].children["b"]
        self.assertTrue(node_b.is_dir)
        self.assertIn("c.txt", node_b.children)

    def test_repeated_directory_is_allowed(self):
        """Каталог можно объявить после вложенного в него файла."""
        vfs = parse_vfs(HEADER + "/a/b.txt,file,\n/a,dir,\n")
        self.assertEqual(count_nodes(vfs.root), (1, 1))

    def test_errors(self):
        """Неверные данные CSV приводят к VfsError."""
        bad_texts = [
            "name,kind,data\n",
            HEADER + "/a.txt,file\n",
            HEADER + "/a.txt,link,\n",
            HEADER + "/a.txt,file,not*base64\n",
            HEADER + "/a,dir,dGV4dA==\n",
            HEADER + "a.txt,file,\n",
            HEADER + "/a/../b,file,\n",
            HEADER + "/a.txt,file,\n/a.txt,file,\n",
            HEADER + "/a.txt,file,\n/a.txt/b,file,\n",
            HEADER + "/,dir,\n",
        ]
        for text in bad_texts:
            with self.subTest(text=text):
                with self.assertRaises(VfsError):
                    parse_vfs(text)

    def test_error_contains_line_number(self):
        """Сообщение об ошибке содержит номер строки CSV."""
        with self.assertRaisesRegex(VfsError, "строка 3"):
            parse_vfs(HEADER + "/a.txt,file,\n/b.txt,link,\n")


class LoadVfsTest(unittest.TestCase):
    """Проверка загрузки примеров VFS из файлов."""

    def test_minimal(self):
        """Минимальная VFS содержит один файл."""
        vfs = load_vfs(example_path("minimal.csv"))
        self.assertEqual(count_nodes(vfs.root), (0, 1))

    def test_several_files_with_binary(self):
        """Двоичный файл восстанавливается из base64 без потерь."""
        vfs = load_vfs(example_path("files.csv"))
        self.assertEqual(count_nodes(vfs.root), (0, 4))
        logo = vfs.root.children["logo.png"].content
        self.assertTrue(logo.startswith(b"\x89PNG"))

    def test_deep(self):
        """Глубокая VFS содержит не менее трёх уровней вложенности."""
        vfs = load_vfs(example_path("deep.csv"))
        reports = (vfs.root.children["home"].children["user"]
                   .children["docs"].children["reports"])
        self.assertIn("2026.txt", reports.children)

    def test_missing_file(self):
        """Отсутствующий файл VFS приводит к VfsError."""
        with self.assertRaises(VfsError):
            load_vfs(example_path("missing.csv"))

    def test_broken_examples(self):
        """Примеры повреждённых VFS не загружаются."""
        for name in ("broken_header.csv", "broken_base64.csv"):
            with self.subTest(name=name):
                with self.assertRaises(VfsError):
                    load_vfs(example_path(name))

    def test_source_file_is_not_modified(self):
        """Загрузка VFS не изменяет исходный CSV-файл."""
        path = example_path("deep.csv")
        with open(path, "rb") as vfs_file:
            before = vfs_file.read()
        load_vfs(path)
        with open(path, "rb") as vfs_file:
            self.assertEqual(vfs_file.read(), before)


class RenderTreeTest(unittest.TestCase):
    """Проверка текстового представления дерева VFS."""

    def test_render_tree(self):
        """Каталоги выводятся со слешем, файлы — с размером."""
        vfs = parse_vfs(HEADER + "/a/b.txt,file,dGV4dA==\n/c,dir,\n")
        expected = "/\n  a/\n    b.txt (4 байт)\n  c/"
        self.assertEqual(render_tree(vfs), expected)


class ResolvePartsTest(unittest.TestCase):
    """Проверка разрешения путей относительно текущего каталога."""

    def test_paths(self):
        """Абсолютные, относительные пути, . и .. разрешаются как в UNIX."""
        cwd = ["home", "user"]
        cases = [
            ("/etc", ["etc"]),
            ("docs", ["home", "user", "docs"]),
            ("./docs/", ["home", "user", "docs"]),
            ("..", ["home"]),
            ("../../..", []),
            ("/home//user/../", ["home"]),
            (".", ["home", "user"]),
        ]
        for path, expected in cases:
            with self.subTest(path=path):
                self.assertEqual(resolve_parts(cwd, path), expected)

    def test_format_path(self):
        """Корень выводится как /, вложенные пути — через /."""
        self.assertEqual(format_path([]), "/")
        self.assertEqual(format_path(["home", "user"]), "/home/user")


class VfsGetTest(unittest.TestCase):
    """Проверка поиска элемента VFS по списку имён."""

    def setUp(self):
        """Подготовить VFS с каталогом и файлом."""
        self.vfs = parse_vfs(HEADER + "/a/b.txt,file,\n")

    def test_existing(self):
        """Существующий элемент находится, корень — пустой список."""
        self.assertTrue(self.vfs.get([]).is_dir)
        self.assertFalse(self.vfs.get(["a", "b.txt"]).is_dir)

    def test_missing(self):
        """Отсутствующий элемент даёт ошибку «нет такого файла»."""
        with self.assertRaisesRegex(VfsError, "Нет такого"):
            self.vfs.get(["a", "c"])

    def test_file_in_the_middle(self):
        """Файл в середине пути даёт ошибку «это не каталог»."""
        with self.assertRaisesRegex(VfsError, "не каталог"):
            self.vfs.get(["a", "b.txt", "c"])


class VfsRemoveTest(unittest.TestCase):
    """Проверка удаления элементов VFS в памяти."""

    def setUp(self):
        """Подготовить VFS с каталогом /a и файлом /a/b.txt."""
        self.vfs = parse_vfs(HEADER + "/a/b.txt,file,\n/c,dir,\n")

    def test_remove(self):
        """Удалённый элемент больше не находится."""
        self.vfs.remove(["c"])
        self.assertNotIn("c", self.vfs.root.children)
        with self.assertRaises(VfsError):
            self.vfs.get(["c"])

    def test_remove_errors(self):
        """Корень и отсутствующий элемент удалить нельзя."""
        for parts in ([], ["nope"], ["a", "nope"], ["nope", "x"]):
            with self.subTest(parts=parts):
                with self.assertRaises(VfsError):
                    self.vfs.remove(parts)

    def test_source_file_unchanged_after_remove(self):
        """Удаление меняет только память: файл VFS остаётся прежним."""
        path = example_path("deep.csv")
        with open(path, "rb") as vfs_file:
            before = vfs_file.read()
        vfs = load_vfs(path)
        vfs.remove(["tmp"])
        with open(path, "rb") as vfs_file:
            self.assertEqual(vfs_file.read(), before)
        self.assertIn("tmp", load_vfs(path).root.children)


if __name__ == "__main__":
    unittest.main()
