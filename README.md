# PyEditor

A minimal, nano-inspired text editor for your terminal, implemented in Python with the `curses` library. Edit files without leaving the command line—Ctrl+S to save, Ctrl+Q to quit.

---

## Table of Contents

- [Overview](#overview)  
- [Features](#features)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Keybindings](#keybindings)  
- [Development & Customization](#development--customization)  
- [Contributing](#contributing)  
- [License](#license)  
- [Author](#author)  

---

## Overview

PyEditor is a lightweight, terminal-based text editor that mimics the simplicity and keybindings of Nano. It runs in a Unix-style terminal (Linux, macOS, WSL) and does not require a GUI.  

All you need is Python and a terminal window to open, modify, and save files quickly.

---

## Features

- Open existing files or start with an empty buffer  
- Navigate with arrow keys, handle long files with scrolling  
- Insert printable characters, Backspace, and Enter for new lines  
- Ctrl+S to save (prompts for “Save As” on unnamed buffers)  
- Ctrl+Q to quit the editor gracefully  
- Status bar displaying filename, cursor position, and shortcuts  

---

## Prerequisites

- Python 3.6 or newer  
- A Unix-compatible terminal supporting the `curses` module  
- (Windows users: run under WSL or use a compatible `curses` port)  

---

## Installation

Clone the repository and make the script executable:

```bash
git clone https://github.com/bocaletto-luca/PyEditor.git
cd PyEditor
chmod +x pyeditor.py
```

No additional packages are required—`curses` is included with most Python distributions.

---

## Usage

Launch PyEditor with or without a filename:

```bash
./pyeditor.py [optional_filename.txt]
```

- If a filename is provided, that file is loaded into the editor.  
- If no filename is given, you start with a blank buffer and can save it later.

---

## Keybindings

| Combination   | Action                              |
|---------------|-------------------------------------|
| Arrow Keys    | Move cursor up/down/left/right      |
| Backspace     | Delete character before the cursor  |
| Enter         | Insert a new line                   |
| Ctrl + S      | Save file (`Save As` if unnamed)    |
| Ctrl + Q      | Quit editor                         |

---

## Development & Customization

- Extend syntax highlighting by integrating `pygments` with `curses` color pairs.  
- Add search and replace (e.g., Ctrl+F, Ctrl+R) with a prompt.  
- Implement undo/redo stacks to revisit changes.  
- Support mouse events if your terminal allows.  
- Package as a pip-installable module with entry points.

---

## Contributing

Contributions, bug reports, and feature requests are welcome!

1. Fork the repository  
2. Create a new branch for your feature or bugfix  
3. Commit changes with clear messages  
4. Open a pull request and describe your changes  

Please follow [PEP 8](https://peps.python.org/pep-0008/) coding style and include tests where applicable.

---

## License

This project is licensed under the **GPL License**. See [LICENSE](LICENSE) for details.

---

## Author

**Luca Bocaletto**  
- GitHub: [bocaletto-luca](https://github.com/bocaletto-luca)  
- Website: https://bocaletto-luca.github.io  
- Portfolio: https://bocalettoluca.altervista.org  
