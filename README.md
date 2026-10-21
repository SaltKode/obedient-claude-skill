# Obedient Claude Skill

**Less wandering. More finished work.**

A practical workflow for Claude that keeps coding, research, design, and writing focused on the task you actually asked for.

Claude should make normal technical decisions, use its tools, and finish the job—not ask permission for every edit or invent an unrelated project along the way.

## Latest update

**21 October 2026 — CodeQL test-fixture fix**

Addressed the clear-text-storage finding in `tools/test_install_claude.py`: the fixture now clearly identifies its content as public, synthetic test data—not real credentials. Strengthened checks confirm that file contents are not echoed to either output stream when installation fails, and that the original file remains unchanged. All **45 offline tests passed**, and the follow-up CodeQL analysis completed successfully. Installer behavior and security-scanning rules are unchanged.

[Fix and patch](https://github.com/SaltKode/obedient-claude-skill/commit/6c5ca74c89b2873714115d699df6cca047f3001d) · [Quality checks](https://github.com/SaltKode/obedient-claude-skill/actions/runs/39533629370) · [CodeQL analysis](https://github.com/SaltKode/obedient-claude-skill/actions/runs/39533629133)

## 🎯 What it improves

| Benefit | How the skill guides Claude |
| --- | --- |
| **Independent execution** | Carry out necessary steps and reuse decisions you have already approved. |
| **Fewer sidequests** | Skip unrelated rewrites, cleanup, new services, and speculative features. |
| **Focused debugging** | Diagnose the actual cause, make targeted changes, and preserve working behavior. |
| **Reliable delivery** | Run relevant checks, report real results, and return the complete output you requested. |
| **Better continuity** | Retain corrections, decisions, language preferences, and handoff boundaries. |
| **Useful research and UI work** | Respect hard constraints, support claims with evidence, and follow the actual visual reference. |

**Autonomous within the task. Ask only for a genuinely missing decision.** Unnecessary work should be skipped—not turned into more approval questions.

## ⚡ How it targets wasted tokens

The routine uses a compact working agreement and loads detailed guidance only when needed. It encourages targeted reads and edits, batching independent tool calls, reusing still-valid findings and checks, concise diagnostics, and stopping when the job is done.

The goal is to remove wasted work, not reduce reasoning quality. It does not change your model or effort settings, skip required tests, shorten requested deliverables, or launch extra agents without authorization. Token savings depend on the task; compare actual runs with the [focus evaluation guide](evaluation/FOCUS-EVALUATION.md).

## 🚀 Install

### Claude Code — let Claude handle it

Download this repository using **Code → Download ZIP**, extract it, and open the folder in Claude Code. Then paste:

```text
Read INSTALL-WITH-CLAUDE.txt and install this skill.
Run the dry-run first, preserve my existing instructions,
and apply the installation if there is no unresolved conflict.
```

The installer needs **Python 3.10+**, uses no third-party Python packages, and preserves existing instructions with backups when replacing content. It does not change permissions, models, or other skills.

Start a fresh session, then use:

```text
/work-with-me Fix the issue and verify the result.
```

<details>
<summary>Prefer terminal commands?</summary>

Run from the downloaded or cloned repository folder.

**macOS / Linux / WSL**

```bash
python3 tools/install_claude.py
python3 tools/install_claude.py --apply
```

**Windows**

```powershell
py -3 tools/install_claude.py
py -3 tools/install_claude.py --apply
```

The first command previews changes without writing files. Review it before applying. For an existing installation, add `--update` to both commands after reviewing the changes. Custom locations and rollback are explained in [START-HERE.md](START-HERE.md).

</details>

For a project-local **skill-only** installation through the skills CLI, see [the optional ecosystem setup](docs/ECOSYSTEM-INSTALL.md). Keep one installation manager per destination.

### Claude chat / Cowork

1. Download the [skill-only ZIP](https://github.com/SaltKode/obedient-claude-skill/raw/refs/heads/main/work-with-me.zip).
2. Open **Customize → Skills**, upload it, and enable **Work With Me**.
3. For the standing preferences, merge [this instruction block](instructions/CLAUDE-chat-preferences.txt) into **Settings → Instructions for Claude**, where available.

Use one authoritative skill copy. Local Code files are not automatically available in a cloud session. [Full setup guide](START-HERE.md).

## Inside the kit

Ten on-demand modules cover scope, coding, UI, research, writing, efficiency, recovery, communication, tools, and practical examples. You also get project and handoff templates, a dry-run-first installer, an uploadable ZIP, and **37 task scenarios and 8 activation probes**, plus an optional budgeted comparison runner for maintainers.

The repository name is **Obedient Claude Skill**; the installed skill and command remain **`work-with-me`** and **`/work-with-me`**.

## Development

The [quality workflow](.github/workflows/quality.yml) checks the installer and packaging on Linux, Windows, and macOS, including Python 3.10 and 3.14 configurations. It also checks local documentation links, evaluation structure, instruction-size limits, and ZIP/source consistency.

```bash
python3 -B -m unittest discover -s tools -p 'test_*.py' -v
python3 -B tools/check_repository.py
```

The optional [trial runner](evaluation/TRIALS.md) previews comparisons without calling a model. Paid runs require explicit execution, limits, and an isolated environment; ordinary CI remains offline and Python-only.

See [comparison-informed improvements](docs/COMPARISON-IMPROVEMENTS.md), [maintenance and workflow decisions](docs/MAINTAINING.md), [evaluation](evaluation/FOCUS-EVALUATION.md), and the [validation record](VALIDATION.md).

## License

[GNU AGPL v3](LICENSE).
