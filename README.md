# FileNav

A simple, TUI file dialog built with Python and the curses library.

## Features

- Navigate through directories using arrow keys
- Display file sizes in human-readable format
- Sort files by alphabet or type
- Go to a specific path
- Select files or directories

## Requirements

- Python 3.x
- curses library (typically included in standard Python installations)

## Installation

1. Clone this repository or download the source code.
2. Install the required dependencies:

## Usage

To use FileNav in your Python project:

```python
from filenav import GetPath

file_or_folder_path = "/home/user/"
selected_path = GetPath(file_or_folder_path)
if selected_path:
    print(f"Selected path: {selected_path}")
else:
    print("No path selected")
```

## Controls

- Arrow Up/Down: Move cursor
- Enter/Right Arrow: Open directory or select file
- Shift+Enter: Select current directory
- Left Arrow/Backspace: Go to parent directory
- 's': Toggle sort mode (by alphabet or type)
- 'f': Go to a specific path
- 'q': Quit the navigator

## Note
This module is designed for use in terminal environments and relies on the curses library, which is typically pre-installed on Unix-like systems (Linux, macOS). Windows users may need to install a third-party curses library.