"""Разбор параметров командной строки эмулятора (этап 2)."""
import argparse

VFS_PATH_HELP = "путь к физическому расположению VFS"
SCRIPT_PATH_HELP = "путь к стартовому скрипту"


def build_parser():
    """Создать парсер параметров командной строки эмулятора."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор языка оболочки ОС",
    )
    parser.add_argument(
        "--vfs-path",
        dest="vfs_path",
        default=None,
        help=VFS_PATH_HELP,
    )
    parser.add_argument(
        "--script-path",
        dest="script_path",
        default=None,
        help=SCRIPT_PATH_HELP,
    )
    return parser


def parse_args(argv):
    """Разобрать список аргументов командной строки.

    Возвращает объект с полями vfs_path и script_path. Каждое поле
    равно None, если соответствующий параметр не был задан.
    """
    return build_parser().parse_args(argv)
