# hub-cli

A modular command-line interface (CLI) for personal terminal workflows: calendar, notes, mail synchronization, weather queries, and semantic book search with RAG.

---

##  Project Structure

```
hub-cli/
├── hub/                  # Core package
│   ├── cli.py            # Entry point & command routing
│   ├── agenda.py         # Calendar & task operations
│   ├── notes.py          # Notes storage & BM25 search
│   ├── weather.py        # Open-Meteo forecast client
│   ├── mail.py           # IMAP email synchronization
│   ├── books.py          # Calibre library search
│   ├── rag.py            # BM25 Okapi retriever
│   ├── db.py             # SQLite context manager (WAL mode)
│   ├── config.py         # Configuration loader
│   ├── ai_client.py      # Dual provider (LM Studio / API)
│   └── ui.py             # Terminal styling & spinner
├── tests/                # Unit test suite
├── pyproject.toml        # Package & CLI script definition
├── requirements.txt      # Zero external dependencies
└── config.example.json   # Configuration template
```

---

##  Quickstart

### 1. Installation
Install the package in editable mode:

```bash
pip install -e .
```

Now you can invoke `hub` directly from any directory:

```bash
hub --help
```

Or run directly without installation:

```bash
python3 -m hub
```

### 2. Configuration
Copy the template configuration file:

```bash
mkdir -p ~/.config/hub
cp config.example.json ~/.config/hub/config.json
```

Fill in your respective credentials and paths in `~/.config/hub/config.json`.

---

##  Testing
Run the zero-dependency test suite:

```bash
python3 -m unittest discover -s tests
```

---

##  License
MIT License
