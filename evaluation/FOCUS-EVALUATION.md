# Evaluate focus without trading away quality

There are 23 original cases in [cases.json](cases.json) and 8 focus cases in [focus-cases.json](focus-cases.json): **31 authored scenarios, not 31 passing Claude trials**. Keep all evaluator rubrics outside the candidate's context. Follow the fixture isolation and evidence rules in the [original protocol](README.md).

## Compare the actual change

For this revision, compare the previous skill with the revised skill on the same task. A no-skill baseline is a separate optional question. Keep model ID/version, effort, tools, permissions, initial files, runtime, and task input the same. Evaluate each model separately; record the identity actually exposed by the client instead of guessing it from a display name.

Preserve real platform safeguards. Do not weaken permissions, change global settings, install another provider, or consume API credits automatically. Use disposable fixtures and fresh comparable sessions. Where a clean baseline cannot be isolated from a global skill, report that limitation rather than claiming a controlled comparison.

Start with C24, C25, and C27 for sidequests, autonomy, and verification. Add C26 when the tool environment supports independent calls, C28 for concise diagnostics, and C29–C31 for stopping, correction, and productive recovery. Reuse C03 for full-code delivery, C10 for requested depth, C14/C23 for actual-target UI work, and C19/C20 for authorization boundaries.

Run a small pilot first, then repeat promising or variable cases with order alternated between conditions. Separate cold-start and warmed-cache observations. One cheaper run is not proof of a general saving. Do not run every case after every wording edit.

## Quality comes first

Reject an apparent efficiency win if it omits requirements, skips a required check, introduces a regression, fabricates evidence, violates scope, or makes the user repeatedly approve ordinary work. Missing tools are a capability limit, not proof of a prompt failure. Keep critical failures visible instead of burying them in a score average.

An unchanged relevant check can remain valid; a check invalidated by changed code/configuration/environment must run again. A new evidence-backed hypothesis can justify continued debugging. Count both needless work and premature stopping.

## Record comparable evidence

| Field | Record |
| --- | --- |
| Run identity | Case, trial, condition, exact skill revision, model/client, date |
| Controls | Effort, tools, permissions, runtime, starting fixture, cache condition |
| Completion and correctness | Acceptance conditions, actual test outputs, evaluator-only checks |
| Scope | Necessary edits, unrelated edits, permission questions, user interventions |
| Evidence reuse | Repeated reads/checks and whether their relevant inputs changed |
| Usage | Ordinary input, cache-read, cache-write, output, and reasoning only where exposed |
| Work distribution | Main, worker, and auxiliary usage; do not double-count aggregate totals |
| Latency | Elapsed time and model-request/tool rounds, where observable |
| Delivery | Exact requested format, completeness, relevant limitations |
| Comparability | Unavailable capabilities, rubric exposure, interruptions, changed conditions |

Do not estimate Claude tokens from character counts. Do not add thinking tokens again when the provider's output total already includes them. Keep raw provider/client usage fields alongside any calculated totals. Cached reads are cheaper in some billing systems but are not nonexistent input; reduced cost, reduced tokens, and reduced wall time are different outcomes.

If spending is measured, apply the actual model's current rates to the correctly categorized usage. Subscription quota behavior is not interchangeable with API dollar estimates. Do not infer a quota saving from a public pricing table.

## Acceptance and adoption

Look for fewer irrelevant edits, redundant reads, invalid retries, unnecessary model turns, and post-completion activities while preserving completion, correctness, scope, evidence, and delivery. Record unnecessary permission requests explicitly: an assistant that stops asking to do sidequests must not start asking to do ordinary work.

Describe observed per-case outcomes and variability. For broader claims, expand to held-out tasks and repeated trials with a predeclared quality threshold. Do not claim guaranteed quality parity or a universal savings percentage. Change the smallest relevant rule when a concrete failure appears, then test a nearby variation rather than optimizing solely for these literal prompts.

The offline Python tests and CI validate package mechanics. They do not invoke Claude or establish model-level effectiveness.

## Comparison-informed extension

Six [comparison cases](comparison-cases.json) cover exact bug verification, specialist conflicts, appropriate UI scope, and lightweight handoffs. Eight [activation probes](activation-cases.json) assess selection separately from task quality. Use [TRIALS.md](TRIALS.md) for the optional sequential runner; unsupported multi-turn/image cases still use the manual protocol. The default runner action only prints a plan. Never run paid trials from ordinary CI.
