# Hybrid routing policy

This project uses a local Ollama instance exposed via MCP (`ollama-local`
server). Follow these rules strictly.

## Rule 1 — Classify before analyzing

Before analyzing ANY user-provided code snippet, document, data file,
log, or other free-form text:

1. Call `classify_sensitivity(text)` from the `ollama-local` MCP server.
2. If the result is `"sensitive"`:
   - DO NOT include the raw text in any subsequent prompt or tool call
     that touches the cloud (Read is fine, Bash on local files is fine —
     the restriction is on data that would be re-sent as prompt context).
   - Call `summarize_locally(text)` to get a safe gist.
   - Reference findings by the summary, not by the raw snippet.
3. If the result is `"safe"`:
   - Proceed normally with built-in tools.

## Rule 2 — Private embeddings use local

For any embedding operation over private, internal, or client-provided
text, use `embed_locally(text)` instead of cloud embedding services.

Public web content and OSS documentation can use cloud embeddings
without restriction.

## Rule 3 — Model availability

Before planning a workflow that depends on a specific local model
(code model, vision model, embedding model), call `list_local_models()`
to confirm what is installed. Do not assume availability.

## Rule 4 — Report routing decisions

When a routing decision affects the user (e.g. a sensitive snippet
was summarized instead of analyzed directly), say so in one sentence:

> "I noticed the snippet contains sensitive data, so I'm working from
>  a local summary instead of the raw text."

This keeps the user aware of what left the machine and what did not.
