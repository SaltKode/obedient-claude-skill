# Optional skills CLI installation

The normal Python installer remains the **full setup**: standing agreement plus portable skill. The ZIP path needs no Node.js. The optional skills CLI path installs **only the skill** for one project; it does not install `instructions/CLAUDE.md` or the chat preferences.

From the target project, inspect discovery before installation:

```bash
npx skills@1.7.4 add SaltKode/obedient-claude-skill --list
npx skills@1.7.4 add SaltKode/obedient-claude-skill --skill work-with-me -a claude-code --copy
```

This CLI version requires Node.js 22.20+. The first invocation may download the CLI. The explicit version makes the distribution procedure reviewable; review newer CLI releases before upgrading it. The skill source is the repository's current default branch, not frozen by the CLI version. Review the source separately. Interactive installation is intentional; `--yes` is not needed for the normal setup.

## Keep ownership clear

Choose one installation manager per destination. Before using this path, check whether the project or your personal configuration already contains `work-with-me`. Do not put a second competing copy alongside a full installation or run one manager over another manager's target. This CLI does not inherit our Python installer's collision guarantees.

A skills-CLI copy has no `.work-with-me-owned` marker. Our installer will refuse to replace that copy if you target the same configuration directory. Do not forge the marker. To migrate, back up custom changes and deliberately remove or move the old managed copy before using the new manager. Preserve unrelated instructions.

Use the same CLI and source to review/reinstall an update, or its supported update commands after checking their target scope. Do not run a broad update of every installed skill merely to update this one. With `--copy`, source edits do not silently update the installed copy.

The tested layout is project-local `.claude/skills/work-with-me/`. Keep the standing agreement separately in your project instructions if you need it, after resolving existing conflicts. A successful filesystem installation is not proof of live Claude activation.

## Smoke testing

A maintainer should test listing, installation, repeated installation, source-content updates, and preservation of unrelated files in a disposable project. Compare every installed skill file with the selected source. Verify that no standing agreement or installer ownership marker was silently created. Never use a real project as the smoke fixture.

See the dated execution record in [VALIDATION.md](../VALIDATION.md). The optional path is not part of ordinary CI, which stays Python-only and does not fetch npm packages or call Claude.

[Official CLI source](https://github.com/vercel-labs/skills) · [Commands](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) · [Discovery layout](https://github.com/vercel-labs/skills/blob/main/docs/creating-skills.md)
