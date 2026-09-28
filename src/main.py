"""Точка входа эмулятора командной оболочки."""
import sys

from emulator.config import parse_args
from emulator.gui import EmulatorApp


def main(argv=None):
    """Разобрать параметры командной строки и запустить эмулятор."""
    args = parse_args(sys.argv[1:] if argv is None else argv)
    app = EmulatorApp(vfs_path=args.vfs_path, script_path=args.script_path)
    app.run()


if __name__ == "__main__":
    main()
