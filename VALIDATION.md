# Validation record

Prepared 20 October 2026. This distinguishes executed artifact checks from model-behavior claims.

## Executed checks

| Check | Result | What it establishes |
| --- | --- | --- |
| Skill-format validator | Passed | Required YAML structure and naming rules are accepted by the validator used for this package. This is not a Claude account upload test. |
| Portable frontmatter inspection | `name` and `description` only; description is 197 characters | The package avoids Code-specific frontmatter and stays within the stricter documented description limit. |
| Installer tests | 15 passed | The exercised preservation, backup, collision, idempotence, and failure-recovery paths work in temporary Linux directories. |
| Installer dry-run using the actual kit | Passed; destination did not exist afterward | Planning the actual installation created no target files. |
| Independent focused-fix exercise | One source line changed; all 4 existing tests passed; complete corrected source returned in chat | The available agent could apply the routine to a small executable task while respecting scope and format. |
| Reference and archive checks | See the delivery check below | Linked local resources exist and the delivered archives have the intended layout. |

The installer tests were run with `python3 -B tools/test_install_claude.py`. They cover fresh installation, unchanged repeats, BOM/CRLF preservation, exact bytes outside the managed block, owned updates and backups, unknown skill collisions, invalid markers/encoding, missing sources, relative destinations, symlink refusal, state changes after planning, and injected backup/commit failures.

All installer operations used temporary destinations. The validation checks did not modify a live user Claude configuration, account setting, repository, provider, permission mode, or subscription. Publishing this source repository is separate from installing or evaluating it in Claude.

## Independent task exercise

A fresh agent received the working agreement, the skill, a small Python invoice module, the existing four tests, and a user-style request to fix only the percentage tax calculation and return the full corrected file in chat.

The agent changed `subtotal * tax_rate` to `subtotal * tax_rate / Decimal("100")`, preserving the rest of the source. The tests covered the reported rate, a zero rate, a fractional rate, and existing presentation behavior. The parent independently ran the same four tests and confirmed the resulting file.

The worker was not given an evaluator rubric or a description of a suspected skill defect. It still received an explicit skill invocation, so this exercise does not measure automatic skill selection.

**The exercise used an available GPT-family agent, not Claude.** There was no baseline without the routine and no model comparison. It is a small workflow check, not evidence of Claude effectiveness or equivalence to GPT-6.1 Sol.

## Review findings incorporated

The review clarified that explicit new-project stack-selection authority includes the necessary local dependencies, temporary preview servers and background tests can fit ordinary implementation scope, and retrieved material or worker reports cannot establish new user approval.

These changes preserve autonomy while making the scope boundary more precise. They were not introduced as guaranteed technical security controls.

## Practical limits

- No live Claude session or account upload was available for validation in this task.
- The full twenty-case Claude evaluation remains unrun. Use `evaluation/README.md` for a small-first comparison on the actual model and environment.
- Native Windows and macOS runtime execution were not tested here. The installer uses Python standard-library APIs and includes Windows reparse-point checks; that is implementation intent, not platform verification.
- The installer preserves files mechanically but cannot reconcile contradictory natural-language preferences.
- The routine cannot guarantee automatic selection, adherence, exact quality, savings, background execution, or tool access.

## Delivery check

Before delivery, the package is checked for parseable evaluation JSON, existing relative Markdown links, expected skill entry points, archive integrity, and a single `work-with-me/` root in the skill-only ZIP. The general kit and skill-only ZIP contain the complete source material required for their documented use.
