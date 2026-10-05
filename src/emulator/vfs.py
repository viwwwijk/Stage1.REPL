"""Виртуальная файловая система (VFS), которая хранится только в памяти.

Источником VFS служит CSV-файл с заголовком ``path,type,content``.
Каждая строка описывает один элемент: абсолютный путь внутри VFS, тип
(``dir`` или ``file``) и содержимое файла в кодировке base64. Вложенность
задаётся путём: элемент ``/home/user/a.txt`` лежит в каталоге
``/home/user``. Недостающие родительские каталоги создаются
автоматически. Исходный файл только читается и никогда не изменяется.
"""
import base64
import binascii
import csv
import io

CSV_HEADER = ["path", "type", "content"]
TYPE_DIR = "dir"
TYPE_FILE = "file"
SEPARATOR = "/"
INDENT = "  "
FORBIDDEN_NAMES = (".", "..")
FIRST_DATA_LINE = 2


class VfsError(Exception):
    """Ошибка загрузки или разбора VFS."""


class VfsNode:
    """Элемент VFS: каталог или файл."""

    def __init__(self, name, is_dir, content=b""):
        """Создать элемент с именем name, каталог или файл."""
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.children = {}


class Vfs:
    """Дерево VFS с корневым каталогом ``/``."""

    def __init__(self):
        """Создать пустую VFS из одного корневого каталога."""
        self.root = VfsNode("", True)

    def add(self, path, is_dir, content=b""):
        """Добавить элемент по абсолютному пути.

        Повторное объявление каталога допускается и ничего не меняет,
        любое другое повторение пути считается ошибкой.
        """
        parts = split_path(path)
        if not parts:
            raise VfsError("корневой каталог нельзя объявить повторно")
        parent = self.make_dirs(parts[:-1], path)
        name = parts[-1]
        existing = parent.children.get(name)
        if existing is not None:
            if existing.is_dir and is_dir:
                return
            raise VfsError("путь встречается повторно: " + path)
        parent.children[name] = VfsNode(name, is_dir, content)

    def make_dirs(self, parts, path):
        """Вернуть каталог по списку имён, создавая недостающие."""
        node = self.root
        for part in parts:
            child = node.children.get(part)
            if child is None:
                child = VfsNode(part, True)
                node.children[part] = child
            elif not child.is_dir:
                raise VfsError("файл используется как каталог: " + path)
            node = child
        return node


def split_path(path):
    """Разбить абсолютный путь VFS на список имён."""
    if not path.startswith(SEPARATOR):
        raise VfsError("путь должен быть абсолютным: " + path)
    parts = [part for part in path.split(SEPARATOR) if part]
    for part in parts:
        if part in FORBIDDEN_NAMES:
            raise VfsError("недопустимое имя в пути: " + path)
    return parts


def decode_content(text, line_number):
    """Декодировать содержимое файла из base64."""
    try:
        return base64.b64decode(text, validate=True)
    except (binascii.Error, ValueError):
        raise VfsError(line_prefix(line_number) + "неверные данные base64")


def line_prefix(line_number):
    """Вернуть префикс сообщения об ошибке с номером строки CSV."""
    return "строка " + str(line_number) + ": "


def add_row(vfs, row, line_number):
    """Добавить в VFS элемент, описанный строкой CSV."""
    if len(row) != len(CSV_HEADER):
        raise VfsError(line_prefix(line_number)
                       + "ожидается полей: " + str(len(CSV_HEADER)))
    path, kind, content = row
    if kind == TYPE_DIR:
        if content:
            raise VfsError(line_prefix(line_number)
                           + "у каталога не может быть содержимого")
        is_dir, data = True, b""
    elif kind == TYPE_FILE:
        is_dir, data = False, decode_content(content, line_number)
    else:
        raise VfsError(line_prefix(line_number)
                       + "неизвестный тип элемента: " + kind)
    try:
        vfs.add(path, is_dir, data)
    except VfsError as error:
        raise VfsError(line_prefix(line_number) + str(error))


def parse_vfs(text):
    """Построить VFS в памяти по тексту CSV-файла."""
    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader, None)
        if header != CSV_HEADER:
            raise VfsError("неверный формат: ожидается заголовок "
                           + ",".join(CSV_HEADER))
        vfs = Vfs()
        for line_number, row in enumerate(reader, FIRST_DATA_LINE):
            if row:
                add_row(vfs, row, line_number)
    except csv.Error as error:
        raise VfsError("неверный формат CSV: " + str(error))
    return vfs


def load_vfs(path):
    """Прочитать CSV-файл и построить по нему VFS в памяти."""
    try:
        with open(path, "r", encoding="utf-8", newline="") as vfs_file:
            text = vfs_file.read()
    except OSError as error:
        raise VfsError("не удалось открыть VFS: " + str(error))
    except UnicodeDecodeError:
        raise VfsError("неверный формат: файл VFS не в кодировке UTF-8")
    return parse_vfs(text)


def count_nodes(node):
    """Вернуть число каталогов и файлов внутри каталога node."""
    dirs = files = 0
    for child in node.children.values():
        if child.is_dir:
            sub_dirs, sub_files = count_nodes(child)
            dirs += 1 + sub_dirs
            files += sub_files
        else:
            files += 1
    return dirs, files


def render_tree(vfs):
    """Вернуть текстовое представление дерева VFS."""
    lines = [SEPARATOR]
    append_children(vfs.root, 1, lines)
    return "\n".join(lines)


def append_children(node, depth, lines):
    """Добавить в lines строки для содержимого каталога node."""
    for name in sorted(node.children):
        child = node.children[name]
        indent = INDENT * depth
        if child.is_dir:
            lines.append(indent + name + SEPARATOR)
            append_children(child, depth + 1, lines)
        else:
            size = str(len(child.content))
            lines.append(indent + name + " (" + size + " байт)")
