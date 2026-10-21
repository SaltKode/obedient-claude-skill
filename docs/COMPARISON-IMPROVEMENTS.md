# Changes informed by comparable skills

This revision adapts specific ideas into the existing ten-module routine. It does not install a competing framework, copy their instruction files, add mandatory agents, or claim their benchmarks as our results.

| Source | Idea adapted | Boundary retained |
| --- | --- | --- |
| [Anthropic skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) | Separate activation testing from end-task evaluation; collect actual results from small paired trials. | Optional maintainer tool with explicit limits, not an automatic paid evaluation swarm. |
| [Superpowers debugging](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging) and [Matt Pocock diagnosing-bugs](https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnosing-bugs) | Verify the reported failure, distinguish hypotheses with focused observations. | Static diagnosis remains useful when the real runtime is unavailable. |
| [Writing for agents](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents) and [handoff](https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff) | State when a reference is needed; link authoritative artifacts instead of copying their contents. | No compulsory task-state document for tiny work. |
| [ECC iterative retrieval](https://github.com/affaan-m/ECC/tree/main/skills/iterative-retrieval) | Identify the unresolved question before expanding a search. | No new retrieval agent or arbitrary numerical search quota. |
| [Impeccable](https://github.com/pbakaus/impeccable) | Separate refinement from redesign and fix coherent groups before re-rendering. | User references, functionality, and actual delivery target remain authoritative. |
| [Skills CLI](https://github.com/vercel-labs/skills) | Optional discoverable skill-only distribution. | Existing full installer remains dependency-free; no silent mixing of installation ownership. |

## What changed

The skill entry point selects guidance for concrete needs. Coding guidance ties a check to the original defect; UI guidance distinguishes repair, reference matching, and redesign. Specialist skills supply technical advice but do not expand user authorization or impose unnecessary process. Long-task state references plans, diffs, and logs instead of copying them wholesale.

The original 31 behavior cases remain. Six comparison cases and eight activation cases extend coverage to misleading green checks, specialist conflicts, appropriate design scope, lightweight handoffs, and unnecessary skill loading. Expected activation is evaluator-only and must not be included in a candidate's prompt.

The description itself is deliberately unchanged pending actual activation evidence. Metadata validation now follows the specification's 1,024-character limit, separate from a 360-character editorial review warning and the existing byte-size budgets. This is not an instruction to fill all available space. [Agent Skills specification](https://agentskills.io/specification)

The optional [trial runner](../evaluation/TRIALS.md) uses immutable committed snapshots, neutral numbered workspaces, sequential alternating conditions, actual client traces, file changes, and blank human review records. It does not automatically score quality, run model judges, or grant tools. Baseline contamination, actual confinement, permissions, model availability, and independent correctness checks remain explicit operator responsibilities.

## Avoid regressions

Do not count a cheaper incomplete result as an improvement. Keep full deliverables, required checks, user decisions, and ordinary in-scope autonomy. Compare model and effort settings unchanged. Test simplifications or removals of nonessential guidance on nearby and held-out tasks, not only the literal authored examples. Never weaken authorization or evidence requirements because a small pilot happened not to exercise them.

Keep this development rationale outside the installed skill. Its source list is attribution and design context, not a direction for Claude to browse every competitor before doing a task.
