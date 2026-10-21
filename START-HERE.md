# Setup and maintenance

The portable skill is `work-with-me`. Its detailed routines work with a compact persistent agreement; project facts remain separate. Start with the [README](README.md) for the shortest installation path.

## Claude Code

Open this checkout or an extracted repository ZIP in Claude Code and give it [INSTALL-WITH-CLAUDE.txt](INSTALL-WITH-CLAUDE.txt). That prompt authorizes this installation after inspection and a dry-run, not changes to your permissions, providers, or projects.

For manual installation, use an existing Python 3.10+ interpreter from the repository root:

```bash
python3 tools/install_claude.py
python3 tools/install_claude.py --apply
```

On Windows, use `py -3` instead of `python3`. A suitable interpreter named `python` also works. The first command is read-only. Review the paths and meaningful conflicts in existing instructions before applying. Do not install extra tooling merely to use the Markdown skill.

### What changes

| Default location | Purpose |
| --- | --- |
| `~/.claude/CLAUDE.md` | Adds the kit's marked agreement, preserving text outside its block. |
| `~/.claude/skills/work-with-me/` | Installs the entry point, detailed references, and templates. |
| `~/.claude/work-with-me-backups/` | Saves originals before replacing existing content when required. |

The installer does not alter models, providers, permission settings, other skills, or project repositories. It preserves UTF-8/BOM and LF/CRLF text outside its own block. Unsupported encodings, invalid markers, and linked/junction paths are refused. It cannot reconcile contradictory natural-language rules for you.

The destination belongs to the operating-system user running the command. WSL and native Windows are separate environments. For an established custom directory, add its actual absolute path to both commands:

```powershell
py -3 tools/install_claude.py --config-dir 'C:\Users\YourName\claude-config'
py -3 tools/install_claude.py --config-dir 'C:\Users\YourName\claude-config' --apply
```

Replace the example path. Use a real directory rather than a symlink alias. Avoid concurrent edits to the installation targets.

### Confirm loading

Start a fresh Claude Code session, inspect loaded instructions with `/context`, and invoke `/work-with-me` with a task. A file on disk alone is not proof that a session loaded it. If absent, check the actual configuration directory, active skill interface, disabled or duplicate copies, and old sessions before adding tooling.

[Official memory locations](https://code.claude.com/docs/en/memory) · [Official skills documentation](https://code.claude.com/docs/en/skills)

## Updating

Obtain the new source and review its changes. Preview an owned installation update, then apply it:

```bash
python3 tools/install_claude.py --update
python3 tools/install_claude.py --update --apply
```

Use the same custom `--config-dir`, if applicable. The installer backs up replaced content, updates only its owned skill and agreement block, and makes unchanged repeats a no-op. It refuses an unrelated existing `work-with-me` skill even with `--update`. Resolve that collision deliberately; do not overwrite someone else's skill to make installation succeed.

The owner-specific defaults include English responses and no extra agents without authorization. Review these preferences when adapting the kit for another person.

## Without Python

Back up your personal `CLAUDE.md`, merge [the agreement](instructions/CLAUDE.md) after resolving conflicts, and copy `skills/work-with-me` into the personal skills directory. This manual copy has no installer ownership marker: maintain it manually or deliberately migrate after inspection. Do not create a fake ownership marker to bypass collision protection.

## Claude chat, Cowork, and cloud sessions

Upload [work-with-me.zip](work-with-me.zip) through **Customize → Skills** and enable it where supported. Upload the skill-only archive, not a ZIP of the repository. Merge [the chat preferences](instructions/CLAUDE-chat-preferences.txt) into **Settings → Instructions for Claude** where that surface is available. Ask Claude to use Work With Me on the next substantial task.

Cowork/cloud sessions use their supported account or project instructions and skills; they do not simply read a local personal installation. Keep one authoritative version and avoid conflicting synced and local copies. If custom skills are unavailable, use the preference block and attach the relevant Markdown routine for the task.

[Official custom-skill upload](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) · [Account instructions](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features)

Fill the [project template](instructions/PROJECT.template.md) with actual current facts before putting it into active project instructions. Do not import the entire handbook into persistent context.

## Rollback

Remove only the section between `<!-- BEGIN WORK-WITH-ME v1 -->` and `<!-- END WORK-WITH-ME v1 -->` from personal `CLAUDE.md`. Preserve other content and any edits made since installation. Remove only the installed `skills/work-with-me` directory, or restore a reviewed earlier owned version from the backup path the installer reported. There is no broad reset or automatic uninstall.

For chat, edit the copied preferences and disable/remove the uploaded skill through the account interface. Check the result in a fresh session.

## Evaluate without wasting usage

Start with a real task that previously failed. Check completion, scope, honest verification, and unnecessary permission questions—not whether Claude promises to follow instructions. Use the [focus comparison protocol](evaluation/FOCUS-EVALUATION.md) for current-versus-revised testing. Authored cases are not measured performance results. Do not run the entire suite or change model settings automatically.

## Optional project-local ecosystem installation

The [skills CLI path](docs/ECOSYSTEM-INSTALL.md) installs only the portable skill, not the standing agreement. Do not mix managers at one destination. The normal full installer and ZIP remain available without Node.js.
