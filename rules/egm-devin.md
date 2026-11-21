---
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
