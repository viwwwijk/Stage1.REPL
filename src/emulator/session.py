"""Состояние сеанса эмулятора: VFS, параметры и текущий каталог."""
from emulator.vfs import (NOT_A_DIR, SEPARATOR, Vfs, VfsError,
                          format_path, resolve_parts)


class Session:
    """Сеанс работы с эмулятором.

    Хранит загруженную VFS, параметры запуска, текущий каталог и
    предыдущий каталог (для ``cd -``). Каталоги задаются списками имён
    от корня VFS.
    """

    def __init__(self, vfs=None, config=None):
        """Создать сеанс; по умолчанию VFS пустая, каталог — корень."""
        self.vfs = vfs if vfs is not None else Vfs()
        self.config = config if config is not None else {}
        self.cwd = []
        self.prev_cwd = None

    def cwd_path(self):
        """Вернуть абсолютный путь текущего каталога."""
        return format_path(self.cwd)

    def lookup(self, path):
        """Найти элемент VFS по пути относительно текущего каталога.

        Возвращает пару (список имён от корня, элемент). Путь со
        слешем на конце должен указывать на каталог. При ошибке
        возбуждается VfsError.
        """
        parts = resolve_parts(self.cwd, path)
        node = self.vfs.get(parts)
        if path.endswith(SEPARATOR) and not node.is_dir:
            raise VfsError(NOT_A_DIR)
        return parts, node

    def change_dir(self, parts):
        """Сделать текущим каталог parts, запомнив предыдущий."""
        self.prev_cwd = self.cwd
        self.cwd = list(parts)
