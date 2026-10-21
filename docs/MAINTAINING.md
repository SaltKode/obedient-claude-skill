# Maintenance and workflow decisions

## Four review notes

| Suggested workflow | Decision | Reason |
| --- | --- | --- |
| Publish Python Package | Not added | The product is a Markdown skill with standard-library installer scripts, not a Python package. PyPI would add packaging, registry ownership, and release maintenance without simplifying the existing ZIP installation. |
| Python package testing | Adapted and added | Test the actual installer and packaging scripts across operating systems and Python versions; validate skill metadata, local links, evaluations, instruction-size limits, and ZIP/source consistency. |
| SLSA Generic generator | Deferred | Provenance is useful for a defined release artifact and verification process. It does not test instruction quality or token efficiency. Add it when there is a release pipeline and consumers have a verification path, rather than claiming SLSA compliance from a copied workflow. |
| README | Rewritten | Benefits first, fewer technical detours, simple Code/chat setup, restrained emoji, and no unsupported savings percentage. |

The workflow uses GitHub-hosted runners, read-only repository permissions, SHA-pinned checkout/setup actions, no persisted checkout credentials, a timeout, and cancellation of superseded runs. It requests no secrets or model API calls. It neither publishes packages nor modifies user Claude settings. GitHub's current account/runner policies still apply.

## Local development

Use Python 3.10+ and its standard library; no pip install is necessary.

```bash
python3 -B -m unittest discover -s tools -p 'test_*.py' -v
python3 -B tools/build_skill.py
python3 -B tools/check_repository.py
```

Use `py -3` on Windows. Rebuild the ZIP only after skill-source changes; `python3 -B tools/build_skill.py --check` verifies without writing. The archive contains one `work-with-me/` root and includes the unchanged repository license. Entries are sorted with fixed timestamps and permissions. Equal inputs produce equal bytes with the same compression implementation; cross-environment checks compare exact uncompressed source bytes rather than assuming all zlib versions emit identical compressed bytes.

The offline validator accepts this repository's intentionally small metadata subset, checks local file-link targets (not external websites or heading anchors), validates evaluation/rubric IDs and fixture paths, and rejects a stale archive. It is not a universal Markdown/YAML parser or a test of model behavior. Instruction budgets are UTF-8 bytes, not Claude token measurements. Budget changes need review, not the deletion of necessary quality rules.

## Behavioral changes

The focus revision makes necessary follow-through autonomous and tells Claude to skip optional sidequests without turning them into permission questions. It adds independent-call batching, targeted editing, selective reference loading, evidence invalidation rules, concise but complete diagnostics, and an explicit completion boundary.

No-progress checkpoints encourage reassessment rather than abandoning useful troubleshooting after an arbitrary command count. Explicit user limits remain binding. The kit does not lower model effort, switch models, grant tools, change permission modes, or add a worker framework.

Keep the compact Code/chat agreements semantically aligned and preserve owner-specific language and handoff decisions. Keep detailed guidance in the ten references. Add a behavior case for a concrete failure, then compare current and revised skills using [the focus protocol](../evaluation/FOCUS-EVALUATION.md). Smaller files are not by themselves proof of cheaper or better task execution.

## Sources checked for this revision

- [Claude skill loading and supporting files](https://code.claude.com/docs/en/skills).
- [Claude usage and context management](https://code.claude.com/docs/en/costs).
- [Claude custom skill upload](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).
- [GitHub Python testing and package publishing](https://docs.github.com/en/actions/tutorials/build-and-test-code/python).
- [GitHub Actions secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use).
- [SLSA provenance requirements and builders](https://slsa.dev/how-to/get-started).

Product interfaces change. Check the relevant official documentation when updating installation or workflow mechanics instead of hardcoding assumptions about a model name or price.

## Comparison-informed revision

See [the design changes](COMPARISON-IMPROVEMENTS.md) and [optional trial runner](../evaluation/TRIALS.md). The runner and its fake-process unit tests are developer tools, excluded from the installed skill. Metadata validation follows the 1,024-character specification separately from a 360-character editorial review warning; the current description stays unchanged until activation evidence justifies a change. The optional [skills CLI path](ECOSYSTEM-INSTALL.md) is tested separately and is not an npm dependency of the package or CI.
