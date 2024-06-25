import os
import curses

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0

class FileNavigator:
    def __init__(self, initial_path=None):
        self.current_path = os.path.abspath(initial_path) if initial_path else os.getcwd()
        self.cursor_position = 0
        self.scroll_offset = 0
        self.items = []
        self.sizes = {}
        self.calculating_size = False
        self.sort_by_alphabet = False

    def get_items(self):
        try:
            all_items = [f for f in os.listdir(self.current_path) if not f.startswith('.')]
            folders = []
            files = []
            for item in all_items:
                full_path = os.path.join(self.current_path, item)
                if os.path.isdir(full_path):
                    folders.append(item)
                else:
                    files.append(item)
            
            if self.sort_by_alphabet:
                self.items = ['..'] + sorted(folders + files)
            else:
                self.items = ['..'] + sorted(folders) + sorted(files)
                
            self.sizes = {}
            for item in self.items:
                full_path = os.path.join(self.current_path, item)
                if os.path.isfile(full_path):
                    try:
                        self.sizes[item] = os.path.getsize(full_path)
                    except OSError:
                        self.sizes[item] = -1
                else:
                    self.sizes[item] = -2  # Indicate it's a directory
        except PermissionError:
            self.items = ['..']
            self.sizes = {'..': -2}

    def calculate_folder_size(self, path):
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    pass
        return total

    def prompt_for_path(self, stdscr):
        height, width = stdscr.getmaxyx()
        stdscr.addstr(height-1, 0, "Enter path: ")
        curses.echo()
        path = stdscr.getstr(height-1, 12, width-13).decode('utf-8')
        curses.noecho()
        return path.strip()

    def clear_screen(self):
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def display(self, stdscr):
        self.clear_screen()
        curses.curs_set(0)  # Hide the cursor
        while True:
            height, width = stdscr.getmaxyx()
            if height < 5 or width < 40:
                stdscr.clear()
                stdscr.addstr(0, 0, "Window too small. Please resize.", curses.A_BOLD)
                stdscr.refresh()
                stdscr.getch()
                continue

            self.get_items()
            stdscr.clear()
            try:
                stdscr.addstr(0, 0, f"Current path: {self.current_path}")
                stdscr.addstr(1, 0, "Return: Navigate | Shift+Enter: Select | s: Sort by Alphabet/Type | f: Go to Path | q: Quit")
                stdscr.addstr(2, 0, "-" * width)

                for i in range(min(height - 4, len(self.items))):
                    item_index = i + self.scroll_offset
                    if item_index < len(self.items):
                        item = self.items[item_index]
                        size = self.sizes[item]
                        if size == -1:
                            size_str = "N/A"
                        elif size == -2:
                            size_str = "DIR"
                        else:
                            size_str = format_size(size)
                        if os.path.isdir(os.path.join(self.current_path, item)):
                            item += "/"
                        display_str = f"{item:<50} {size_str:>10}"
                        if item_index == self.cursor_position:
                            stdscr.addstr(i + 3, 0, f"> {display_str}", curses.A_REVERSE)
                        else:
                            stdscr.addstr(i + 3, 0, f"  {display_str}")

                if self.calculating_size:
                    stdscr.addstr(height-1, 0, "Calculating size...", curses.A_BOLD)
            except curses.error:
                pass  # Handle the error and skip drawing if the terminal is too small

            stdscr.refresh()

            key = stdscr.getch()

            if key == ord('q'):
                return None
            elif key == curses.KEY_UP:
                self.cursor_position = max(0, self.cursor_position - 1)
            elif key == curses.KEY_DOWN:
                self.cursor_position = min(len(self.items) - 1, self.cursor_position + 1)
            elif key == ord('\n') or key == 10 or key == 13 or key == curses.KEY_RIGHT: # Enter key or arrow right
                selected_item = self.items[self.cursor_position]
                new_path = os.path.join(self.current_path, selected_item)
                if selected_item == '..':
                    self.current_path = os.path.dirname(self.current_path)
                elif os.path.isdir(new_path):
                    self.current_path = new_path
                else:
                    return new_path
                self.clear_screen()
                self.cursor_position = 0
                self.scroll_offset = 0
            elif key == 353:  # Shift+Enter
                selected_item = self.items[self.cursor_position]
                if selected_item == '..':
                    return os.path.dirname(self.current_path)
                else:
                    new_path = os.path.join(self.current_path, selected_item)
                    if os.path.isdir(new_path):
                        return new_path
            elif key in (curses.KEY_BACKSPACE, ord('\b'), 127) or key == curses.KEY_LEFT:  # Backspace key or left arrow
                parent_dir = os.path.dirname(self.current_path)
                if parent_dir != self.current_path:  # Check if there's an upper directory
                    self.current_path = parent_dir
                    self.clear_screen()
                    self.cursor_position = 0
                    self.scroll_offset = 0
            elif key == ord('s'):  # Toggle sort type
                self.sort_by_alphabet = not self.sort_by_alphabet
            elif key == ord('f'):  # Prompt for path
                new_path = self.prompt_for_path(stdscr)
                if os.path.exists(new_path) and os.path.isdir(new_path):
                    self.current_path = os.path.abspath(new_path)
                    self.clear_screen()
                    self.cursor_position = 0
                    self.scroll_offset = 0
                else:
                    stdscr.addstr(height-1, 0, "Invalid path. Press any key to continue.", curses.A_BOLD)
                    stdscr.getch()
            
            elif key == curses.KEY_RESIZE:  # Handle terminal resize
                continue

            # Adjust scroll offset
            if self.cursor_position < self.scroll_offset:
                self.scroll_offset = self.cursor_position
            elif self.cursor_position >= self.scroll_offset + height - 4:
                self.scroll_offset = self.cursor_position - (height - 5)

def GetPath(initial_path=None):
    return curses.wrapper(FileNavigator(initial_path).display)