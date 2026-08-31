#!/usr/bin/env python3
import sys
import os
import shlex
import readline
import atexit

from .db import init_db
from .agent import handle_user_input
from .ui import Colors as C
from .agenda import add_event, list_events, mark_done, delete_event
from .notes import add_note, list_notes, search_notes, delete_note
from .weather import fetch_weather
from .mail import fetch_latest_emails
from .books import search_books

HISTORY_FILE = os.path.expanduser("~/.config/hub/.history")

def setup_readline():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if os.path.exists(HISTORY_FILE):
        try:
            readline.read_history_file(HISTORY_FILE)
        except Exception:
            pass
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")

    def completer(text, state):
        buffer = readline.get_line_buffer().lstrip()
        tokens = buffer.split()
        
        if not tokens or (len(tokens) == 1 and not buffer.endswith(" ")):
            matches = [c for c in ["agenda", "notes", "mail", "weather", "books", "ask", "help", "exit", "quit"] if c.startswith(text)]
        elif tokens[0] == "agenda":
            matches = [s for s in ["add", "list", "done", "rm"] if s.startswith(text)]
        elif tokens[0] == "notes":
            matches = [s for s in ["add", "list", "search", "rm"] if s.startswith(text)]
        else:
            matches = []
            
        return matches[state] if state < len(matches) else None

    readline.set_completer(completer)
    atexit.register(lambda: readline.write_history_file(HISTORY_FILE) if os.path.exists(os.path.dirname(HISTORY_FILE)) else None)

def print_help():
    print(f"""
{C.BOLD}hub-cli commands:{C.RESET}
  agenda [list|add <title>|done <id>|rm <id>]   Manage calendar & tasks
  notes  [list|add <title> [content]|search <q>|rm <id>]  Manage notes with BM25 search
  mail   [account_key]                         Sync email headers
  weather [city]                               Get weather forecast
  books  <query>                               Search Calibre library
  ask    <question>                            Ask AI assistant (Local / API)
  help / -h / --help                           Show this help message
  exit / quit / q                              Exit interactive shell
""")

def run_command(args):
    if not args:
        return
    cmd = args[0].lower()
    
    if cmd in ("help", "-h", "--help"):
        print_help()
    elif cmd == "agenda":
        sub = args[1].lower() if len(args) > 1 else "list"
        if sub == "add":
            if len(args) > 2:
                add_event(" ".join(args[2:]))
            else:
                print(f"{C.YELLOW}Usage:{C.RESET} agenda add <event title>")
        elif sub == "done":
            if len(args) > 2:
                try: mark_done(int(args[2]))
                except ValueError: print(f"{C.RED}[ERROR]{C.RESET} Invalid ID.")
            else:
                print(f"{C.YELLOW}Usage:{C.RESET} agenda done <id>")
        elif sub == "rm":
            if len(args) > 2:
                try: delete_event(int(args[2]))
                except ValueError: print(f"{C.RED}[ERROR]{C.RESET} Invalid ID.")
            else:
                print(f"{C.YELLOW}Usage:{C.RESET} agenda rm <id>")
        elif sub == "list":
            list_events(show_all=True)
        else:
            add_event(" ".join(args[1:]))
    elif cmd == "notes":
        sub = args[1].lower() if len(args) > 1 else "list"
        if sub == "add":
            if len(args) > 2:
                title = args[2]
                content = " ".join(args[3:]) if len(args) > 3 else ""
                add_note(title, content)
            else:
                print(f"{C.YELLOW}Usage:{C.RESET} notes add <title> [content]")
        elif sub == "search":
            if len(args) > 2:
                search_notes(" ".join(args[2:]))
            else:
                print(f"{C.YELLOW}Usage:{C.RESET} notes search <query>")
        elif sub == "rm":
            if len(args) > 2:
                try: delete_note(int(args[2]))
                except ValueError: print(f"{C.RED}[ERROR]{C.RESET} Invalid ID.")
            else:
                print(f"{C.YELLOW}Usage:{C.RESET} notes rm <id>")
        elif sub == "list":
            list_notes()
        else:
            search_notes(" ".join(args[1:]))
    elif cmd == "mail":
        acc = args[1] if len(args) > 1 else None
        fetch_latest_emails(acc)
    elif cmd == "weather":
        city = " ".join(args[1:]) if len(args) > 1 else None
        fetch_weather(city)
    elif cmd in ("books", "find"):
        if len(args) > 1:
            search_books(" ".join(args[1:]))
        else:
            print(f"{C.YELLOW}Usage:{C.RESET} books <query>")
    elif cmd == "ask":
        if len(args) > 1:
            handle_user_input(" ".join(args[1:]))
        else:
            print(f"{C.YELLOW}Usage:{C.RESET} ask <prompt>")
    else:
        handle_user_input(" ".join(args))

def main():
    init_db()

    if len(sys.argv) > 1:
        run_command(sys.argv[1:])
        return

    setup_readline()
    print(f"{C.BOLD}hub-cli{C.RESET} | Type a command or question (type '{C.CYAN}help{C.RESET}' or '{C.CYAN}exit{C.RESET}').\n")
    
    while True:
        try:
            raw_cmd = input(f"{C.CYAN}hub > {C.RESET}").strip()
            if not raw_cmd:
                continue
            if raw_cmd.lower() in ("exit", "quit", "q"):
                print("Bye.")
                break
            
            try:
                tokens = shlex.split(raw_cmd)
            except ValueError:
                tokens = raw_cmd.split()

            run_command(tokens)
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            break

if __name__ == "__main__":
    main()
