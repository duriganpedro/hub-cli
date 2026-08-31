#!/usr/bin/env python3
import json
import re
from datetime import date
from .ai_client import query_llm
from .agenda import add_event, list_events
from .notes import add_note, list_notes
from .weather import fetch_weather
from .books import search_books
from .mail import fetch_latest_emails
from .ui import Colors as C, render_box

SYSTEM_PROMPT = """You are a minimalist, highly efficient terminal assistant.
Today's date: {CURRENT_DATE}.

If the user request maps to an action, output a single JSON object without commentary:
- Agenda: {"action": "agenda_add", "title": "...", "date": "YYYY-MM-DD", "time": "HH:MM"}
- List Agenda: {"action": "agenda_list"}
- Note: {"action": "note_add", "title": "...", "content": "..."}
- List Notes: {"action": "note_list"}
- Weather: {"action": "weather", "city": "..."}
- Search Books: {"action": "book_search", "query": "..."}
- Check Mail: {"action": "mail_fetch", "account": "primary"}
- General Question / Chat: {"action": "chat", "response": "..."}
"""

def handle_user_input(user_input):
    cleaned = user_input.strip()
    if not cleaned:
        return

    # Fast Path - Local regex routing for zero latency
    if cleaned.lower() in ("today", "agenda", "events"):
        list_events()
        return
    if cleaned.lower() in ("notes", "list notes"):
        list_notes()
        return
    if cleaned.lower().startswith("weather"):
        parts = cleaned.split(maxsplit=1)
        city = parts[1] if len(parts) > 1 else None
        fetch_weather(city)
        return
    if cleaned.lower().startswith("mail") or cleaned.lower() == "inbox":
        fetch_latest_emails()
        return
    if cleaned.lower().startswith("book ") or cleaned.lower().startswith("find "):
        query = cleaned.split(maxsplit=1)[1]
        search_books(query)
        return

    # LLM Router Path
    prompt = SYSTEM_PROMPT.replace("{CURRENT_DATE}", str(date.today()))
    response = query_llm(cleaned, system_prompt=prompt)

    try:
        data = json.loads(response)
        action = data.get("action")

        if action == "agenda_add":
            add_event(data.get("title"), data.get("date"), data.get("time"))
        elif action == "agenda_list":
            list_events()
        elif action == "note_add":
            add_note(data.get("title"), data.get("content", ""))
        elif action == "note_list":
            list_notes()
        elif action == "weather":
            fetch_weather(data.get("city"))
        elif action == "book_search":
            search_books(data.get("query"))
        elif action == "mail_fetch":
            fetch_latest_emails(data.get("account", "primary"))
        elif action == "chat":
            print(f"\n{data.get('response')}\n")
        else:
            print(f"\n{response}\n")
    except Exception:
        print(f"\n{response}\n")
