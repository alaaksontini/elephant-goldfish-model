# EGM for the Devin CLI

An unofficial fork of
[google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model)
that packages the Elephant-Goldfish Model (EGM) for the
[Devin CLI](https://devin.ai/cli).

Upstream EGM targets Antigravity, Claude Code, and Codex. Devin can load the
upstream plugin through its Claude-compatible manifest, but three Devin-specific
problems make that unsafe:

1. **The plugin injects an always-on contributor rule.** Devin treats a plugin
   root `AGENTS.md` as an always-on rule in every session. Upstream's
   `AGENTS.md` is guidance for contributing to the EGM repository, not for using
   EGM, so it would be applied to every project you open. This fork removes it.
2. **Reviewers can write.** Claude gets separate adapters with
   `tools: [Read, Grep, Glob]`. Devin loads the shared `agents/*.md` personas
   directly, and a persona without `allowed-tools` gets every tool, including
   file edits and shell. This fork restricts the eight reviewer personas to
   `read`, `grep`, and `glob`.
3. **Reviewer names do not resolve.** The skills ask for `egm-zoom-out`; Devin
   namespaces plugin agents as `egm:egm-zoom-out`. This fork adds a
   `model_decision` rule that maps the names and requires the built-in
   `subagent_explore` profile as the fallback.

## Install

Requires the Devin CLI and a signed-in account.

```sh
devin plugins install alaaksontini/elephant-goldfish-model
```

If you already installed the upstream plugin, remove it first so the plugin name
`egm` does not collide:

```sh
devin plugins remove egm
devin plugins install alaaksontini/elephant-goldfish-model
```

Verify the install:

```sh
devin plugins info egm
```

Expected: 8 skills, 10 agent profiles, and one agent-decided rule
(`rules/egm-devin.md`). There should be no always-on `AGENTS.md` rule.

## Use

Start a Devin CLI session and run an EGM command:

```text
/egm:egm-review docs/designs/webhooks.md
```

| Command | What it does |
| --- | --- |
| `/egm:egm-brainstorm` | Explore an idea and write a concepts brief. |
| `/egm:egm-draft` | Turn a brief into a design document, section by section. |
| `/egm:egm-review` | Run the Goldfish review protocol on a document. |
| `/egm:egm-review-loop` | Run the automated review-and-fix loop. |
| `/egm:egm-resolve` | Apply approved fixes from reviewer findings. |
| `/egm:egm-drift-report` | Compare design documents with the code. |
| `/egm:egm-lite` | Run the lightweight 5-step EGM protocol. |
| `/egm:egm-bootstrap` | Generate README files across a repository subtree. |

See the upstream
[workflow guide](https://github.com/google/elephant-goldfish-model/blob/main/docs/getting_started.md)
for the full process.

## Reviewer isolation

Goldfish reviews need a fresh context and read-only reviewers.

- The eight reviewer personas have `allowed-tools: [read, grep, glob]`.
- The synthesizer can read, write the report, and spawn reviewers
  (`max-nesting: 2`).
- The bootstrap orchestrator can read, run shell commands, write README files,
  and spawn workers (`max-nesting: 2`).
- `rules/egm-devin.md` tells the parent to use `egm:egm-<persona>`, never
  `subagent_general`, and never resume a reviewer.
- Only the parent writes the artifacts the workflow asks for.

Devin does not have Claude's `omitClaudeMd: true`, so project or global rules
may still reach a reviewer's context. Conversation history is not inherited.

## Differences from upstream

| | Upstream | This fork |
| --- | --- | --- |
| Plugin-root rule | always-on contributor `AGENTS.md` | removed |
| Reviewer tools in Devin | full access | read-only |
| Reviewer names | `egm-<persona>` | `egm:egm-<persona>` via rule |
| Devin support | experimental `.windsurf` routing | plugin install |

## Maintaining this fork

The fork tracks upstream `main`. The Devin changes are kept in
`scripts/apply-devin-patches.py`, which is idempotent:

```sh
git remote add upstream https://github.com/google/elephant-goldfish-model.git  # once
git fetch upstream
git merge upstream/main
python3 scripts/apply-devin-patches.py
git push origin main
devin plugins update egm
```

The script removes `AGENTS.md`, adds `allowed-tools` to any persona that lacks
it (read-only by default), and writes `rules/egm-devin.md`. Review the diff
after an upstream merge, especially if upstream adds a write-capable persona.

If upstream adds native Devin support, this fork becomes unnecessary.

## Attribution

Apache-2.0. The skills, personas, standards, and documentation come from
[google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model).
This fork changes only the Devin packaging. See the upstream
[README](https://github.com/google/elephant-goldfish-model#readme) and
[docs](https://github.com/google/elephant-goldfish-model/tree/main/docs).

Not affiliated with Google.
