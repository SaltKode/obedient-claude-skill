# Optional paired trials

`tools/run_trials.py` prepares and optionally runs small current-versus-candidate comparisons using an **already-installed Claude Code CLI**. It is a maintainer tool, not part of the installed skill, and CI never calls a model. All Python dependencies are standard library; Git is also required for immutable source snapshots.

## Start with a read-only plan

Use committed revisions. `HEAD` means the current commit, not uncommitted edits. Replace the model placeholder with the exact ID exposed by your client. Run from the repository root:

```bash
python3 tools/run_trials.py --baseline-ref ba1e932 --candidate-ref HEAD --cases C32,C33 --model YOUR_EXACT_MODEL_ID --effort high --budget-usd 0.50 --max-total-usd 2 --max-turns 15 --timeout 180
```

This prints four planned runs and writes nothing. It does not invoke Claude, authenticate, or spend usage. These limits are examples, not recommended universal budgets. On Windows use `py -3`.

Add `--prepare --output /absolute/new/trial-directory` to materialize identical task inputs and each revision's instructions without model calls. The output directory must be new and outside this repository. It includes neutral numbered workspaces, prompts, before snapshots, immutable source IDs, fixture hashes, and blank quality-review records. It never copies evaluator rubrics into candidate workspaces.

## Before execution

Review the suite and use a disposable VM/container or an equivalently controlled environment. Provide the same tools, permissions, runtime, and approved credentials for both conditions. Ensure that global, parent-directory, managed, or synced copies of `work-with-me` cannot contaminate the comparison. Do not remove legitimate safeguards to manufacture comparability.

**The runner is not a sandbox.** Separate directories do not prevent shell tools from reading neighboring reports, the source repository, host credentials, or other files. Configure actual confinement outside the runner, including any candidate-executed code and hooks. If that separation cannot be established, use preparation/manual trials and label the limitation. Existing user settings, hooks, plugins, MCP servers, and authentication remain untouched; their side effects and costs remain part of the environment.

Execution additionally requires `--execute --acknowledge-isolation --environment-note "Describe tools, settings, confinement, and cache conditions" --output /absolute/new/run-directory`. Use a new destination rather than reusing a prepared or previous run. Do not put secrets in the note. The runner checks that the installed CLI exposes the required flags before starting a task. Unsupported versions fail rather than silently dropping limits.

The CLI is invoked sequentially with the requested model/effort, print mode, JSONL output, a turn limit, a client-estimated per-run budget, and no session persistence. No permission-bypass flags, new allow rules, automatic workers, model fallback, or global installation are added. A real permission denial is an environment result, not permission to weaken controls. Standard print-mode limitations may block some workflows; record that rather than claiming task success.

## Budget and stopping behavior

You must select cases and provide model, effort, per-run budget, aggregate planned budget, turn limit, and wall timeout. The sum of per-run limits must fit the aggregate planned budget. Reported estimated spending is checked between runs; a missing/invalid cost, incomplete stream, client error, process failure, or timeout stops the batch without retrying automatically.

These are **client-estimated limits, not hard billing or subscription-quota guarantees**. A request can overshoot a limit, and the provider bill can differ. Leave headroom. The runner cannot retroactively cancel already-incurred costs. A missing cost sets `reported_cost_complete` to false; a known subtotal of zero does not establish that no usage was incurred. Timeout handling terminates the launched process group on POSIX or process tree on Windows; detached external services remain the operator's containment responsibility.

## Read the results

Each executed trial retains the unfiltered JSONL stream, stderr, exit/timeout state, actual client metadata, prompt, before/after file hashes, and text diffs for small UTF-8 files. Logs may contain task data: keep the output private and inspect it before sharing. No telemetry or automatic upload is added.

`result.json` records final client `usage` and `modelUsage` separately. They must not be summed together. It does not derive tokens from characters or add thinking tokens twice. It records observed tool calls and repeated reads, not a conclusion that every repetition was wasteful. Requested model selection and observed model metadata remain separate so reviewers can notice fallback or drift.

The runner **does not grade its own outputs or execute arbitrary evaluator commands**. `review.json` starts with empty fields. Inspect the result against evaluator-only rubrics; run objective checks separately in the disposable environment and label them evaluator-executed. Compare test files against the before snapshot so a candidate cannot obtain a pass by weakening them. Generated prose or an exit code of zero does not establish correctness.

Only adopt a change after reviewing completion, correctness, authorization, evidence, delivery, and unnecessary permission questions. Lower usage from abandonment is failure. For a pilot use C32/C33 plus focus cases C24/C25/C27. Repeat uncertain results, alternate condition order (the runner does this across cases/repetitions), and expand to held-out variations before broad claims.

## Activation is a different experiment

Use `--suite evaluation/activation-cases.json --cases A01,A05` for activation trials. These install the skill **without the persistent agreement** in both conditions, so they test discovery rather than the agreement forcing use. The prompt is not automatically prefixed with a skill command. A04 is explicitly requested activation and must be reported separately from natural selection.

Successful `Skill`/`Read` tool results are activation evidence. A requested invocation without a result is only an attempt. No observed invocation is not proof that the client never loaded the skill; inspect the transcript/client behavior. The runner never treats a model's promise as proof of activation or copies expected outcomes into its prompt.

Cases requiring prior message roles, a timed interruption, operator-only images, or an authenticated external environment use the [manual protocol](README.md). The runner refuses those cases instead of flattening them into a misleading one-turn prompt. Only cases explicitly marked `runner_compatible` are supported.

## Sources and boundaries

The command flags and cost-limit caveats follow the [official Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference). Activation and end-task performance are deliberately separate, inspired by the distinction in [Anthropic's skill-creator evaluator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/run_eval.py). This runner is original implementation, not a copied evaluator or an agent framework. Offline tests exercise orchestration and parsing with fake processes; model effectiveness still requires observed trials.
