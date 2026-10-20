# Validation record

## Focus revision — 20 October 2026

The following checks were executed against the prepared focus revision, not inferred from the presence of test files.

| Check | Observed result |
| --- | --- |
| Installer and package unit tests | 26 passed locally on Linux with Python 3.14.4; 26 passed on a GitHub-hosted Ubuntu runner with Python 3.14.8. |
| Actual-kit installation in a temporary directory | Dry-run created no destination; installation succeeded; an unchanged repeat made no content changes; the bundled license was installed. No live Claude configuration was changed. |
| Skill structure | Portable name/description metadata accepted by the repository's narrow validator; all ten reference modules retained. |
| Documentation and evaluations | Local file-link targets resolve; 31 unique authored case/rubric pairs have matching IDs and valid fixture paths. |
| Upload ZIP | 14 entries match the skill source bytes, including the unchanged AGPL license; CRC and layout checks pass. |
| Historical README cleanup | Each of the two rewritten historical trees differs from its original only in README.md, removing the requested paragraph. The initial license commit remains unchanged. |

The archive was also built and checked in [a GitHub-hosted preparation run](https://github.com/SaltKode/obedient-claude-skill/actions/runs/39380502060). That one-use job stored the validated Git blob without modifying main and removed its temporary branch. The shipped repository contains only the normal read-only [quality workflow](.github/workflows/quality.yml).

Archive SHA-256:

```text
651ccdd935989dbc9eadb997ec19224a92ef59d630aed70a457fa9c9fbeff15e
```

## Instruction footprint

Compared with the preceding instruction-following revision:

| File | Previous UTF-8 bytes | Revised UTF-8 bytes |
| --- | ---: | ---: |
| Persistent Code agreement | 6,473 | 5,371 |
| Skill entry point | 8,737 | 5,271 |
| Chat preferences | 5,295 | 4,670 |

These are exact file sizes, not tokenizer measurements or end-to-end usage savings. Detailed guidance remains available on demand. The revision does not change models, effort settings, runtime permissions, or required verification.

## Reproducing the artifact checks

Use Python 3.10+ from the repository root:

```bash
python3 -B -m unittest discover -s tools -p 'test_*.py' -v
python3 -B tools/check_repository.py
python3 -B tools/build_skill.py --check
```

On Windows, use `py -3` instead of `python3`. Tests use disposable directories and no model API. The validator checks this repository's metadata subset and local file targets; it does not validate external websites or Markdown heading anchors.

The normal quality workflow runs Linux/Python 3.10 and 3.14, Windows/Python 3.14, and macOS/Python 3.14. Inspect the [Actions results](https://github.com/SaltKode/obedient-claude-skill/actions) for each published revision rather than treating a configured job as an executed pass.

## Behavioral evaluation

The 31 scenarios are evaluation inputs, not benchmark results. Artifact tests establish installer and package properties; they do not establish Claude task quality or savings. Use [FOCUS-EVALUATION.md](evaluation/FOCUS-EVALUATION.md) for paired current-versus-revised trials with unchanged model, effort, permissions, and task inputs. Completion, correctness, scope, evidence, and delivery must remain intact before lower usage counts as an improvement.

## Earlier checks

The original installer suite contains 15 tests covering preservation, backups, collisions, idempotence, and injected failure recovery. The previous revision's record reported 14 passes and one unavailable symlink test on Windows. A prior four-test coding exercise used a GPT-family worker, not a Claude benchmark. Current reproducible checks and per-revision CI logs take precedence over those historical observations.
