"""Команды работы с VFS: ls, cd, find, wc (этап 4).

Команды только читают VFS, всё состояние сеанса (текущий каталог)
хранится в объекте Session. Сообщения об ошибках повторяют по смыслу
сообщения GNU coreutils на русском языке.
"""
import fnmatch

from emulator.errors import CommandError
from emulator.vfs import SEPARATOR, VfsError, format_path

OPTION_PREFIX = "-"
END_OF_OPTIONS = "--"
CURRENT_DIR = "."
PREVIOUS_DIR = "-"
DIR_SIZE = 4096
DIR_MODE = "drwxr-xr-x"
FILE_MODE = "-rw-r--r--"
NAME_SEPARATOR = "  "
WC_COUNTERS = "lwc"
WC_TOTAL = "итого"
FIND_TYPES = {"f": False, "d": True}
FIND_PREDICATES = ("-name", "-type")


def split_options(args, allowed, command):
    """Разделить аргументы на набор ключей и список операндов.

    Ключи — аргументы вида ``-x`` или ``-xy``, их можно указывать в
    любом месте. После ``--`` все аргументы считаются операндами.
    Недопустимый ключ приводит к CommandError.
    """
    flags = set()
    operands = []
    options_ended = False
    for arg in args:
        if options_ended or not is_option(arg):
            operands.append(arg)
        elif arg == END_OF_OPTIONS:
            options_ended = True
        else:
            for flag in arg[1:]:
                if flag not in allowed:
                    raise CommandError(command + ": неверный ключ — «"
                                       + flag + "»")
                flags.add(flag)
    return flags, operands


def is_option(arg):
    """Проверить, что аргумент выглядит как ключ (``-x``, но не ``-``)."""
    return arg.startswith(OPTION_PREFIX) and arg != OPTION_PREFIX


def quote_name(name):
    """Заключить имя с пробелами в одинарные кавычки, как GNU ls."""
    if " " in name:
        return "'" + name + "'"
    return name


def node_size(node):
    """Вернуть размер элемента для ls -l: байты файла или 4096."""
    return DIR_SIZE if node.is_dir else len(node.content)


def format_entries(entries, long_format):
    """Отформатировать пары (имя, элемент) для вывода ls."""
    if not long_format:
        return NAME_SEPARATOR.join(quote_name(name) for name, _ in entries)
    width = max((len(str(node_size(node))) for _, node in entries),
                default=0)
    lines = []
    for name, node in entries:
        mode = DIR_MODE if node.is_dir else FILE_MODE
        size = str(node_size(node)).rjust(width)
        lines.append(mode + " " + size + " " + quote_name(name))
    return "\n".join(lines)


def list_dir(node):
    """Вернуть отсортированные пары (имя, элемент) содержимого каталога."""
    return sorted(node.children.items())


def lookup_all(paths, session, error_prefix):
    """Найти элементы VFS для всех путей и вернуть пары (путь, элемент).

    При первом ненайденном пути возбуждается CommandError: текст
    ошибки строится функцией error_prefix(путь) и причиной из VFS.
    """
    targets = []
    for path in paths:
        try:
            targets.append((path, session.lookup(path)[1]))
        except VfsError as error:
            raise CommandError(error_prefix(path) + str(error))
    return targets


def ls_access_error(path):
    """Начало сообщения ls о недоступном пути."""
    return "ls: невозможно получить доступ к '" + path + "': "


def execute_ls(args, session):
    """ls [-l] [ПУТЬ...] — вывести содержимое каталогов или имена файлов.

    Без путей выводится текущий каталог. Сначала выводятся указанные
    файлы, затем каталоги; при нескольких путях содержимое каждого
    каталога предваряется заголовком ``путь:``.
    """
    flags, paths = split_options(args, "l", "ls")
    long_format = "l" in flags
    targets = lookup_all(paths or [CURRENT_DIR], session, ls_access_error)
    files = [(path, node) for path, node in targets if not node.is_dir]
    blocks = [format_entries(files, long_format)] if files else []
    for path, node in targets:
        if node.is_dir:
            blocks.append(format_dir_block(path, node, long_format,
                                           bool(targets[1:])))
    return "\n\n".join(blocks)


def format_dir_block(path, node, long_format, with_header):
    """Отформатировать содержимое каталога для ls.

    При with_header перед содержимым выводится заголовок ``путь:``.
    """
    listing = format_entries(list_dir(node), long_format)
    if not with_header:
        return listing
    if not listing:
        return path + ":"
    return path + ":\n" + listing


def execute_cd(args, session):
    """cd [ПУТЬ | -] — сменить текущий каталог.

    Без аргументов выполняется переход в корень VFS (в VFS нет
    домашнего каталога). ``cd -`` возвращает в предыдущий каталог и,
    как в bash, выводит его путь.
    """
    if args[1:]:
        raise CommandError("cd: слишком много аргументов")
    path = args[0] if args else SEPARATOR
    if path == PREVIOUS_DIR:
        return change_to_previous(session)
    try:
        parts, node = session.lookup(path)
    except VfsError as error:
        raise CommandError("cd: " + path + ": " + str(error))
    if not node.is_dir:
        raise CommandError("cd: " + path + ": Это не каталог")
    session.change_dir(parts)
    return ""


