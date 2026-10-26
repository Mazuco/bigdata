"""Pattern 2 — MCP bridge exposing local Ollama as tools for any MCP client
(Claude Code, custom agents, other LLM apps).

Install:
    pip install mcp ollama

Register in Claude Code by adding this to .mcp.json in your project:

    {
      "mcpServers": {
        "ollama-local": {
          "command": "python",
          "args": ["/absolute/path/to/ollama_mcp_server.py"],
          "env": {
            "OLLAMA_HOST": "http://localhost:11434"
          }
        }
      }
    }

Then in Claude Code: `/mcp` lists it. Tools become callable by the agent.
"""
from __future__ import annotations

import json
import os

import ollama
from mcp.server.fastmcp import FastMCP

OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
LOCAL_CHAT_MODEL = os.getenv("LOCAL_CHAT_MODEL", "llama3.2:3b")
LOCAL_EMBED_MODEL = os.getenv("LOCAL_EMBED_MODEL", "nomic-embed-text")

client = ollama.Client(host=OLLAMA_URL)

mcp = FastMCP("ollama-local-bridge")


# ─────────────────────────────────────────────────────────────────────────────
# Tool 1 — Summarize locally (keeps raw text off the cloud)
# ─────────────────────────────────────────────────────────────────────────────
@mcp.tool()
def summarize_locally(text: str, max_sentences: int = 3) -> str:
    """Summarize a piece of text using the LOCAL Ollama model.

    USE THIS when the text contains sensitive data (PII, internal code,
    NDA material, credentials, infrastructure names). The raw text never
    leaves this machine — only the summary comes back, which you can
    then safely reason about.

    Args:
        text: The text to summarize (can be long).
        max_sentences: Target length of the summary (default 3).

    Returns:
        A short summary written in English.
    """
    prompt = f"Summarize the following in {max_sentences} sentences, in English:\n\n{text}"
    r = client.generate(
        model=LOCAL_CHAT_MODEL,
        prompt=prompt,
        options={"temperature": 0.1},
    )
    return r["response"].strip()


# ─────────────────────────────────────────────────────────────────────────────
# Tool 2 — Classify sensitivity (gatekeeper before cloud calls)
# ─────────────────────────────────────────────────────────────────────────────
_CLASSIFIER_SYSTEM = """You are a security classifier. Return ONLY valid JSON.

Classify the user input as 'safe' or 'sensitive'.

Sensitive = contains any of:
- API keys, tokens, passwords, credentials
- Personal data (CPF, SSN, email, phone, address of real people)
- Internal company data (internal URLs, class names, NDA material)
- Medical, legal, financial data of third parties
- Code snippets that look proprietary

Safe = generic programming questions, public info, textbook algorithms.

Format: {"level": "safe"|"sensitive", "reason": "<one sentence>"}
"""


@mcp.tool()
def classify_sensitivity(text: str) -> dict:
    """Classify whether a piece of text contains sensitive data.

    CALL THIS BEFORE processing any user-provided code snippet, document,
    or data to decide if it is safe to analyze with cloud tools or if
    it must stay on-device.

    Args:
        text: The text to classify.

    Returns:
        {"level": "safe" | "sensitive", "reason": "<one sentence>"}
    """
    r = client.chat(
        model=LOCAL_CHAT_MODEL,
        messages=[
            {"role": "system", "content": _CLASSIFIER_SYSTEM},
            {"role": "user", "content": text},
        ],
        format="json",
        options={"temperature": 0.0},
    )
    try:
        return json.loads(r["message"]["content"])
    except json.JSONDecodeError:
        # Default to the safer choice when the classifier misbehaves
        return {"level": "sensitive", "reason": "classifier output malformed"}


# ─────────────────────────────────────────────────────────────────────────────
# Tool 3 — Embed locally (for private semantic search / RAG)
# ─────────────────────────────────────────────────────────────────────────────
@mcp.tool()
def embed_locally(text: str) -> list[float]:
    """Create a 768-dimensional embedding using local nomic-embed-text.

    USE THIS instead of any cloud embedding service when the text
    comes from a private corpus (internal docs, confidential sources,
    client data). The text never leaves this machine.

    Args:
        text: The text to embed.

    Returns:
        A 768-float list representing the embedding vector.
    """
    r = client.embeddings(model=LOCAL_EMBED_MODEL, prompt=text)
    return r["embedding"]


# ─────────────────────────────────────────────────────────────────────────────
# Tool 4 — List models available locally
# ─────────────────────────────────────────────────────────────────────────────
@mcp.tool()
def list_local_models() -> list[str]:
    """List all models currently installed on the local Ollama instance.

    Call this when the agent needs to know which models are available
    before planning a workflow (e.g. is there an embedding model? a code model?).

    Returns:
        A list of model names (e.g. ["llama3.2:3b", "nomic-embed-text", ...]).
    """
    models = client.list()
    return [m.model for m in models.models]


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run()
