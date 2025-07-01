#!/usr/bin/env python3
"""
PyEditor v1.2 – Nano-like terminal text editor with Undo/Redo, Search, Mouse, Line Numbers.

Features:
- Ctrl+S = Save, Ctrl+Q = Quit
- Ctrl+Z = Undo, Ctrl+Y = Redo
- Ctrl+F = Search forward
- Mouse-click cursor positioning
- Line numbers with dynamic width
- “*” indicator for unsaved changes
- Colorized status bar
- Configurable keybindings
"""

import curses
import curses.ascii
import sys
import os

# Keybindings
KEY_SAVE    = curses.ascii.DC3    # Ctrl+S
KEY_QUIT    = curses.ascii.DC1    # Ctrl+Q
KEY_UNDO    = curses.ascii.SUB    # Ctrl+Z
KEY_REDO    = curses.ascii.EM     # Ctrl+Y
KEY_SEARCH  = 6                   # Ctrl+F
KEY_BACKSP  = (curses.KEY_BACKSPACE, 127)

class PyEditor:
    def __init__(self, stdscr, filename=None):
        self.stdscr = stdscr
        curses.raw()
        curses.noecho()
        stdscr.keypad(True)
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

        self.filename = filename
        self.lines = self._load_file(filename)
        self.cursor_x = 0
        self.cursor_y = 0
        self.offset_y = 0
        self.modified = False
        self.search_term = ''
        self.undo_stack = []
        self.redo_stack = []

        self._save_undo_state()
        self.run()

    def _load_file(self, fname):
        if fname and os.path.exists(fname):
            with open(fname, 'r') as f:
                return [ln.rstrip('\n') for ln in f]
        return ['']

    def run(self):
        while True:
            self.stdscr.clear()
            self._draw_text()
            self._draw_status()
            self.stdscr.refresh()
            ch = self.stdscr.getch()

            if ch == curses.KEY_MOUSE:
                self._handle_mouse()
            elif ch == KEY_QUIT:
                if self.modified and not self._confirm("Unsaved changes—quit anyway?"):
                    continue
                break
            elif ch == KEY_SAVE:
                self._save_file()
            elif ch == KEY_UNDO:
                self._undo()
            elif ch == KEY_REDO:
                self._redo()
            elif ch == KEY_SEARCH:
                self._search()
            elif ch in KEY_BACKSP:
                self._backspace()
            elif ch in (10, 13):
                self._newline()
            elif ch in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):
                self._move_cursor(ch)
            elif 32 <= ch <= 126:
                self._insert_char(chr(ch))

    def _draw_text(self):
        h, w = self.stdscr.getmaxyx()
        lineno_w = len(str(len(self.lines))) + 2
        for i in range(h - 1):
            idx = self.offset_y + i
            if idx >= len(self.lines):
                break
            line = self.lines[idx]
            num = f"{idx+1}".rjust(lineno_w - 1) + ' '
            self.stdscr.addstr(i, 0, num)
            self.stdscr.addstr(i, lineno_w, line[:w - lineno_w - 1])
        if self.search_term:
            self._highlight_search(lineno_w)
        scr_y = self.cursor_y - self.offset_y
        scr_x = self.cursor_x + lineno_w
        self.stdscr.move(scr_y, scr_x)

    def _draw_status(self):
        h, w = self.stdscr.getmaxyx()
        name = self.filename or "[No Name]"
        if self.modified:
            name += " *"
        pos = f"Ln {self.cursor_y+1}, Col {self.cursor_x+1}"
        keys = "Ctrl+S Save | Ctrl+Q Quit | Ctrl+Z Undo | Ctrl+Y Redo | Ctrl+F Search"
        status = f" {name} | {pos} | {keys} "
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(h - 1, 0, status.ljust(w - 1)[:w - 1])
        self.stdscr.attroff(curses.color_pair(1))

    def _move_cursor(self, key):
        dy = dx = 0
        if key == curses.KEY_UP:    dy = -1
        if key == curses.KEY_DOWN:  dy = 1
        if key == curses.KEY_LEFT:  dx = -1
        if key == curses.KEY_RIGHT: dx = 1
        ny = max(0, min(self.cursor_y + dy, len(self.lines) - 1))
        nx = max(0, self.cursor_x + dx)
        nx = min(nx, len(self.lines[ny]))
        self.cursor_y, self.cursor_x = ny, nx
        h, _ = self.stdscr.getmaxyx()
        if self.cursor_y < self.offset_y:
            self.offset_y = self.cursor_y
        elif self.cursor_y >= self.offset_y + h - 1:
            self.offset_y = self.cursor_y - (h - 2)

    def _insert_char(self, ch):
        self._save_undo_state()
        row = self.lines[self.cursor_y]
        self.lines[self.cursor_y] = row[:self.cursor_x] + ch + row[self.cursor_x:]
        self.cursor_x += 1
        self.modified = True

    def _backspace(self):
        if self.cursor_x == 0 and self.cursor_y == 0:
            return
        self._save_undo_state()
        if self.cursor_x > 0:
            row = self.lines[self.cursor_y]
            self.lines[self.cursor_y] = row[:self.cursor_x - 1] + row[self.cursor_x:]
            self.cursor_x -= 1
        else:
            prev = self.lines[self.cursor_y - 1]
            curr = self.lines.pop(self.cursor_y)
            self.cursor_y -= 1
            self.cursor_x = len(prev)
            self.lines[self.cursor_y] = prev + curr
        self.modified = True

    def _newline(self):
        self._save_undo_state()
        row = self.lines[self.cursor_y]
        left, right = row[:self.cursor_x], row[self.cursor_x:]
        self.lines[self.cursor_y] = left
        self.lines.insert(self.cursor_y + 1, right)
        self.cursor_y += 1
        self.cursor_x = 0
        self.modified = True

    def _save_file(self):
        if not self.filename:
            name = self._prompt("Save as:")
            if not name:
                return
            self.filename = name
        try:
            with open(self.filename, "w") as f:
                f.write("\n".join(self.lines) + "\n")
            self.modified = False
        except Exception as e:
            self._show_msg(f"Save error: {e}")

    def _handle_mouse(self):
        _, mx, my, _, _ = curses.getmouse()
        h, w = self.stdscr.getmaxyx()
        lineno_w = len(str(len(self.lines))) + 2
        if 0 <= my < h - 1 and mx >= lineno_w:
            self.cursor_y = min(self.offset_y + my, len(self.lines) - 1)
            self.cursor_x = min(mx - lineno_w, len(self.lines[self.cursor_y]))

    def _prompt(self, prompt):
        curses.echo()
        self.stdscr.addstr(0, 0, prompt + " ")
        self.stdscr.clrtoeol()
        answer = self.stdscr.getstr(0, len(prompt) + 1, 60).decode()
        curses.noecho()
        return answer.strip()

    def _confirm(self, msg):
        ans = self._prompt(f"{msg} (y/N)")
        return ans.lower().startswith('y')

    def _save_undo_state(self):
        self.undo_stack.append((self.lines.copy(), self.cursor_x, self.cursor_y))
        if len(self.undo_stack) > 100:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def _undo(self):
        if len(self.undo_stack) < 2:
            return
        state = self.undo_stack.pop()
        self.redo_stack.append(state)
        prev = self.undo_stack[-1]
        self.lines, self.cursor_x, self.cursor_y = prev[0].copy(), prev[1], prev[2]
        self.modified = True

    def _redo(self):
        if not self.redo_stack:
            return
        state = self.redo_stack.pop()
        self._save_undo_state()
        self.lines, self.cursor_x, self.cursor_y = state[0].copy(), state[1], state[2]
        self.modified = True

    def _search(self):
        term = self._prompt("Search:")
        if not term:
            self.search_term = ''
            return
        self.search_term = term
        for y in range(self.cursor_y, len(self.lines)):
            idx = self.lines[y].find(term)
            if idx >= 0:
                self.cursor_y, self.cursor_x = y, idx
                self._adjust_offset()
                return
        self._show_msg("Not found")

    def _highlight_search(self, offset):
        h, _ = self.stdscr.getmaxyx()
        for i in range(h - 1):
            y = self.offset_y + i
            if y >= len(self.lines):
                break
            row = self.lines[y]
            start = 0
            while True:
                idx = row.find(self.search_term, start)
                if idx < 0:
                    break
                self.stdscr.chgat(i, offset + idx, len(self.search_term), curses.A_REVERSE)
                start = idx + len(self.search_term)

    def _show_msg(self, msg):
        h, w = self.stdscr.getmaxyx()
        self.stdscr.addstr(h - 1, 0, msg[:w - 1].ljust(w - 1), curses.color_pair(1))
        self.stdscr.refresh()
        self.stdscr.getch()

    def _adjust_offset(self):
        h, _ = self.stdscr.getmaxyx()
        if self.cursor_y < self.offset_y:
            self.offset_y = self.cursor_y
        elif self.cursor_y >= self.offset_y + h - 1:
            self.offset_y = self.cursor_y - (h - 2)


def main(stdscr):
    fname = sys.argv[1] if len(sys.argv) > 1 else None
    PyEditor(stdscr, fname)

if __name__ == "__main__":
    curses.wrapper(main)
