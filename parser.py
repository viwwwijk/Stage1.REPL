"""Разбор строки ввода эмулятора на команду и аргументы."""

QUOTE_CHARS = ("'", '"')


class ParserError(Exception):
    """Ошибка разбора строки ввода."""


def parse_line(line):
    """Разбить строку на список аргументов с учётом кавычек.

    Кавычки группируют символы в один аргумент и в результат не
    попадают. Незакрытая кавычка приводит к ParserError.
    """
    tokens = []
    current = []
    started = False
    quote = None

    for char in line:
        if quote is not None:
            if char == quote:
                quote = None
            else:
                current.append(char)
        elif char in QUOTE_CHARS:
            quote = char
            started = True
        elif char.isspace():
            if started:
                tokens.append("".join(current))
                current = []
                started = False
        else:
            current.append(char)
            started = True

    if quote is not None:
        raise ParserError("незакрытая кавычка " + quote)
    if started:
        tokens.append("".join(current))
    return tokens


def split_command(tokens):
    """Отделить имя команды от её аргументов."""
    if not tokens:
        raise ParserError("пустая строка не содержит команды")
    return tokens[0], tokens[1:]
