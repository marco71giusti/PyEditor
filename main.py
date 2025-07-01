#!/usr/bin/env python3
"""
PyEditor v1.3 – Nano-like editor with JSON config, Pygments syntax highlight,
Find/Replace (regex), Undo/Redo, Search, Mouse, Line Numbers, Color theme.
"""

import curses, curses.ascii, sys, os, json, pathlib, re
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

# 1) Load JSON config
CFG_PATH = pathlib.Path.home()/'.pyeditor.json'
if CFG_PATH.exists():
    with open(CFG_PATH) as f:
        CONFIG = json.load(f)
else:
    CONFIG = {
      "keybindings": {"save":19,"quit":17,"undo":26,"redo":25,"search":6,"replace":18},
      "syntax": {"lexer":"python"},
      "theme": {"status_bg":"cyan","status_fg":"black",
                "keyword":"yellow","string":"green","comment":"blue"}
    }

# 2) Map keycodes
KEY_SAVE    = CONFIG["keybindings"]["save"]
KEY_QUIT    = CONFIG["keybindings"]["quit"]
KEY_UNDO    = CONFIG["keybindings"]["undo"]
KEY_REDO    = CONFIG["keybindings"]["redo"]
KEY_SEARCH  = CONFIG["keybindings"]["search"]
KEY_REPLACE = CONFIG["keybindings"]["replace"]
KEY_BACKSP  = (curses.KEY_BACKSPACE, 127)

# 3) Color name → curses constant
COLORS = {n:getattr(curses, 'COLOR_'+n.upper()) for n in
          ("black red green yellow blue magenta cyan white").split()}

