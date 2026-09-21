"""Команды эмулятора. На этапе 1 ls и cd являются заглушками."""

EXIT_RESULT = "__exit__"
STUB_COMMANDS = ("ls", "cd")


class CommandError(Exception):
    """Ошибка выполнения команды."""


def execute(command, args):
    """Выполнить команду и вернуть текст для вывода в окно.

    Для команды exit возвращается признак EXIT_RESULT.
    """
    if command == "exit":
        return execute_exit(args)
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
