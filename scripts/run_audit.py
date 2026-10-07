#!/usr/bin/env python3
"""Send an audit pack to a model, and write the report back.

The audits in this repo are done by a model that did not write the code, and the
report is a file, not a conversation. This script is that pipe: it reads a pack
directory, sends the prompt and every file in the pack, and writes the answer
where the audit convention expects it.

It speaks the OpenAI chat-completions shape, so it can reach any endpoint that
does. The key is read from the operator's env file and is never printed, logged,
or written anywhere.

Run from the repo root:

    python3 scripts/run_audit.py <pack-dir> <out-file> [model]
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = Path("/Users/claudiobarone/Projects/OSINT WORKSPACE/.env")

# Both speak the OpenAI chat-completions shape. OpenRouter is the free lane and is
# tried first; DeepSeek is the paid fallback.
PROVIDERS = {
    "openrouter": ("https://openrouter.ai/api/v1/chat/completions", "OPENROUTER_API_KEY"),
    "deepseek": ("https://api.deepseek.com/chat/completions", "DEEPSEEK_API_KEY"),
}
DEFAULT_PROVIDER = "openrouter"

# Text the model should see, in the order it should read it. A binary or a lock
# file would only cost tokens.
SKIP_SUFFIX = {".png", ".jar", ".lock", ".db", ".bin"}


def api_key(name: str) -> str:
    if not ENV_FILE.exists():
        raise SystemExit(f"no env file at {ENV_FILE}")
    text = ENV_FILE.read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(name)}=(.*)$", text, re.M)
    if not match:
        raise SystemExit(f"{name} is not in the env file")
    return match.group(1).strip().strip('"').strip("'")


def collect(pack: Path) -> str:
    prompt = (pack / "audit_prompt.md").read_text(encoding="utf-8")
    parts = [prompt, "\n\n---\n\n# The files\n"]
    for path in sorted(pack.rglob("*")):
        if not path.is_file() or path.name == "audit_prompt.md":
            continue
        if path.suffix in SKIP_SUFFIX:
            continue
        relative = path.relative_to(pack)
        body = path.read_text(encoding="utf-8", errors="replace")
        parts.append(f"\n## {relative}\n\n```\n{body}\n```\n")
    return "".join(parts)


SYSTEM = (
    "You are a code auditor. You did not write this code. Answer with the requested "
    "structure and nothing else. Every claim needs a file and a line. If you cannot "
    "point at a line, say so instead of guessing. Do not explain the project."
)


def call(endpoint: str, key_name: str, model: str, body: str, thought_budget: int,
         exclude_thinking: bool) -> dict:
    """One completion. `thought_budget` is a hard cap on reasoning tokens."""
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": body},
        ],
        "temperature": 0,
        "max_tokens": 12000,
        # The whole reason earlier attempts failed. Left uncapped, a reasoning model
        # spends the entire output budget thinking and returns an empty answer. A
        # hard cap forces it to stop and write, and `exclude` keeps the thinking out
        # of the reply so the budget goes to the answer.
        "reasoning": {"max_tokens": thought_budget, "exclude": exclude_thinking},
    }).encode("utf-8")
    request = urllib.request.Request(endpoint, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key(key_name),
        "HTTP-Referer": "https://github.com/cemini23/basgiath",
        "X-Title": "Basgiath port audit",
    })
    with urllib.request.urlopen(request, timeout=900) as response:
        return json.load(response)


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    pack = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    model = sys.argv[3] if len(sys.argv) > 3 else ""
    provider = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_PROVIDER
    if provider not in PROVIDERS:
        raise SystemExit(f"unknown provider {provider!r}; known: {sorted(PROVIDERS)}")
    if not model:
        raise SystemExit("name a model, e.g. anthropic/claude-sonnet-4.5")
    endpoint, key_name = PROVIDERS[provider]
    if not pack.is_dir():
        raise SystemExit(f"no pack at {pack}")

    body = collect(pack)
    print(f"pack {pack.name}: {len(body)} chars, model {model}")

    # Three attempts, each with more room to think. The first is the one that
    # normally works; the others exist so a stubborn model is not simply lost.
    attempts = [(2500, True), (8000, True), (20000, False)]
    report, usage, note = "", {}, ""
    for budget, exclude in attempts:
        try:
            result = call(endpoint, key_name, model, body, budget, exclude)
        except urllib.error.HTTPError as error:
            raise SystemExit(f"the endpoint refused it: {error.code} {error.read()[:400]!r}")
        message = result["choices"][0]["message"]
        usage = result.get("usage", {})
        text = (message.get("content") or "").strip()
        if text:
            report = text
            break
        note = f"empty answer at thought_budget={budget}"

    if not report:
        report = f"<!-- {note}; the model never answered. -->"

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"<!-- model={model} pack={pack.name} usage={usage} -->\n\n{report}\n",
                   encoding="utf-8")
    print(f"wrote {out} ({len(report)} chars, usage {usage})")


if __name__ == "__main__":
    main()