class PyEditor:
    def __init__(self, stdscr, filename=None):
        self.stdscr = stdscr
        curses.raw(); curses.noecho(); stdscr.keypad(True)
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
        curses.start_color(); curses.use_default_colors()

        # 4) Init color pairs from theme
        theme = CONFIG["theme"]
        fg = COLORS.get(theme["status_fg"], curses.COLOR_WHITE)
        bg = COLORS.get(theme["status_bg"], curses.COLOR_BLUE)
        curses.init_pair(1, fg, bg)      # status bar
        curses.init_pair(2, COLORS[theme["keyword"]], -1)
        curses.init_pair(3, COLORS[theme["string"]],  -1)
        curses.init_pair(4, COLORS[theme["comment"]], -1)

        # 5) Syntax lexer
        self.lexer = get_lexer_by_name(CONFIG["syntax"]["lexer"])
        self.token_map = {
          Token.Keyword:    curses.color_pair(2),
          Token.String:     curses.color_pair(3),
          Token.Comment:    curses.color_pair(4),
        }

        # Buffer state
        self.filename = filename
        self.lines = self._load_file(filename)
        self.cx = self.cy = self.offset = 0
        self.modified = False
        self.search_term = ''
        self.undo_stack = []; self.redo_stack = []
        self._save_undo_state()
        self.run()

    def _load_file(self, fname):
        if fname and os.path.exists(fname):
            return [ln.rstrip('\n') for ln in open(fname)]
        return ['']

    def run(self):
        while True:
            self.stdscr.clear()
            self._draw()
            self.stdscr.refresh()
            ch = self.stdscr.getch()
            if ch==curses.KEY_MOUSE:       self._handle_mouse()
            elif ch==KEY_QUIT:             return
            elif ch==KEY_SAVE:             self._save_file()
            elif ch==KEY_UNDO:             self._undo()
            elif ch==KEY_REDO:             self._redo()
            elif ch==KEY_SEARCH:           self._search()
            elif ch==KEY_REPLACE:          self._replace()
            elif ch in KEY_BACKSP:         self._backspace()
            elif ch in (10,13):            self._newline()
            elif ch in (curses.KEY_UP, curses.KEY_DOWN,
                        curses.KEY_LEFT, curses.KEY_RIGHT):
                                            self._move(ch)
            elif 32<=ch<=126:              self._insert(chr(ch))

    def _draw(self):
        h,w = self.stdscr.getmaxyx()
        numw= len(str(len(self.lines)))+2
        for i in range(h-1):
            y = self.offset + i
            if y>=len(self.lines): break
            row = self.lines[y]
            # line number
            self.stdscr.addstr(i,0,f"{y+1}".rjust(numw-1)+" ")
            # syntax-color
            x = numw
            for ttype,tok in lex(row, self.lexer):
                col = self.token_map.get(ttype, curses.A_NORMAL)
                self.stdscr.addstr(i, x, tok, col)
                x += len(tok)
        # highlight search hits
        if self.search_term:
            for i in range(h-1):
                y = self.offset+i
                if y>=len(self.lines): break
                line = self.lines[y]
                col=numw
                idx=0
                while True:
                    idx=line.find(self.search_term, idx)
                    if idx<0: break
                    self.stdscr.chgat(i, col+idx, len(self.search_term), curses.A_REVERSE)
                    idx+=len(self.search_term)
        # status bar
        name = self.filename or "[No Name]"
        if self.modified: name+=" *"
        pos = f"Ln {self.cy+1},Col {self.cx+1}"
        keys= "S:Ctrl+S  Q:Ctrl+Q  Z:Ctrl+Z  Y:Ctrl+Y  F:Ctrl+F  R:Ctrl+R"
        status=f" {name} | {pos} | {keys} "
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(h-1,0,status.ljust(w-1)[:w-1])
        self.stdscr.attroff(curses.color_pair(1))
        # move cursor
        curs_y = self.cy - self.offset
        self.stdscr.move(curs_y, self.cx + numw)

    def _move(self, k):
        dy=dx=0
        if k==curses.KEY_UP:    dy=-1
        if k==curses.KEY_DOWN:  dy=1
        if k==curses.KEY_LEFT:  dx=-1
        if k==curses.KEY_RIGHT: dx=1
        ny = max(0, min(self.cy+dy, len(self.lines)-1))
        nx = max(0, min(self.cx+dx, len(self.lines[ny])))
        self.cy, self.cx = ny, nx
        h,_ = self.stdscr.getmaxyx()
        if self.cy<self.offset: self.offset=self.cy
        if self.cy>=self.offset+h-1: self.offset=self.cy-(h-2)

    def _insert(self, ch):
        self._save_undo_state()
        row = self.lines[self.cy]
        self.lines[self.cy] = row[:self.cx]+ch+row[self.cx:]
        self.cx+=1; self.modified=True

    def _backspace(self):
        if self.cx==0 and self.cy==0: return
        self._save_undo_state()
        if self.cx>0:
            row=self.lines[self.cy]
            self.lines[self.cy]=row[:self.cx-1]+row[self.cx:]
            self.cx-=1
        else:
            prev=self.lines.pop(self.cy)
            self.cy-=1
            self.cx=len(self.lines[self.cy])
            self.lines[self.cy]+=prev
        self.modified=True

    def _newline(self):
        self._save_undo_state()
        row=self.lines[self.cy]
        left,right=row[:self.cx],row[self.cx:]
        self.lines[self.cy]=left
        self.lines.insert(self.cy+1,right)
        self.cy+=1; self.cx=0; self.modified=True

    def _save_file(self):
        if not self.filename:
            name=self._prompt("Save as:")
            if not name: return
            self.filename=name
        try:
            with open(self.filename,'w') as f:
                f.write('\n'.join(self.lines)+'\n')
            self.modified=False
        except Exception as e:
            self._show(f"Save error: {e}")

    def _handle_mouse(self):
        _,mx,my,_,_=curses.getmouse()
        h,_=self.stdscr.getmaxyx()
        numw=len(str(len(self.lines)))+2
        if 0<=my<h-1 and mx>=numw:
            self.cy=min(self.offset+my,len(self.lines)-1)
            self.cx=min(mx-numw,len(self.lines[self.cy]))

    def _prompt(self,msg):
        curses.echo()
        self.stdscr.addstr(0,0,msg+' ')
        self.stdscr.clrtoeol()
        ans=self.stdscr.getstr(0,len(msg)+1,60).decode()
        curses.noecho()
        return ans.strip()

    def _undo(self):
        if len(self.undo_stack)<2: return
        state=self.undo_stack.pop(); self.redo_stack.append(state)
        prev=self.undo_stack[-1]
        self.lines,self.cx,self.cy=prev[0].copy(),prev[1],prev[2]
        self.modified=True

    def _redo(self):
        if not self.redo_stack: return
        state=self.redo_stack.pop()
        self._save_undo_state()
        self.lines,self.cx,self.cy=state[0].copy(),state[1],state[2]
        self.modified=True

    def _search(self):
        term=self._prompt("Search:")
        if not term: return
        self.search_term=term
        for y in range(self.cy,len(self.lines)):
            idx=self.lines[y].find(term)
            if idx>=0:
                self.cy, self.cx=y, idx
                break

    def _replace(self):
        pattern=self._prompt("Find regex:")
        if not pattern: return
        repl=self._prompt("Replace with:")
        try:
            rx=re.compile(pattern)
        except re.error as e:
            return self._show(f"Regex error: {e}")
        cnt=0
        for i,line in enumerate(self.lines):
            new,n=rx.subn(repl,line)
            if n>0:
                self.lines[i]=new; cnt+=n
        self.modified=True
        self._show(f"Replaced {cnt} occurrence(s)")

    def _save_undo_state(self):
        self.undo_stack.append((self.lines.copy(),self.cx,self.cy))
        if len(self.undo_stack)>100: self.undo_stack.pop(0)
        self.redo_stack.clear()

    def _show(self,msg):
        h,w=self.stdscr.getmaxyx()
        self.stdscr.addstr(h-1,0,msg[:w-1].ljust(w-1),curses.color_pair(1))
        self.stdscr.refresh(); self.stdscr.getch()

def main(stdscr):
    fname=sys.argv[1] if len(sys.argv)>1 else None
    PyEditor(stdscr,fname)

if __name__=="__main__":
    curses.wrapper(main)
