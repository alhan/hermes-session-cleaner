#!/usr/bin/env python3
"""Hermes Session Cleaner — delete short sessions, generate missing titles.

Usage:
    hermes_cleaner.py [--dry-run] [--min-messages N] [--no-delete] [--no-title]

Scans the Hermes session DB and:
1. Deletes sessions with fewer than N messages (default: 5)
2. Generates titles for sessions that don't have one (using local Ollama)

Safety: --dry-run shows what would happen without making changes.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
sys.path.insert(0, str(HERMES_HOME / "hermes-agent"))
from hermes_state import SessionDB  # noqa: E402


# ── Markdown cleanup ────────────────────────────────────────────────────────

def strip_markdown(text: str) -> str:
    """Strip markdown formatting."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*\*([^*]+)\*\*\*", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    return text.strip()


# ── Title generation ────────────────────────────────────────────────────────

def build_title_prompt(msgs: list[dict]) -> str:
    """Build prompt from conversation messages."""
    conversation = []
    for m in msgs:
        content = (m.get("content") or "").strip()
        if len(content) > 400:
            content = content[:400] + "..."
        if content:
            conversation.append(f"[{m['role']}] {content}")

    transcript = "\n\n".join(conversation)

    return (
        "You are a title generator. Your ONLY job is to output a plain text title.\n\n"
        "Generate a short, descriptive title (3-7 words, max 50 characters) for the "
        "conversation below. Capture the MAIN topic.\n\n"
        "FORMAT RULES:\n"
        "- Output ONLY the title text. Nothing else.\n"
        "- Plain text only — NO markdown, NO quotes, NO formatting.\n"
        "- NO punctuation at the end. NO 'Title:' prefix.\n\n"
        f"CONVERSATION:\n{transcript}\n\n"
        "TITLE:"
    )


def call_llm(prompt: str, endpoint: str, model: str) -> str | None:
    """Call OpenAI-compatible API for title generation."""
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 80,
        "temperature": 0.1,
    }).encode("utf-8")

    try:
        req = Request(endpoint, data=body,
                      headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            msg = data["choices"][0]["message"]
            raw = (msg.get("content")
                   or msg.get("reasoning_content")
                   or msg.get("reasoning")
                   or "").strip()

            title = strip_markdown(raw)
            title = title.strip("\"'«»„”")
            title = re.sub(r"^(Title|Başlık|TITLE)[:\s-]*", "",
                           title, flags=re.IGNORECASE)
            if len(title) > 50:
                title = title[:47] + "..."
            return title if title else None
    except Exception as e:
        print(f"  LLM error: {e}", file=sys.stderr)
        return None


def generate_title_for_session(db: SessionDB, session_id: str,
                                endpoint: str, model: str) -> str | None:
    """Generate and set a title for a session."""
    msgs = db.get_messages_as_conversation(session_id)
    user_msgs = [m for m in msgs if m.get("role") in ("user", "assistant")]
    if len(user_msgs) < 2:
        return None

    prompt = build_title_prompt(user_msgs)
    title = call_llm(prompt, endpoint, model)
    if title:
        db.set_session_title(session_id, title)
    return title


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Hermes session cleaner — delete short sessions + missing titles"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would happen, don't change anything")
    parser.add_argument("--min-messages", type=int, default=5,
                        help="Delete sessions with fewer than N messages (default: 5)")
    parser.add_argument("--no-delete", action="store_true",
                        help="Skip deletion, only generate titles")
    parser.add_argument("--no-title", action="store_true",
                        help="Skip title generation, only delete")
    parser.add_argument("--max-titles", type=int, default=20,
                        help="Max titles to generate in one run (default: 20)")
    args = parser.parse_args()

    db_path = HERMES_HOME / "state.db"
    if not db_path.exists():
        print(f"Session DB not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    db = SessionDB(db_path)
    endpoint = os.environ.get(
        "HERMES_CLEANER_ENDPOINT",
        "http://100.83.239.61:11434/v1/chat/completions"
    )
    model = os.environ.get("HERMES_CLEANER_MODEL", "hermes3:latest")

    # ── Scan ────────────────────────────────────────────────────────────
    sessions = db.list_sessions_rich(limit=500)

    to_delete = []
    to_title = []

    for s in sessions:
        sid = s["id"]
        msg_count = int(s.get("message_count", 0))
        title = s.get("title") or ""
        source = s.get("source", "?")

        if msg_count < args.min_messages:
            to_delete.append((sid, msg_count, title, source))
        elif not title:
            to_title.append((sid, msg_count, source))

    print(f"Sessions scanned : {len(sessions)}")
    print(f"To delete (<{args.min_messages} msgs) : {len(to_delete)}")
    print(f"To title  (>= {args.min_messages} msgs, no title): {len(to_title)}")

    # ── Delete short sessions ───────────────────────────────────────────
    if not args.no_delete and to_delete:
        print(f"\n--- Deleting {len(to_delete)} short sessions ---")
        for sid, cnt, title, src in to_delete:
            title_info = f' "{title}"' if title else ""
            if args.dry_run:
                print(f"  [DRY RUN] Would delete: {sid[:30]}  msgs={cnt}  src={src}{title_info}")
            else:
                try:
                    db.delete_session(sid)
                    print(f"  Deleted: {sid[:30]}  msgs={cnt}  src={src}{title_info}")
                except Exception as e:
                    print(f"  FAILED: {sid[:30]} — {e}", file=sys.stderr)
    elif args.no_delete:
        print("\n(delete skipped via --no-delete)")

    # ── Generate missing titles ─────────────────────────────────────────
    if not args.no_title and to_title:
        limit = min(len(to_title), args.max_titles)
        print(f"\n--- Generating titles ({limit} of {len(to_title)}) ---")
        generated = 0
        for sid, cnt, src in to_title[:limit]:
            if args.dry_run:
                print(f"  [DRY RUN] Would title: {sid[:30]}  msgs={cnt}  src={src}")
                continue
            print(f"  {sid[:30]}  msgs={cnt}  src={src} ...", end=" ", flush=True)
            title = generate_title_for_session(db, sid, endpoint, model)
            if title:
                print(f'→ "{title}"')
                generated += 1
            else:
                print("FAILED")
        print(f"\nTitles generated: {generated}/{limit}")
    elif args.no_title:
        print("\n(title generation skipped via --no-title)")

    if args.dry_run:
        print("\n[DRY RUN] No changes made.")


if __name__ == "__main__":
    main()
