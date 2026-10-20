# Obedient Claude Skill: setup guide

## What this gives you

This package turns the working behavior you value in GPT-6.1 Sol in Work mode into an explicit Claude routine: take ownership of the task, use real tools, make focused changes, check the result, preserve decisions, and finish the requested deliverable.

It contains a short persistent agreement plus an extensive skill with ten detailed modules. The important distinction is scope: Claude should act independently on the work you authorized and ask before introducing a material change you did not authorize.

This is a behavioral setup, not a model conversion. It cannot give Claude another model's underlying abilities or access to a computer it is not connected to. The files are built and validated; they have not been installed into your own Claude environment from this session.

Use the local installer for Claude Code on the machine where the intended project is accessible. Use the account instructions and skill upload for ordinary Claude chat. For Cowork or cloud sessions, enable the account skill and use the environment's supported project/session instructions for the persistent agreement; do not assume local personal files are shared with the cloud. [Skill loading across environments](https://code.claude.com/docs/en/skills)

## Fastest setup with Claude Code

Open this repository checkout somewhere you can access from Claude Code, or extract a downloaded repository ZIP first. The earlier `claude-workstyle-kit.zip` distribution also works. Give Claude the actual folder path and paste the full contents of `INSTALL-WITH-CLAUDE.txt`.

That prompt authorizes the local installation, tells Claude to inspect the existing rules and installer, run a dry-run, and apply the kit if there is no meaningful unresolved conflict. It does not authorize changing your stack, providers, permission settings, or other projects.

An installer can preserve existing text; it cannot determine whether two natural-language instructions contradict each other. Resolve actual conflicts in your old rules rather than accumulating contradictory instructions. A broad review of every file on your computer is unnecessary.

## Manual Claude Code installation

The installer needs Python 3.10 or newer and uses only the standard library. Run it from the repository or extracted package root, where `tools/` and `instructions/` are present. Use the interpreter already available on your machine.

On Windows, if the Python launcher is installed:

```powershell
py -3 tools/install_claude.py
py -3 tools/install_claude.py --apply
```

On macOS, Linux, or WSL:

```bash
python3 tools/install_claude.py
python3 tools/install_claude.py --apply
```

The first command is a dry-run and writes nothing. The second applies the installation. If your working interpreter is named `python`, use that name instead after confirming its version.

The default destination is the current operating-system user's `.claude` directory. An installation in WSL belongs to the WSL user's environment; it is not automatically a native Windows installation. If your Claude setup uses a custom directory, pass its actual absolute path with `--config-dir` to both commands. The installer deliberately does not guess a custom location.

For example, an already-established custom Windows directory can be supplied as:

```powershell
py -3 tools/install_claude.py --config-dir 'C:\Users\YourName\claude-config' --apply
```

Replace the example with the directory your Claude installation actually uses.

### Installed layout

| Destination under the configuration directory | Purpose |
| --- | --- |
| `CLAUDE.md` | Your existing text plus this kit's clearly marked working-agreement section. |
| `skills/work-with-me/` | The skill, its reference modules, and two optional templates. |
| `work-with-me-backups/` | Original content retained before replacing existing material. Created only when a backup is needed. |

