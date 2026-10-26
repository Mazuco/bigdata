"""Pattern 1 — Guard local, think cloud.

A local-first router that classifies every prompt with Ollama BEFORE
deciding whether to forward it to Claude Code (cloud) or answer locally.

Guarantees that no byte of a 'sensitive' prompt ever leaves the machine —
not even to decide where it goes.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...     # for cloud fallback
    python hybrid_router.py "your prompt here"

Or import as a library:
    from hybrid_router import route
    answer = route("some question")
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import ollama

OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "llama3.2:3b")

ollama_client = ollama.Client(host=OLLAMA_URL)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Local classifier — determines if the prompt should stay on-device
# ─────────────────────────────────────────────────────────────────────────────
CLASSIFIER_SYSTEM = """You are a security classifier. Return ONLY valid JSON.

Classify the user input as 'safe' or 'sensitive'.

Sensitive = contains ANY of:
- API keys, tokens, passwords, credentials, access keys
- Personal data (CPF, SSN, email, phone, address of real people)
- Internal company data (internal URLs, class names, infrastructure, NDA material)
- Medical, legal, financial data belonging to third parties
- Code snippets that look proprietary (uncommon patterns, business logic)

Safe = generic programming questions, public info, abstract reasoning,
       textbook algorithms, OSS library usage, hypothetical examples.

Return format: {"level": "safe"|"sensitive", "reason": "<one short sentence>"}
"""


def classify_sensitivity(prompt: str) -> dict:
    """Classify a prompt locally. Deterministic by design."""
    r = ollama_client.chat(
        model=LOCAL_MODEL,
        messages=[
            {"role": "system", "content": CLASSIFIER_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        format="json",
        options={"temperature": 0.0},
    )
    try:
        return json.loads(r["message"]["content"])
    except json.JSONDecodeError:
        # If the model misbehaves, default to the safe-for-privacy choice: local
        return {"level": "sensitive", "reason": "classifier output malformed — defaulting to local"}


# ─────────────────────────────────────────────────────────────────────────────
# 2. Local answer path — stays on the machine
# ─────────────────────────────────────────────────────────────────────────────
def answer_locally(prompt: str) -> str:
    """Answer the prompt using the local Ollama model."""
    r = ollama_client.chat(
        model=LOCAL_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.3},
    )
    return r["message"]["content"]


# ─────────────────────────────────────────────────────────────────────────────
# 3. Cloud answer path — delegates to Claude Code
# ─────────────────────────────────────────────────────────────────────────────
def answer_with_claude_code(prompt: str) -> str:
    """Delegate the prompt to Claude Code (headless mode).

    Requires the Claude Code CLI installed and ANTHROPIC_API_KEY set.
    See https://docs.claude.com/claude-code for setup.
    """
    try:
        result = subprocess.run(
            ["claude", "--print", prompt],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        return result.stdout
    except FileNotFoundError:
        return (
            "[cloud path unavailable] Claude Code CLI not found. "
            "Install from https://docs.claude.com/claude-code — "
            "falling back to local.\n\n" + answer_locally(prompt)
        )
    except subprocess.CalledProcessError as e:
        return f"[cloud error] {e.stderr}\n\nFalling back to local:\n\n{answer_locally(prompt)}"


# ─────────────────────────────────────────────────────────────────────────────
# 4. The router
# ─────────────────────────────────────────────────────────────────────────────
def route(prompt: str, *, verbose: bool = True) -> str:
    """Classify locally, then route to local or cloud."""
    classification = classify_sensitivity(prompt)
    level = classification.get("level", "sensitive")
    reason = classification.get("reason", "(no reason given)")

    if verbose:
        print(f"[router] level={level}  reason={reason}", file=sys.stderr)

    if level == "sensitive":
        if verbose:
            print("[router] → staying LOCAL\n", file=sys.stderr)
        return answer_locally(prompt)

    if verbose:
        print("[router] → forwarding to CLOUD (Claude Code)\n", file=sys.stderr)
    return answer_with_claude_code(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hybrid_router.py '<your prompt>'")
        sys.exit(1)

    user_prompt = " ".join(sys.argv[1:])
    print(route(user_prompt))
