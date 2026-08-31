#!/usr/bin/env python3
import sqlite3
import os
from .config import load_config
from .ui import Colors as C

def get_calibre_connection():
    cfg = load_config()
    db_path = cfg.get("library", {}).get("calibre_metadata_path")
    if not db_path or not os.path.exists(db_path):
        return None
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def search_books(query, limit=10):
    conn = get_calibre_connection()
    if not conn:
        print(f"{C.YELLOW}[WARNING]{C.RESET} Calibre metadata.db path not configured or file not found.")
        return []

    cursor = conn.cursor()
    cursor.execute("""
    SELECT b.id, b.title, b.author_sort, b.path 
    FROM books b
    WHERE b.title LIKE ? OR b.author_sort LIKE ?
    LIMIT ?
    """, (f"%{query}%", f"%{query}%", limit))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"{C.DIM}No books found matching '{query}'.{C.RESET}")
        return []

    print(f"\n{C.BOLD}--- LIBRARY RESULTS ({len(rows)}) ---{C.RESET}")
    for r in rows:
        print(f"#{r['id']} {C.CYAN}{r['title']}{C.RESET} - {r['author_sort']}")
    print()
    return rows
