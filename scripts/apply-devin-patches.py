#!/usr/bin/env python3
"""Apply the Devin CLI packaging patches to this EGM checkout.

Idempotent. Run after merging upstream:

    git fetch upstream
    git merge upstream/main
    python3 scripts/apply-devin-patches.py

The patch has three parts:

1. Remove the plugin-root AGENTS.md. Devin injects it as an always-on rule in
   every session, and upstream's file is contributor guidance for the EGM
   repository rather than instructions for using EGM.
2. Restrict the shared persona files under agents/ with Devin's allowed-tools
   frontmatter. Reviewers are read-only; the synthesizer and bootstrap
   orchestrator keep the tools they need to write reports and README files.
3. Write rules/egm-devin.md, which maps the skills' persona names
   (egm-zoom-out) to Devin's plugin-namespaced profiles (egm:egm-zoom-out).
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / "agents"
RULES_DIR = ROOT / "rules"

READ_ONLY = ["read", "grep", "glob"]
SYNTHESIZER_TOOLS = [
    "read", "grep", "glob", "edit", "run_subagent", "read_subagent",
]
BOOTSTRAP_TOOLS = [
    "read", "grep", "glob", "exec", "edit", "run_subagent", "read_subagent",
]

RULE = """---
trigger: model_decision
description: Use when running an EGM (Elephant-Goldfish Model) skill or spawning an EGM Goldfish reviewer in the Devin CLI.
---

# EGM delegation in the Devin CLI

EGM personas are registered as plugin subagent profiles named `egm:<persona>`.
For example, the `egm-zoom-out` persona is the `egm:egm-zoom-out` profile.

When an EGM skill tells you to spawn a reviewer:

1. Call `run_subagent` with the matching `egm:egm-<persona>` profile.
2. If that profile is unavailable, call `run_subagent` with the built-in
   `subagent_explore` profile and tell the subagent to read `agents/<persona>.md`
   from the EGM plugin first. Resolve that path from the EGM plugin root, the
   parent of the running skill's `skills/<name>/` folder.
3. Never use `subagent_general` for a Goldfish reviewer. Reviewers are read-only;
   `subagent_general` can write.
4. Never resume a reviewer. Every review needs a fresh context.
5. Reviewers return findings as text. Only the parent writes files, and only the
   artifacts the workflow asks for after the user approves.
"""


def frontmatter_bounds(lines: list[str]) -> tuple[int, int]:
    if not lines or lines[0].strip() != "---":
        raise ValueError("expected frontmatter on the first line")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return 0, index
    raise ValueError("unterminated frontmatter")


def patch_persona(path: pathlib.Path) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    start, end = frontmatter_bounds(lines)
    block = lines[start + 1:end]
    if any(line.split(":", 1)[0].strip() == "allowed-tools" for line in block):
        return False

    if path.name == "synthesizer.md":
        tools, nesting = SYNTHESIZER_TOOLS, 2
    elif path.name == "bootstrap_orchestrator.md":
        tools, nesting = BOOTSTRAP_TOOLS, 2
    else:
        tools, nesting = READ_ONLY, None

    addition = ["allowed-tools:"] + [f"  - {tool}" for tool in tools]
    if nesting is not None:
        addition.append(f"max-nesting: {nesting}")

    lines[end:end] = addition
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def main() -> int:
    agents = ROOT / "AGENTS.md"
    if agents.exists():
        agents.unlink()
        print(f"removed {agents.relative_to(ROOT)}")

    changed = []
    for persona in sorted(AGENTS_DIR.glob("*.md")):
        if patch_persona(persona):
            changed.append(persona.name)
    for name in changed:
        print(f"patched agents/{name}")
    if not changed:
        print("agents/ already patched")

    RULES_DIR.mkdir(exist_ok=True)
    rule = RULES_DIR / "egm-devin.md"
    if not rule.exists() or rule.read_text(encoding="utf-8") != RULE:
        rule.write_text(RULE, encoding="utf-8")
        print(f"wrote {rule.relative_to(ROOT)}")
    else:
        print(f"{rule.relative_to(ROOT)} already current")

    return 0


if __name__ == "__main__":
    sys.exit(main())
