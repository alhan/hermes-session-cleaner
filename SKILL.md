---
name: session-cleaner
description: "Clean Hermes session DB: delete short conversations, generate missing titles."
version: 1.1.0
installed_from: https://github.com/alhan/hermes-session-cleaner/raw/branch/main/SKILL.md
---

# Session Cleaner

When the user says **"temizlik yap"** or **"clean sessions"**, follow this workflow.

Trigger keywords: `temizlik yap`, `clean sessions`

## Workflow

### Step 1: Dry-run first

ALWAYS dry-run first — deletion is irreversible:

```bash
SKILL_DIR=$(dirname $(readlink -f ~/.hermes/skills/productivity/session-cleaner/SKILL.md))
python3 "$SKILL_DIR/scripts/hermes_cleaner.py" --dry-run
```

### Step 2: Report and confirm

Show the user:
- How many sessions will be deleted (and some examples)
- How many sessions will get titles

Ask for confirmation. User may want to adjust `--min-messages` or skip parts.

### Step 3: Run for real

```bash
python3 "$SKILL_DIR/scripts/hermes_cleaner.py"
```

### Options

| Flag | Effect |
|---|---|
| `--dry-run` | Preview only, no changes |
| `--min-messages N` | Delete sessions with < N messages (default: 5) |
| `--no-delete` | Skip deletion, only generate titles |
| `--no-title` | Skip title generation, only delete |
| `--max-titles N` | Max titles per run (default: 20) |

## Configuration

Default is DeepSeek v4 Flash API (works everywhere, needs API key in `.env`):

| Env var | Default | Description |
|---|---|---|
| `HERMES_CLEANER_MODEL` | `deepseek-v4-flash` | Model for title generation |
| `HERMES_CLEANER_ENDPOINT` | `https://api.deepseek.com/v1/chat/completions` | API endpoint |
| `HERMES_CLEANER_API_KEY` | auto-loaded from `~/.hermes/.env` (`DEEPSEEK_API_KEY`) | API key |

To switch to local Ollama:
```bash
export HERMES_CLEANER_ENDPOINT="http://localhost:11434/v1/chat/completions"
export HERMES_CLEANER_MODEL="hermes3:latest"
export HERMES_CLEANER_API_KEY=""
```

## Important Rules

- **Dry-run first. Always.** Deletion is IRREVERSIBLE.
- Short sessions are deleted FIRST, then titles generated for remaining untitled ones.
  This avoids generating titles for sessions that will be deleted anyway.
- Title generation uses the same model rules as **session-ending** skill — see
  its Pitfalls section for model selection guidance.

## Pitfalls

### Same model pitfalls as session-ending

This skill uses the same title generation pipeline as session-ending. All pitfalls
from that skill apply — see **session-ending** skill's Pitfalls section for the
full model compatibility table. Key points:
- `deepseek-v4-flash` requires `max_tokens ≥ 500` (script already uses 500)
- `deepseek-chat` and `hermes3:latest` work with any limit
- Ollama thinking models (`gemma4:12b`, `qwen3.5:9b`) are unreliable — avoid
- Markdown stripping and strict prompt formatting are handled by the script

### Overlap between short AND untitled sessions

Sessions that are both short (< N msgs) AND untitled appear in both lists during
scan. The script handles this correctly: delete runs first, so these sessions
are removed before title generation starts. No titles are wasted on doomed sessions.

## See Also

- **session-ending** skill — per-session title + save workflow ("ending")
- Gitea repo: https://github.com/alhan/hermes-session-cleaner
