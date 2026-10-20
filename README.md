# Obedient Claude Skill

An extensive, modular collaboration routine for Claude: take ownership of the task, work within the agreed scope, use available tools, verify the result, and finish the requested deliverable.

The design follows the working habits the user values in **GPT-6.1 Sol in Work mode**. It gives Claude an explicit working agreement and practical routines for coding, building interfaces, research, writing, and sustained work. Model capabilities and tool access still depend on the Claude environment you use.

**The repository is named Obedient Claude Skill. The portable skill keeps its internal name `work-with-me`, and its Claude Code command is `/work-with-me`.**

## What it is designed to improve

- **Task ownership:** carry an implementation request through to a usable result; produce the requested analysis when the task is research, review, or planning.
- **Scope discipline:** preserve the selected stack, existing work, and accepted decisions. Seek a decision before an unapproved material change, while reusing authorization already given. Explicit new-project stack selection includes its necessary local dependencies.
- **Focused repairs:** fix a narrow defect without turning it into an unrelated rewrite.
- **Honest verification:** distinguish inspected source, executed checks, rendered screenshots, and completed external actions. Report missing capabilities accurately.
- **Continuity:** incorporate corrections, answer status questions, and resume the active task without losing earlier requirements.
- **Proportionate effort:** keep small tasks focused, give deep requests appropriate substance, and avoid redundant research, testing, or delegation.
- **Complete delivery:** honor full-code-in-chat requests, supplied UI references, and requested files or archives.

A short persistent agreement establishes the everyday defaults. The skill adds **ten detailed reference modules**, loaded as relevant, plus optional task-state and decision templates. A separate project template keeps project facts out of the general routine. See [the research and design rationale](RESEARCH-AND-DESIGN.md).

## Install in Claude Code

Download or clone this repository and open a terminal in its root directory. The installer requires **Python 3.10 or newer** and uses only the standard library.

### macOS, Linux, or WSL

```bash
python3 tools/install_claude.py
python3 tools/install_claude.py --apply
```

### Windows with the Python launcher

```powershell
py -3 tools/install_claude.py
py -3 tools/install_claude.py --apply
```

The **first command is a dry-run and writes nothing**. Review its destination and planned changes, along with any conflicting existing instructions, before running the second command. If your suitable interpreter is named `python`, use that name instead.

By default, the destination is the current operating-system user's `~/.claude` directory:

| Installed item | Purpose |
| --- | --- |
| `CLAUDE.md` | Adds this kit's clearly marked working-agreement section while preserving existing text outside it. |
| `skills/work-with-me/` | Installs the skill, reference modules, and templates. |
| `work-with-me-backups/` | Retains existing content when a backup is needed. |

For an established custom configuration directory, supply its **absolute path** with `--config-dir` to both commands. The installer does not infer a custom location. A WSL installation belongs to the WSL user's environment; native Windows uses its own environment.

An unchanged repeat makes no changes. For a reviewed update, preview with `--update`, then apply with `--apply --update`. The installer refuses an unrelated existing skill named `work-with-me`, including when `--update` is supplied. It manages only its own instruction section and owned skill; it does not change permission settings, providers, or project stacks.

Start a fresh Claude Code session, inspect loaded instructions with `/context`, and invoke:

```text
/work-with-me
```

Then give Claude a real task. Explicit invocation provides a clear starting point; automatic skill selection can vary. [Official instruction locations](https://code.claude.com/docs/en/memory) · [Official skill loading and invocation](https://code.claude.com/docs/en/skills)

For an installation prompt you can give Claude Code, use [INSTALL-WITH-CLAUDE.txt](INSTALL-WITH-CLAUDE.txt). For custom paths, manual installation without Python, conflict handling, updates, and rollback, see [START-HERE.md](START-HERE.md).

## Use in Claude web or Cowork

The ready-to-upload skill archive is **[work-with-me.zip](work-with-me.zip)** at the repository root. Its single top-level `work-with-me/` folder contains the skill and supporting files. Upload this skill-only archive rather than a ZIP of the entire repository.

### Claude web

1. Copy [instructions/CLAUDE-chat-preferences.txt](instructions/CLAUDE-chat-preferences.txt) into **Settings → Instructions for Claude**. Merge it with your existing preferences and resolve meaningful contradictions.
2. Open **Customize → Skills**, upload `work-with-me.zip`, and enable it where custom skills are available in your account.
3. Ask Claude to use **Work With Me** on a substantial task. Add current project facts using [PROJECT.template.md](instructions/PROJECT.template.md), filling the template before placing it in active project instructions.

[Official personalization guidance](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features) · [Official custom-skill upload guidance](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)

### Cowork and cloud sessions

Enable the uploaded skill through the account's supported skills interface. Supply the working agreement through the environment's supported project or session instructions for the intended workspace. Confirm what that session actually loads; a local Claude Code installation does not by itself establish that a cloud session has those files or preferences. [Skill loading across environments](https://code.claude.com/docs/en/skills)

If custom skills are unavailable in the interface, use the preference block and attach the relevant Markdown routine to the task. Keep one authoritative skill version so uploaded, local, and synced copies do not drift into conflicting instructions.

## Repository guide

| File or directory | Contents |
| --- | --- |
| [START-HERE.md](START-HERE.md) | Complete setup, maintenance, troubleshooting, and rollback instructions. |
| [instructions/CLAUDE.md](instructions/CLAUDE.md) | Persistent Claude Code working agreement. |
| [instructions/CLAUDE-chat-preferences.txt](instructions/CLAUDE-chat-preferences.txt) | Paste-ready account preferences. |
| [instructions/PROJECT.template.md](instructions/PROJECT.template.md) | Project-specific facts, constraints, and decisions. |
| [skills/work-with-me/SKILL.md](skills/work-with-me/SKILL.md) | Portable skill entry point and reference routing. |
| [skills/work-with-me/references/](skills/work-with-me/references/) | Ten modules covering scope, coding, UI, research, writing, efficiency, continuity, communication, tools, and calibration examples. |
| [skills/work-with-me/assets/](skills/work-with-me/assets/) | Optional task-state and decision templates. |
| [work-with-me.zip](work-with-me.zip) | Skill-only upload package. |
| [tools/install_claude.py](tools/install_claude.py) | Dry-run-first local installer. |
| [tools/test_install_claude.py](tools/test_install_claude.py) | Installer tests using temporary destinations. |
| [evaluation/README.md](evaluation/README.md) | Manual Claude comparison protocol and twenty behavioral cases. |
| [RESEARCH-AND-DESIGN.md](RESEARCH-AND-DESIGN.md) | Design decisions, alternatives considered, and official sources. |
| [NATIVE-CONTROLS.md](NATIVE-CONTROLS.md) | Separate guidance on actual execution permissions and their limits. |
| [VALIDATION.md](VALIDATION.md) | Executed checks and explicit validation limits. |

## Validation and practical limits

The [validation record](VALIDATION.md) documents **15 passing installer tests in temporary Linux directories**, skill-format checks, and a dry-run of the actual kit. A separate small coding exercise used a GPT-family agent. These checks establish properties of the package and installer; they do not establish Claude's behavioral effectiveness.

To run the included installer tests locally:

```bash
python3 -B tools/test_install_claude.py
```

Use the appropriate Python launcher on Windows. To assess Claude's behavior, follow [the manual evaluation protocol](evaluation/README.md): begin with three high-value cases, keep the model, tools, settings, and inputs comparable, and record actual outputs and tool traces. Change the smallest relevant rule when a concrete failure justifies it.

## License

This repository uses the [GNU Affero General Public License, version 3](LICENSE).
