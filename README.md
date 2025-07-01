# PyEditor v0.9

PyEditor is a modern terminal-based text editor implemented in Python, designed to marry the familiar simplicity of Nano with powerful, IDE-style features—all within a console. It uses the curses library for efficient screen management and Pygments for real-time syntax highlighting across any language supported by its lexers. Users benefit from a JSON configuration file that allows full customization of keybindings (save, quit, undo, redo, search, replace) and the color theme for status bars and token types. Core editing facilities include undo/redo stacks, interactive incremental search (Ctrl+F), regex-powered find & replace (Ctrl+R), dynamic line numbering, mouse-driven cursor placement, and a colorized status bar displaying file name, modified state, cursor coordinates, and shortcut reminders. All operations function without any GUI dependency, making PyEditor ideal for remote SSH sessions, lightweight container environments, or local development on headless systems. With minimal startup overhead and a clean, extensible codebase, PyEditor provides a streamlined yet feature-rich editing experience.  

---

## Table of Contents

- [Overview](#overview)  
- [Features](#features)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Keybindings](#keybindings)  
- [Configuration](#configuration)  
- [Contributing](#contributing)  
- [License](#license)  
- [Author](#author)  

---

## Overview

PyEditor is a lightweight, terminal-based text editor that combines Nano’s straightforward interface with next-generation enhancements. It operates entirely within a Unix-style terminal (Linux, macOS, WSL) and requires no GUI.

---

## Features

- Nano-inspired simplicity with advanced enhancements  
- Undo/Redo (Ctrl+Z / Ctrl+Y) and unlimited history snapshots  
- Incremental search (Ctrl+F) and regex find & replace (Ctrl+R)  
- Real-time syntax highlighting via Pygments lexers  
- Dynamic line numbers and smooth viewport scrolling  
- Mouse-click cursor positioning for quick navigation  
- Colorized status bar showing file name, modified flag, cursor position, and key hints  
- Fully customizable keybindings and color themes through JSON  

---

## Prerequisites

- Python 3.6 or newer  
- Unix-style terminal supporting the `curses` module  
- Pygments library (`pip install pygments`)  

---

## Installation

```bash
git clone https://github.com/bocaletto-luca/PyEditor.git
cd PyEditor
pip install pygments
chmod +x pyeditor.py
```

---

## Usage

```bash
./pyeditor.py [optional_filename]
```

- Launch with a filename to open it, or start on a blank buffer.  
- Use Ctrl+S to save, Ctrl+Q to quit.

---

## Keybindings

| Keys         | Action                                    |
|--------------|-------------------------------------------|
| Arrow Keys   | Move cursor                              |
| Backspace    | Delete character                         |
| Enter        | New line                                 |
| Ctrl + S     | Save file (Save As if unnamed)           |
| Ctrl + Q     | Quit editor                              |
| Ctrl + Z / Y | Undo / Redo                              |
| Ctrl + F     | Search                                   |
| Ctrl + R     | Find & Replace (regex)                   |
| Mouse Click  | Move cursor to clicked position          |

---

## Configuration

Create `~/.pyeditor.json` to override defaults:

```json
{
  "keybindings": {
    "save": 19, "quit": 17, "undo": 26, "redo": 25,
    "search": 6, "replace": 18
  },
  "syntax": { "lexer": "python" },
  "theme": {
    "status_bg": "cyan", "status_fg": "black",
    "keyword": "yellow", "string": "green", "comment": "blue"
  }
}
```

- **keybindings**: ASCII codes for commands  
- **syntax.lexer**: Pygments lexer name  
- **theme**: Curses colors for status bar and token types  

---

## Contributing

Bug reports, feature requests, and pull requests are welcome! Please fork the repository, follow PEP 8 coding style, and include tests or examples when appropriate.

---

## License

Distributed under the **GNU GPL v3**. See [LICENSE](LICENSE) for details.

---

## Author

**Luca Bocaletto**  
- GitHub: [bocaletto-luca](https://github.com/bocaletto-luca)  
- Website: https://bocaletto-luca.github.io  

---