def change_to_previous(session):
    """Выполнить ``cd -``: вернуться в предыдущий каталог.

    Предыдущий каталог мог быть удалён (rmdir), поэтому его наличие
    проверяется заново. Возвращает путь нового текущего каталога.
    """
    if session.prev_cwd is None:
        raise CommandError("cd: предыдущий каталог не задан")
    previous = format_path(session.prev_cwd)
    try:
        session.vfs.get(session.prev_cwd)
    except VfsError as error:
        raise CommandError("cd: " + previous + ": " + str(error))
    session.change_dir(session.prev_cwd)
    return previous


def parse_find_args(args):
    """Разделить аргументы find на пути и список условий.

    Пути идут первыми, затем выражение из условий ``-name ШАБЛОН`` и
    ``-type f|d``. Возвращает пару (пути, [(условие, значение)]).
    """
    split_at = len(args)
    for index, arg in enumerate(args):
        if arg.startswith(OPTION_PREFIX):
            split_at = index
            break
    paths, expression = args[:split_at], args[split_at:]
    predicates = []
    while expression:
        predicate, value = take_predicate(expression)
        predicates.append((predicate, value))
        expression = expression[2:]
    return paths, predicates


def take_predicate(expression):
    """Проверить первое условие выражения find и вернуть его пару."""
    predicate = expression[0]
    if not predicate.startswith(OPTION_PREFIX):
        raise CommandError("find: пути должны предшествовать выражению: "
                           + predicate)
    if predicate not in FIND_PREDICATES:
        raise CommandError("find: неизвестный предикат «" + predicate + "»")
    if not expression[1:]:
        raise CommandError("find: отсутствует аргумент у «"
                           + predicate + "»")
    value = expression[1]
    if predicate == "-type" and value not in FIND_TYPES:
        raise CommandError("find: неизвестный аргумент у -type: " + value)
    return predicate, value


def find_matches(name, node, predicates):
    """Проверить, что элемент удовлетворяет всем условиям find."""
    for predicate, value in predicates:
        if predicate == "-name" and not fnmatch.fnmatchcase(name, value):
            return False
        if predicate == "-type" and node.is_dir != FIND_TYPES[value]:
            return False
    return True


def base_name(path):
    """Вернуть последнее имя пути, как его видит find для -name."""
    stripped = path.rstrip(SEPARATOR)
    if not stripped:
        return SEPARATOR
    return stripped.split(SEPARATOR)[-1]


def join_label(label, name):
    """Присоединить имя к выводимому пути, не удваивая слеш."""
    if label.endswith(SEPARATOR):
        return label + name
    return label + SEPARATOR + name


def walk(label, name, node, predicates, results):
    """Обойти поддерево в глубину, собирая подходящие пути."""
    if find_matches(name, node, predicates):
        results.append(label)
    if node.is_dir:
        for child_name, child in list_dir(node):
            walk(join_label(label, child_name), child_name, child,
                 predicates, results)


def execute_find(args, session):
    """find [ПУТЬ...] [-name ШАБЛОН] [-type f|d] — найти элементы VFS.

    Без путей поиск идёт от текущего каталога ``.``. Пути выводятся
    в том виде, в каком заданы, с добавлением вложенных имён.
    Шаблон -name поддерживает ``*``, ``?`` и ``[...]``.
    """
    paths, predicates = parse_find_args(args)
    results = []
    for path, node in lookup_all(paths or [CURRENT_DIR], session,
                                 find_error):
        walk(path, base_name(path), node, predicates, results)
    return "\n".join(results)


def find_error(path):
    """Начало сообщения find о недоступном пути."""
    return "find: '" + path + "': "


def count_content(content):
    """Посчитать строки, слова и байты содержимого файла."""
    return {
        "l": content.count(b"\n"),
        "w": len(content.split()),
        "c": len(content),
    }


def execute_wc(args, session):
    """wc [-l] [-w] [-c] ФАЙЛ... — посчитать строки, слова и байты.

    Без ключей выводятся все три счётчика. При нескольких файлах
    добавляется строка «итого».
    """
    flags, paths = split_options(args, WC_COUNTERS, "wc")
    if not paths:
        raise CommandError("wc: не указаны файлы "
                           "(чтение стандартного ввода не поддерживается)")
    selected = [key for key in WC_COUNTERS if key in flags or not flags]
    rows = []
    for path, node in lookup_all(paths, session, wc_error):
        if node.is_dir:
            raise CommandError(wc_error(path) + "Это каталог")
        counts = count_content(node.content)
        rows.append(([counts[key] for key in selected], path))
    if rows[1:]:
        rows.append((sum_columns(rows), WC_TOTAL))
    return format_wc(rows)


def wc_error(path):
    """Начало сообщения wc об ошибке для пути."""
    return "wc: " + path + ": "


def sum_columns(rows):
    """Сложить счётчики всех строк wc по столбцам."""
    return [sum(column) for column in zip(*(values for values, _ in rows))]


def format_wc(rows):
    """Выровнять счётчики wc по правому краю общей ширины."""
    width = max(len(str(value)) for values, _ in rows for value in values)
    lines = []
    for values, name in rows:
        numbers = " ".join(str(value).rjust(width) for value in values)
        lines.append(numbers + " " + name)
    return "\n".join(lines)
