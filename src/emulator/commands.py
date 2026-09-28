"""Команды эмулятора.

На этапе 1 ls и cd являются заглушками, их реальная логика появится
на этапе 4. На этапе 2 добавлена служебная команда conf-dump, которая
выводит параметры эмулятора, заданные при запуске.
"""

EXIT_RESULT = "__exit__"
STUB_COMMANDS = ("ls", "cd")
CONFIG_KEYS = ("vfs-path", "script-path")


class CommandError(Exception):
    """Ошибка выполнения команды."""


def execute(command, args, config=None):
    """Выполнить команду и вернуть текст для вывода в окно.

    Для команды exit возвращается признак EXIT_RESULT. Параметр
    config используется только командой conf-dump и содержит
    параметры эмулятора, заданные при запуске.
    """
    if command == "exit":
        return execute_exit(args)
    if command == "conf-dump":
        return execute_conf_dump(args, config)
    if command in STUB_COMMANDS:
        return execute_stub(command, args)
    raise CommandError("неизвестная команда: " + command)


def execute_exit(args):
    """Обработать команду exit, аргументы для неё недопустимы."""
    if args:
        raise CommandError("exit не принимает аргументов")
    return EXIT_RESULT


def execute_stub(command, args):
    """Вывести имя команды-заглушки и её аргументы."""
    if not args:
        return command + ": аргументы отсутствуют"
    return command + ": аргументы: " + ", ".join(args)


def execute_conf_dump(args, config):
    """Вывести параметры эмулятора в формате ключ-значение.

    Значение параметра, который не был задан при запуске, выводится
    как пустая строка.
    """
    if args:
        raise CommandError("conf-dump не принимает аргументов")
    values = config or {}
    lines = (key + "=" + str(values.get(key, "") or "") for key in CONFIG_KEYS)
    return "\n".join(lines)
