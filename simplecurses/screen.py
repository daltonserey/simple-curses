import sys
import curses
import atexit
import time

screen = None

def _assert(condicao, msg):
    if condicao: return
    curses.endwin()
    print(f"erro: {msg}")
    sys.exit()


class Screen:
    
    __instance = None

    def __new__(cls, *args, **kwargs):
        if Screen.__instance:
            return Screen.__instance

        Screen.__instance = object.__new__(cls)
        self = Screen.__instance
        return self

    def __init__(self, init=True):
        self.debug = True
        self.wait_on_exit = 2
        if init:
            self.initialize()
            self.initialized = True

    def initialize(self):
        self.scr = curses.initscr()
        curses.curs_set(0)
        self.scr.scrollok(True)
        self.lins, self.cols = self.scr.getmaxyx()
        atexit.register(self.cleanup)

    def plot(self, lin, col, char="\u2588"):
        if col < self.cols and lin < self.lins:
            self.scr.addstr(lin, col, char)
            self.scr.refresh()

    def unplot(self, lin, col):
        self.plot(lin, col, " ")

    def write(self, pos, text, wrap=False, truncate=False):
        lin = pos // self.cols
        col = pos % self.cols
        lin = lin % self.lins
        self.writeat(lin, col, text, wrap=wrap, truncate=truncate)

    def writeat(self, lin, col, text, wrap=False, truncate=False):
        _assert(lin < self.lins, f"linha inválida {lin} (0 … {self.lins - 1})")
        _assert(col < self.cols, f"coluna inválida {col} (0 … {self.cols - 1})")
        _assert('\n' not in text, "caractere inválido no texto (\\n)")
        _assert('\r' not in text, "caractere inválido no texto (\\r)")

        on_screen_text = text[:self.cols - col]
        writes_on_last_column = col + len(on_screen_text) >= self.cols
        if writes_on_last_column:
            self.scr.insstr(lin, col, on_screen_text)
        else:
            self.scr.addstr(lin, col, on_screen_text)

        off_screen_text = text[self.cols - col:]
        if off_screen_text:
            _assert(truncate or wrap, f"texto muito longo (…{off_screen_text}) (use ou truncate or wrap)")
            _assert(not truncate or not wrap, f"uso simultâneo de opções opostas")
            writes_on_last_line = lin == self.lins - 1
            new_line = 0 if writes_on_last_line else lin + 1
            self.writeat(new_line, 0, off_screen_text, wrap=wrap, truncate=truncate)

        self.scr.refresh()

    def cleanup(self):
        if self.debug:
            time.sleep(self.wait_on_exit)
        curses.endwin()
        if self.debug:
            print("screen: exit")
