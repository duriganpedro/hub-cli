#!/usr/bin/env python3
from datetime import date
from .db import get_db
from .ui import Colors as C

def add_event(title: str, event_date: str | None = None, event_time: str | None = None, category: str = "general"):
    target_date = event_date or str(date.today())
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO agenda (title, event_date, event_time, category) VALUES (?, ?, ?, ?)",
            (title, target_date, event_time, category)
        )
    print(f"{C.GREEN}[OK]{C.RESET} Event added: '{title}' on {target_date} {event_time or ''}".strip())

def list_events(target_date: str | None = None, show_all: bool = False):
    with get_db() as conn:
        cursor = conn.cursor()
        if show_all:
            cursor.execute("SELECT id, title, event_date, event_time, category, completed FROM agenda ORDER BY event_date, event_time")
        else:
            d = target_date or str(date.today())
            cursor.execute("SELECT id, title, event_date, event_time, category, completed FROM agenda WHERE event_date = ? ORDER BY event_time", (d,))
        rows = cursor.fetchall()

    if not rows:
        print(f"{C.DIM}No events found.{C.RESET}")
        return

    print(f"\n{C.BOLD}--- AGENDA ---{C.RESET}")
    for r in rows:
        status = f"{C.GREEN}[DONE]{C.RESET}" if r["completed"] else f"{C.YELLOW}[TODO]{C.RESET}"
        time_str = f"({r['event_time']})" if r["event_time"] else ""
        print(f"#{r['id']} {status} {r['event_date']} {time_str} {r['title']} [{r['category']}]")
    print()

def mark_done(event_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE agenda SET completed = 1 WHERE id = ?", (event_id,))
    print(f"{C.GREEN}[OK]{C.RESET} Event #{event_id} marked as completed.")

def delete_event(event_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM agenda WHERE id = ?", (event_id,))
    print(f"{C.RED}[OK]{C.RESET} Event #{event_id} deleted.")
