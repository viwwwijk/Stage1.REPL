"""Команды, изменяющие VFS (этап 5): rmdir.

Изменения выполняются только над деревом VFS в памяти, исходный
CSV-файл не изменяется. Сообщения об ошибках повторяют по смыслу
сообщения GNU coreutils на русском языке.
"""
from emulator.errors import CommandError
from emulator.fs_commands import base_name, split_options
from emulator.vfs import NOT_A_DIR, SEPARATOR, VfsError

RMDIR_OPTIONS = "pv"
CURRENT_DIR = "."
NOT_EMPTY = "Каталог не пуст"
BUSY = "Устройство или ресурс занято"
INVALID = "Недопустимый аргумент"


def parent_chain(path):
    """Вернуть путь и все его родительские пути для rmdir -p.

    Родители берутся из записи пути, как в GNU rmdir: для ``a/b/c``
    это ``a/b/c``, ``a/b``, ``a``. Корень ``/`` в цепочку не входит.
    """
    path = path.rstrip(SEPARATOR) or SEPARATOR
    chain = [path]
    while SEPARATOR in path.lstrip(SEPARATOR):
        path = path[:path.rindex(SEPARATOR)].rstrip(SEPARATOR)
        chain.append(path)
    return chain


def remove_dir(path, session):
    """Удалить пустой каталог path из VFS в памяти.

    При невозможности удаления возбуждается VfsError с причиной:
    путь не найден, это файл, каталог не пуст, путь оканчивается на
    ``.``, это корень или текущий каталог сеанса.
    """
    if base_name(path) == CURRENT_DIR:
        raise VfsError(INVALID)
    parts, node = session.lookup(path)
    if not node.is_dir:
        raise VfsError(NOT_A_DIR)
    if not parts:
        raise VfsError(BUSY)
    if node.children:
        raise VfsError(NOT_EMPTY)
    if parts == session.cwd:
        raise VfsError(BUSY)
    session.vfs.remove(parts)


def remove_chain(targets, verbose, session, output):
    """Удалить каталоги targets по порядку до первой ошибки.

    При verbose в output добавляется строка о каждом удалении.
    Возвращает текст ошибки или пустую строку, если всё удалено.
    """
    for target in targets:
        try:
            remove_dir(target, session)
        except VfsError as error:
            return ("rmdir: не удалось удалить '" + target + "': "
                    + str(error))
        if verbose:
            output.append("rmdir: удалён каталог '" + target + "'")
    return ""


def execute_rmdir(args, session):
    """rmdir [-p] [-v] КАТАЛОГ... — удалить пустые каталоги.

    Ключ -p удаляет также родительские каталоги из записи пути, пока
    они становятся пустыми; -v сообщает о каждом удалённом каталоге.
    Как и GNU rmdir, команда обрабатывает все операнды, даже если
    некоторые из них удалить не удалось; в этом случае возбуждается
    CommandError со всеми ошибками и выводом об уже удалённом.
    """
    flags, paths = split_options(args, RMDIR_OPTIONS, "rmdir")
    if not paths:
        raise CommandError("rmdir: пропущен операнд")
    output = []
    errors = []
    for path in paths:
        targets = parent_chain(path) if "p" in flags else [path]
        error = remove_chain(targets, "v" in flags, session, output)
        if error:
            errors.append(error)
    if errors:
        raise CommandError("\n".join(errors), "\n".join(output))
    return "\n".join(output)
