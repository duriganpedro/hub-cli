#!/usr/bin/env python3
import sys
import threading
import time

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

C = Colors

class Spinner:
    def __init__(self, message="Processing..."):
        self.message = message
        self.running = False
        self.thread = None

    def _spin(self):
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        idx = 0
        while self.running:
            frame = frames[idx % len(frames)]
            sys.stdout.write(f"\r{C.CYAN}{frame}{C.RESET} {self.message}")
            sys.stdout.flush()
            time.sleep(0.08)
            idx += 1
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    def __enter__(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        if self.thread:
            self.thread.join()

def loading(message="Processing..."):
    return Spinner(message)

def render_box(title, lines, color=Colors.CYAN):
    width = max(len(title) + 4, max((len(l) for l in lines), default=40) + 4)
    print(f"\n{color}┌─ {title} " + "─" * (width - len(title) - 4) + f"┐{Colors.RESET}")
    for l in lines:
        print(f"{color}│{Colors.RESET} {l.ljust(width - 3)}{color}│{Colors.RESET}")
    print(f"{color}└" + "─" * (width - 1) + f"┘{Colors.RESET}\n")
