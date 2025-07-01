#!/usr/bin/env python3
"""
PyEditor – A minimal nano-like text editor in Python/curses.

Features:
- Open or create a file
- Arrow keys for navigation
- Insert text, Backspace, Enter for new line
- Ctrl+S to save, Ctrl+Q to quit
"""

import curses
import sys
import os

CTRL_S = 19
CTRL_Q = 17

class PyEditor:
    def __init__(self, stdscr, filename=None):
        self.stdscr = stdscr
        curses.raw()
        curses.noecho()
        stdscr.keypad(True)
        self.filename = filename
        self.cursor_x = 0
        self.cursor_y = 0
        self.offset_y = 0
        self.lines = []
        if filename and os.path.exists(filename):
            with open(filename, 'r') as f:
                self.lines = [ln.rstrip('\n') for ln in f]
        if not self.lines:
            self.lines = ['']
        self.run()

    def run(self):
        while True:
            self.stdscr.clear()
            self.draw_text()
            self.draw_status()
            self.stdscr.refresh()
            key = self.stdscr.getch()

            if key == curses.KEY_UP:
                self.move_cursor(dy=-1)
            elif key == curses.KEY_DOWN:
                self.move_cursor(dy=1)
            elif key == curses.KEY_LEFT:
                self.move_cursor(dx=-1)
            elif key == curses.KEY_RIGHT:
                self.move_cursor(dx=1)
            elif key == CTRL_Q:
                break
            elif key == CTRL_S:
                self.save_file()
            elif key in (curses.KEY_BACKSPACE, 127):
                self.backspace()
            elif key in (10, 13):
                self.newline()
            elif 32 <= key <= 126:
                self.insert_char(chr(key))

    def draw_text(self):
        height, width = self.stdscr.getmaxyx()
        for idx in range(height - 1):
            line_index = self.offset_y + idx
            if line_index < len(self.lines):
                text = self.lines[line_index]
                self.stdscr.addstr(idx, 0, text[:width - 1])
        screen_y = self.cursor_y - self.offset_y
        self.stdscr.move(screen_y, self.cursor_x)

    def draw_status(self):
        height, width = self.stdscr.getmaxyx()
        name = self.filename or "[No Name]"
        status = f"{name} — Ln {self.cursor_y+1}, Col {self.cursor_x+1}  Ctrl-S=save  Ctrl-Q=quit"
        self.stdscr.attron(curses.A_REVERSE)
        self.stdscr.addstr(height - 1, 0, status[:width - 1].ljust(width - 1))
        self.stdscr.attroff(curses.A_REVERSE)

    def move_cursor(self, dx=0, dy=0):
        new_y = max(0, min(self.cursor_y + dy, len(self.lines) - 1))
        new_x = max(0, self.cursor_x + dx)
        line_length = len(self.lines[new_y])
        if new_x > line_length:
            new_x = line_length
        self.cursor_x, self.cursor_y = new_x, new_y

        height, _ = self.stdscr.getmaxyx()
        if self.cursor_y < self.offset_y:
            self.offset_y = self.cursor_y
        elif self.cursor_y >= self.offset_y + (height - 1):
            self.offset_y = self.cursor_y - (height - 2)

    def insert_char(self, ch):
        line = self.lines[self.cursor_y]
        self.lines[self.cursor_y] = line[:self.cursor_x] + ch + line[self.cursor_x:]
        self.move_cursor(dx=1)

    def backspace(self):
        if self.cursor_x > 0:
            line = self.lines[self.cursor_y]
            self.lines[self.cursor_y] = line[:self.cursor_x - 1] + line[self.cursor_x:]
            self.move_cursor(dx=-1)
        elif self.cursor_y > 0:
            prev_line = self.lines[self.cursor_y - 1]
            current = self.lines.pop(self.cursor_y)
            self.cursor_y -= 1
            self.cursor_x = len(prev_line)
            self.lines[self.cursor_y] = prev_line + current

    def newline(self):
        line = self.lines[self.cursor_y]
        left, right = line[:self.cursor_x], line[self.cursor_x:]
        self.lines[self.cursor_y] = left
        self.lines.insert(self.cursor_y + 1, right)
        self.cursor_y += 1
        self.cursor_x = 0

    def save_file(self):
        if not self.filename:
            curses.echo()
            self.stdscr.addstr(0, 0, "Save as: ")
            name = self.stdscr.getstr().decode('utf-8').strip()
            curses.noecho()
            self.filename = name or self.filename
        try:
            with open(self.filename, 'w') as f:
                f.write('\n'.join(self.lines) + '\n')
            self.show_message(f"Saved to {self.filename}")
        except Exception as e:
            self.show_message(f"Error saving: {e}")

    def show_message(self, msg):
        height, width = self.stdscr.getmaxyx()
        self.stdscr.attron(curses.A_REVERSE)
        self.stdscr.addstr(height - 1, 0, msg[:width - 1].ljust(width - 1))
        self.stdscr.attroff(curses.A_REVERSE)
        self.stdscr.getch()

def main(stdscr):
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    PyEditor(stdscr, filename)

if __name__ == "__main__":
    curses.wrapper(main)
