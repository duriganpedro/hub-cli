#!/usr/bin/env python3
from .db import get_db
from .ui import Colors as C
from .rag import retrieve_top_chunks

def add_note(title: str, content: str = "", category: str = "general"):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (title, content, category) VALUES (?, ?, ?)",
            (title, content, category)
        )
    print(f"{C.GREEN}[OK]{C.RESET} Note saved: '{title}'")

def list_notes(category: str | None = None):
    with get_db() as conn:
        cursor = conn.cursor()
        if category:
            cursor.execute("SELECT id, title, content, category, pinned, created_at FROM notes WHERE category = ? ORDER BY pinned DESC, id DESC", (category,))
        else:
            cursor.execute("SELECT id, title, content, category, pinned, created_at FROM notes ORDER BY pinned DESC, id DESC")
        rows = cursor.fetchall()

    if not rows:
        print(f"{C.DIM}No notes stored.{C.RESET}")
        return

    print(f"\n{C.BOLD}--- NOTES ---{C.RESET}")
    for r in rows:
        pin = f"{C.YELLOW} {C.RESET}" if r["pinned"] else ""
        print(f"#{r['id']} {pin}[{r['category']}] {C.BOLD}{r['title']}{C.RESET}")
        if r['content']:
            print(f"    {r['content']}")
    print()

def search_notes(query: str, top_k: int = 5):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content, category FROM notes")
        rows = cursor.fetchall()

    if not rows:
        print(f"{C.DIM}No notes stored.{C.RESET}")
        return

    docs = []
    doc_map = {}
    for r in rows:
        text = f"{r['title']}\n{r['content'] or ''}".strip()
        docs.append(text)
        doc_map[text] = r

    matched_texts = retrieve_top_chunks(docs, query, top_k=top_k)
    if not matched_texts:
        print(f"{C.DIM}No notes matched query '{query}'.{C.RESET}")
        return

    print(f"\n{C.BOLD}--- SEARCH RESULTS: NOTES ({len(matched_texts)}) ---{C.RESET}")
    for t in matched_texts:
        r = doc_map[t]
        print(f"#{r['id']} [{r['category']}] {C.BOLD}{r['title']}{C.RESET}")
        if r['content']:
            print(f"    {r['content']}")
    print()

def delete_note(note_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    print(f"{C.RED}[OK]{C.RESET} Note #{note_id} removed.")
