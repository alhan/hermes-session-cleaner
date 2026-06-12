# Hermes Session Cleaner

Clean up your Hermes Agent session DB: delete short conversations, generate missing titles.

## Installation

### Option 1: Hermes Skill (recommended)

```bash
hermes skills install https://github.com/alhan/hermes-session-cleaner/raw/branch/main/SKILL.md
```

### Option 2: Manual (git clone)

```bash
git clone https://github.com/alhan/hermes-session-cleaner.git
cd hermes-session-cleaner
python3 hermes_cleaner.py --dry-run
```

### Option 3: One-liner (curl)

```bash
curl -O https://github.com/alhan/hermes-session-cleaner/raw/branch/main/hermes_cleaner.py
python3 hermes_cleaner.py --dry-run
```

## Usage in Hermes

Once installed as a skill, trigger it by saying one of these inside Hermes:

| Say this | What happens |
|---|---|
| `temizlik yap` | Dry-run preview → asks for confirmation → cleans |
| `clean sessions` | Same (English) |

The agent runs dry-run first, shows results, asks for confirmation, then cleans.

## CLI Usage

```bash
python3 hermes_cleaner.py --dry-run              # Preview only (always run first)
python3 hermes_cleaner.py                        # Full clean
python3 hermes_cleaner.py --min-messages 3       # Custom threshold
python3 hermes_cleaner.py --no-title             # Delete only, no titles
python3 hermes_cleaner.py --no-delete --max-titles 50  # Titles only
```

## How It Works

1. Scans all sessions (`~/.hermes/state.db`)
2. Deletes sessions with fewer than N messages (default: 5)
3. Generates titles for sessions with >= N messages but no title (DeepSeek v4 Flash)

## Requirements

- Hermes Agent installed (for `hermes_state` module)
- `DEEPSEEK_API_KEY` in `~/.hermes/.env`
- Alternative: point to local Ollama via env vars

## Configuration

| Variable | Default | Description |
|---|---|---|
| `HERMES_CLEANER_MODEL` | `deepseek-v4-flash` | Model for title generation |
| `HERMES_CLEANER_ENDPOINT` | `https://api.deepseek.com/v1/chat/completions` | API endpoint |
| `HERMES_CLEANER_API_KEY` | from `.env` (`DEEPSEEK_API_KEY`) | API key |

### Using local Ollama instead

```bash
export HERMES_CLEANER_ENDPOINT="http://localhost:11434/v1/chat/completions"
export HERMES_CLEANER_MODEL="hermes3:latest"   # or any Ollama model
export HERMES_CLEANER_API_KEY=""
```

## Cron (Scheduled Cleanup)

```bash
# Inside Hermes:
/cron "every sunday 03:00 run session cleanup"

# Or system cron:
0 3 * * 0 cd /path/to/hermes-session-cleaner && python3 hermes_cleaner.py
```

## Related Projects

| Project | Purpose | When |
|---|---|---|
| [session-ending](https://github.com/alhan/hermes-session-ending) | End session: title + save + reset | End of each session (`ending`) |
| session-cleaner (this repo) | Batch cleanup: delete + title | Weekly maintenance |
