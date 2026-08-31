#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error
from .config import load_config
from .db import get_db
from datetime import date

def query_llm(prompt, system_prompt="You are a direct, concise productivity assistant."):
    config = load_config()
    ai_conf = config.get("ai", {})
    provider = ai_conf.get("provider", "lmstudio")

    if provider == "lmstudio":
        endpoint = ai_conf.get("lmstudio_endpoint", "http://localhost:1234/v1") + "/chat/completions"
        api_key = "not-needed"
        model = ai_conf.get("local_model", "local-model")
    else:
        endpoint = ai_conf.get("endpoint", "https://generativelanguage.googleapis.com/v1beta/openai") + "/chat/completions"
        api_key = ai_conf.get("api_key", "")
        model = ai_conf.get("model", "gemini-2.5-flash")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": ai_conf.get("temperature", 0.2),
        "max_tokens": ai_conf.get("max_tokens", 1024)
    }

    headers = {"Content-Type": "application/json"}
    if api_key and api_key != "not-needed":
        headers["Authorization"] = f"Bearer {api_key}"

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(endpoint, data=req_data, headers=headers)

    from .ui import loading
    with loading("Thinking..."):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                return res_json["choices"][0]["message"]["content"].strip()
        except urllib.error.URLError as e:
            if provider == "lmstudio":
                return f"[ERROR]: Local LM Studio server is not responding at {endpoint}. Start LM Studio local server."
            return f"[ERROR]: Failed connecting to AI API endpoint: {e}"
        except Exception as e:
            return f"[ERROR]: {e}"

def ai_daily_briefing():
    today = str(date.today())
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, event_time FROM agenda WHERE event_date = ? AND completed = 0", (today,))
        events = cursor.fetchall()

    context = f"Date: {today}\n"
    context += "Agenda:\n" + ("\n".join([f"- {r['event_time'] or 'All day'}: {r['title']}" for r in events]) if events else "No events.")
    
    prompt = f"Summarize today's agenda into a 3-line actionable plan:\n\n{context}"
    response = query_llm(prompt)
    print("\n=== DAILY BRIEFING ===")
    print(response)
    print("======================\n")
