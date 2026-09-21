##Графическое окно эмулятора (REPL)
import getpass
import socket
import tkinter

from emulator.commands import EXIT_RESULT, CommandError, execute
from emulator.parser import ParserError, parse_line, split_command

OUTPUT_HEIGHT = 20
OUTPUT_WIDTH = 80
INPUT_WIDTH = 80
PROMPT = "$ "
UNKNOWN_NAME = "unknown"
    
def get_username():
    ##Вернуть имя пользователя текущей ОC
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return UNKNOWN_NAME


def get_hostname():
    #Вернуть имя машины, на которой запущен эмулятор
    try:
        return socket.gethostname()
    except OSError:
        return UNKNOWN_NAME


def build_title():
    #Сформировать заголовок окна из реальных данных ОС
    return "Эмулятор - [" + get_username() + "@" + get_hostname() + "]"


class EmulatorApp:
   #Главное окно эмулятора

    def __init__(self):
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

    def print_line(self, text):
        #Добавить строку текста в область вывода
        self.output_box.insert(tkinter.END, text + "\n")
        self.output_box.see(tkinter.END)

    def print_error(self, error):
        #Вывести сообщение об ошибке
        self.print_line("ошибка: " + str(error))

    def on_enter_pressed(self, event):
        #Обработать нажатие Enter в поле ввода
        line = self.input_box.get()
        self.input_box.delete(0, tkinter.END)
        self.print_line(PROMPT + line)
        self.run_line(line)

    def run_line(self, line):
        #Разобрать и выполнить одну строку ввода
        try:
            tokens = parse_line(line)
        except ParserError as error:
            self.print_error(error)
            return

        if not tokens:
            return

        command, args = split_command(tokens)
        try:
            result = execute(command, args)
        except CommandError as error:
            self.print_error(error)
            return

        if result == EXIT_RESULT:
            self.window.destroy()
        else:
            self.print_line(result)

    def run(self):
        #Запустить цикл обработки событий окна
        self.window.mainloop()

def main():
    app = EmulatorApp()
    app.run()

if __name__ == "__main__":
    main()