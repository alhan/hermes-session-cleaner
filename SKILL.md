---
name: session-cleaner
description: "Clean Hermes session DB: delete short conversations, generate missing titles."
version: 1.0.0
---

# Session Cleaner

Scans the Hermes session DB and:
1. Deletes sessions with fewer than 5 messages (configurable)
2. Generates titles for sessions that don't have one

Uses local Ollama (hermes3:latest) for title generation.

## Usage

```bash
python3 hermes_cleaner.py --dry-run      # Preview
python3 hermes_cleaner.py                # Full clean
python3 hermes_cleaner.py --no-delete    # Titles only
python3 hermes_cleaner.py --min-messages 3  # Custom threshold
```

## Requirements

- Hermes Agent installed (for hermes_state module)
- Ollama with hermes3:latest model (env-configurable)