Personal instructions and skills use these standard Claude Code locations. [Official instruction locations](https://code.claude.com/docs/en/memory) · [Official skill locations](https://code.claude.com/docs/en/skills)

### Existing files and updates

The installer preserves every byte outside its marked instruction section. It supports UTF-8, a UTF-8 BOM, and LF/CRLF line endings. Unsupported encodings, invalid markers, or linked/junction paths produce an error before installation.

An unchanged second run does nothing. If you deliberately update this kit, review the differences and run:

```bash
python3 tools/install_claude.py --apply --update
```

Use the appropriate interpreter for Windows as above. Updates replace only this kit's owned instruction section and owned skill, with backups. A skill with the same name that was not installed by this installer is refused even with `--update`; inspect that collision instead of overwriting it.

The installer is intended for a single run while no other process edits those targets. Close or pause concurrent edits during installation. Native Windows execution was not tested in this Linux session, although the code includes Windows reparse-point checks.

### Confirm loading

Start a fresh Claude Code session. Check loaded instructions with `/context`, then invoke the skill explicitly:

```text
/work-with-me
```

Give it a real task. Confirm behavior through the result and tool evidence, not by asking Claude whether it promises to obey. Skill invocation is documented by Claude Code; automatic selection may still vary. [Skill invocation](https://code.claude.com/docs/en/skills)

If the command is not visible, inspect the current skill interface and actual directory. Check for a disabled skill, wrong configuration location, a duplicate/synced copy, or an old session. Do not install extra tooling to work around a simple path issue.

### Installation without Python

No new dependency is required to use the instructions themselves. Back up your existing personal `CLAUDE.md`, merge `instructions/CLAUDE.md` into it after resolving conflicts, and copy `skills/work-with-me` into your personal skills directory.

This manual copy is not marked as owned by the installer. Future automatic updates will refuse it; continue maintaining it manually or deliberately migrate after inspecting the existing files. Never overwrite an unrelated skill merely to make an installer succeed.

## Setup in ordinary Claude chat

Copy `instructions/CLAUDE-chat-preferences.txt` into **Settings → Instructions for Claude**. Merge it with your current preferences and remove any meaningful contradictions. This is the account-wide part of the setup. [Official personalization instructions](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features)

Open **Customize → Skills**, upload the included `work-with-me.zip`, and enable it where that feature is available in your account. Upload the skill-only ZIP, not the entire kit ZIP. It contains the single top-level `work-with-me` folder expected by the upload workflow. [Official custom-skill guidance](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)

Ask Claude to use Work With Me on a substantial task. Ordinary chat does not use the local installer's files merely because they exist on your computer. If skills are unavailable in your interface, the account preference block remains useful; you can attach the relevant Markdown routine for an individual task.

Choose one authoritative skill source and avoid conflicting local, uploaded, or synced versions.

For each project, adapt `instructions/PROJECT.template.md` to actual current facts. Do not paste unfilled placeholders into an active project's instructions or assume this general kit knows that project's architecture.

## What is inside

| Item | Use |
| --- | --- |
| `instructions/CLAUDE.md` | Persistent personal working agreement for Code. |
| `instructions/CLAUDE-chat-preferences.txt` | Paste-ready account preferences for Claude chat. |
| `instructions/PROJECT.template.md` | Project facts and constraints, filled from evidence. |
| `skills/work-with-me/SKILL.md` | Skill entry point and module routing. |
| `skills/work-with-me/references/` | Ten detailed workflows and examples. |
| `skills/work-with-me/assets/` | Optional task-state and decision templates. |
| `work-with-me.zip` | Skill-only upload package. |
| `INSTALL-WITH-CLAUDE.txt` | Prompt that asks Claude Code to perform the installation. |
| `tools/` | Installer and its isolated tests. |
| `evaluation/` | Twenty behavioral cases and a small-first comparison protocol. |
| `RESEARCH-AND-DESIGN.md` | Research findings, sources, decisions, and limits. |
| `NATIVE-CONTROLS.md` | Optional execution-permission guidance. |
| `VALIDATION.md` | What was actually checked before delivery. |

## Rollback

Remove only the block between `<!-- BEGIN WORK-WITH-ME v1 -->` and `<!-- END WORK-WITH-ME v1 -->` from your personal `CLAUDE.md`, preserving other text. Inspect any changes made after installation before restoring a whole-file backup.

Remove or move only the installed `skills/work-with-me` directory if you no longer want it. If an update replaced an earlier owned version, the installer reports the corresponding backup location; restore the relevant earlier content after reviewing current changes. The installer provides no automatic uninstall command, so no broad reset is implied.

For chat, remove or edit the copied account preferences and disable/remove the skill through the account interface. Restart the relevant session when checking the resulting configuration.

## First real check

Use a small real task that previously exposed the problem. Check whether Claude acts, preserves scope, verifies honestly, and returns the requested output. If it fails, record that particular trace and adjust the smallest relevant rule. Run three high-value evaluation cases before considering the full set; do not spend an entire session proving that a prompt exists.
