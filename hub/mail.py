#!/usr/bin/env python3
import email
import imaplib
import socket
import time
from email.header import decode_header
from .config import load_config
from .ui import Colors as C, loading

DEFAULT_TIMEOUT = 15.0
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0

def decode_mime_words(s: str | None) -> str:
    if not s:
        return ""
    decoded_fragments = decode_header(s)
    res = []
    for fragment, encoding in decoded_fragments:
        if isinstance(fragment, bytes):
            res.append(fragment.decode(encoding or "utf-8", errors="replace"))
        else:
            res.append(str(fragment))
    return "".join(res)

def connect_imap(server: str, port: int, user: str, pwd: str, timeout: float = DEFAULT_TIMEOUT, retries: int = MAX_RETRIES):
    last_err = None
    backoff = INITIAL_BACKOFF
    for attempt in range(1, retries + 1):
        try:
            client = imaplib.IMAP4_SSL(host=server, port=port, timeout=timeout)
            client.login(user, pwd)
            return client
        except (imaplib.IMAP4.error, socket.timeout, OSError) as e:
            last_err = e
            if attempt < retries:
                time.sleep(backoff)
                backoff *= 2
    raise ConnectionError(f"IMAP connection failed after {retries} attempts: {last_err}")

def fetch_latest_emails(account_key: str | None = None, limit: int = 10):
    cfg = load_config()
    accounts = cfg.get("accounts", {})
    
    acc = None
    if account_key and account_key in accounts:
        acc = accounts[account_key]
    elif "primary" in accounts:
        acc = accounts["primary"]
    elif "account_1" in accounts:
        acc = accounts["account_1"]
    elif accounts:
        acc = next(iter(accounts.values()))

    if not acc or not acc.get("email") or not acc.get("password") or "<YOUR_" in acc.get("email", ""):
        print(f"{C.RED}[ERROR]{C.RESET} Valid IMAP account is not configured in ~/.config/hub/config.json.")
        return

    server = acc.get("imap_server")
    port = acc.get("imap_port", 993)
    user = acc.get("email")
    pwd = acc.get("password")
    name = acc.get("name", "Mail")

    client = None
    with loading(f"Syncing emails for {name}..."):
        try:
            client = connect_imap(server, port, user, pwd)
            client.select("INBOX", readonly=True)

            status, data = client.search(None, "ALL")
            if status != "OK" or not data[0]:
                print(f"{C.DIM}Inbox is empty.{C.RESET}")
                return

            email_ids = data[0].split()
            latest_ids = email_ids[-limit:]
            latest_ids.reverse()

            print(f"\n{C.BOLD}--- LATEST EMAILS ({name}) ---{C.RESET}")
            id_set = b",".join(latest_ids)
            status, batch_data = client.fetch(id_set, "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])")
            
            if status == "OK":
                for item in batch_data:
                    if isinstance(item, tuple):
                        header_bytes = item[1]
                        msg = email.message_from_bytes(header_bytes)
                        subject = decode_mime_words(msg.get("Subject", "(No Subject)"))
                        sender = decode_mime_words(msg.get("From", "(Unknown Sender)"))
                        date_hdr = msg.get("Date", "")
                        print(f"• {C.BOLD}{subject}{C.RESET}")
                        print(f"    From: {sender} | Date: {date_hdr}")
            print()
        except Exception as e:
            print(f"{C.RED}[ERROR]{C.RESET} IMAP Sync error: {e}")
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass
                try:
                    client.logout()
                except Exception:
                    pass
