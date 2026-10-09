"""Выбор и выполнение команд эмулятора.

Команды exit (этап 1), conf-dump (этап 2) и vfs-tree (этап 3) —
служебные. Команды ls, cd, find и wc (этап 4) читают VFS и описаны
в модуле emulator.fs_commands. Команда rmdir (этап 5) изменяет VFS в
памяти и описана в модуле emulator.modify_commands. Каждая команда
получает список аргументов и объект Session с VFS, параметрами и
текущим каталогом.
"""
from emulator.errors import CommandError
from emulator.fs_commands import (execute_cd, execute_find, execute_ls,
                                  execute_wc)
from emulator.modify_commands import execute_rmdir
from emulator.session import Session
from emulator.vfs import render_tree

EXIT_RESULT = "__exit__"
CONFIG_KEYS = ("vfs-path", "script-path")

__all__ = ["CONFIG_KEYS", "EXIT_RESULT", "CommandError", "execute"]


def execute(command, args, session=None):
    """Выполнить команду и вернуть текст для вывода в окно.

    Для команды exit возвращается признак EXIT_RESULT. Без session
    используется новый сеанс с пустой VFS. Неизвестная команда и
    неверные аргументы приводят к CommandError.
    """
    if session is None:
        session = Session()
    handler = COMMANDS.get(command)
    if handler is None:
        raise CommandError("неизвестная команда: " + command)
    return handler(args, session)


def execute_exit(args, session):
    """Обработать команду exit, аргументы для неё недопустимы."""
    if args:
        raise CommandError("exit не принимает аргументов")
    return EXIT_RESULT


def execute_conf_dump(args, session):
    """Вывести параметры эмулятора в формате ключ-значение.

    Значение параметра, который не был задан при запуске, выводится
    как пустая строка.
    """
    if args:
        raise CommandError("conf-dump не принимает аргументов")
    values = session.config
    lines = (key + "=" + str(values.get(key, "") or "") for key in CONFIG_KEYS)
    return "\n".join(lines)


def execute_vfs_tree(args, session):
    """Вывести дерево каталогов и файлов VFS, не изменяя её."""
    if args:
        raise CommandError("vfs-tree не принимает аргументов")
    return render_tree(session.vfs)


COMMANDS = {
    "exit": execute_exit,
    "conf-dump": execute_conf_dump,
    "vfs-tree": execute_vfs_tree,
    "ls": execute_ls,
    "cd": execute_cd,
    "find": execute_find,
    "wc": execute_wc,
    "rmdir": execute_rmdir,
}
