"""Графическое окно эмулятора (REPL) с конфигурацией и VFS."""
import getpass
import socket
import tkinter

from emulator.commands import EXIT_RESULT, CommandError, execute
from emulator.parser import ParserError, parse_line, split_command
from emulator.vfs import Vfs, VfsError, count_nodes, load_vfs

OUTPUT_HEIGHT = 20
OUTPUT_WIDTH = 80
INPUT_WIDTH = 80
PROMPT = "$ "
UNKNOWN_NAME = "unknown"


def get_username():
    """Вернуть имя пользователя текущей ОС."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return UNKNOWN_NAME


def get_hostname():
    """Вернуть имя машины, на которой запущен эмулятор."""
    try:
        return socket.gethostname()
    except OSError:
        return UNKNOWN_NAME


def build_title():
    """Сформировать заголовок окна из реальных данных ОС."""
    return "Эмулятор - [" + get_username() + "@" + get_hostname() + "]"


class EmulatorApp:
    """Главное окно эмулятора."""

    def __init__(self, vfs_path=None, script_path=None):
        """Создать окно, загрузить VFS и выполнить стартовый скрипт."""
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.config = {
            "vfs-path": vfs_path or "",
            "script-path": script_path or "",
        }
        self.closed = False
        self.vfs = Vfs()

        self.window = tkinter.Tk()
        self.window.title(build_title())

        self.output_box = tkinter.Text(self.window,
                                       height=OUTPUT_HEIGHT,
                                       width=OUTPUT_WIDTH)
        self.output_box.pack()

        self.input_box = tkinter.Entry(self.window, width=INPUT_WIDTH)
        self.input_box.pack()
        self.input_box.bind("<Return>", self.on_enter_pressed)
        self.input_box.focus()

        self.print_debug_config()

        if self.init_vfs() and self.script_path:
            self.run_script(self.script_path)

    def print_line(self, text):
        """Добавить строку текста в область вывода."""
        self.output_box.insert(tkinter.END, text + "\n")
        self.output_box.see(tkinter.END)

    def print_error(self, error):
        """Вывести сообщение об ошибке."""
        self.print_line("ошибка: " + str(error))

    def print_debug_config(self):
        """Вывести параметры эмулятора при запуске (отладочный вывод).

        Каждый параметр печатается в формате ключ-значение. Для
        незаданного параметра значение — пустая строка.
        """
        for key, value in self.config.items():
            self.print_line(key + "=" + value)

    def init_vfs(self):
        """Загрузить VFS из файла, заданного параметром --vfs-path.

        Без параметра используется пустая VFS из одного корневого
        каталога. Возвращает False, если загрузить VFS не удалось:
        это считается первой ошибкой, и стартовый скрипт не
        выполняется.
        """
        if not self.vfs_path:
            self.print_line("VFS не задана, используется пустая VFS")
            return True
        try:
            self.vfs = load_vfs(self.vfs_path)
        except VfsError as error:
            self.print_error(error)
            return False
        dirs, files = count_nodes(self.vfs.root)
        self.print_line("VFS загружена: каталогов " + str(dirs)
                        + ", файлов " + str(files))
        return True

    def on_enter_pressed(self, event):
        """Обработать нажатие Enter в поле ввода."""
        line = self.input_box.get()
        self.input_box.delete(0, tkinter.END)
        self.print_line(PROMPT + line)
        self.run_line(line)

    def run_line(self, line):
        """Разобрать и выполнить одну строку ввода.

        Возвращает True, если строка выполнена без ошибок (пустая
        строка также считается успехом), и False, если при разборе
        или выполнении произошла ошибка. Команда exit закрывает окно.
        """
        try:
            tokens = parse_line(line)
        except ParserError as error:
            self.print_error(error)
            return False

        if not tokens:
            return True

        command, args = split_command(tokens)
        try:
            result = execute(command, args, self.config, self.vfs)
        except CommandError as error:
            self.print_error(error)
            return False

        if result == EXIT_RESULT:
            self.closed = True
            self.window.destroy()
        else:
            self.print_line(result)
        return True

    def run_script(self, path):
        """Выполнить стартовый скрипт построчно.

        Каждая строка скрипта выводится в область вывода вместе с
        приглашением `$`, как ввод, так и вывод показываются на
        экране, имитируя диалог с пользователем. Выполнение
        останавливается на первой ошибке разбора или команды.
        """
        try:
            with open(path, "r", encoding="utf-8") as script_file:
                lines = script_file.readlines()
        except OSError as error:
            self.print_error(
                "не удалось открыть стартовый скрипт: " + str(error))
            return

        for raw_line in lines:
            line = raw_line.rstrip("\n")
            self.print_line(PROMPT + line)
            if not self.run_line(line):
                return
            if self.closed:
                return

    def run(self):
        """Запустить цикл обработки событий окна."""
        if not self.closed:
            self.window.mainloop()
