# Why this setup uses several layers

Prepared 20 October 2026 for the user's requested GPT-6.1 Sol Work-mode style of collaboration. Claude documentation was checked during this task. This is an original workflow design informed by those documents and the user's stated preferences, not an Anthropic or OpenAI product feature.

## Recommendation

Use a short persistent agreement, an extensive modular skill, and project-specific facts. Keep actual execution permissions separate. Include a chat preference block because ordinary Claude chat and a local coding workspace are different environments.

The practical goal is observable behavior: take ownership, inspect the actual work, make focused changes, verify them, retain decisions, and finish in the requested format. The package does not copy another model's weights, private prompts, or tool environment. It cannot establish identical reasoning, reliability, taste, or outcomes.

## What the research established

Claude Code reads personal instructions from `~/.claude/CLAUDE.md`; project instructions can be separate. Loaded instruction files are combined, so contradictory guidance needs reconciliation. Imports add startup context. These mechanisms guide behavior rather than impose a hard execution boundary. [Official memory documentation](https://code.claude.com/docs/en/memory)

Skills support a compact entry point and supporting files loaded when useful. A user can explicitly invoke a Code skill by its slash command. To keep this package portable, its frontmatter uses only `name` and `description`, with no tool grants or Code-specific execution fields. [Official skills documentation](https://code.claude.com/docs/en/skills)

Anthropic's skill-authoring guidance recommends concise instructions, conditional reference material, and evaluation against real tasks. That supports a detailed handbook whose individual sections are selected as needed. It does not establish that a longer prompt is inherently more effective. [Official authoring guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

Claude chat provides account-wide instructions and project-specific context. Its custom-skill upload expects a ZIP with the skill folder at the top level. The package therefore includes a separate account preference block and a correctly structured skill-only ZIP. [Personalization](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features) · [Custom skill creation](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)

Workers do not necessarily receive the parent's context. Current Claude Code documentation specifically describes inheritance differences for built-in research workers. The delegation routine therefore passes the actual task, constraints, authority limits, and expected evidence to each worker. [Official subagent documentation](https://code.claude.com/docs/en/sub-agents)

Claude Code provides permission modes and command/file rules. Command-pattern rules do not cover every equivalent invocation of a program. The shell sandbox has a narrower scope than the entire assistant environment. Those facts support keeping permissions and containment as a separately reviewed configuration decision. [Permissions](https://code.claude.com/docs/en/permissions) · [Sandbox](https://code.claude.com/docs/en/sandboxing)

## Why this fits the user's actual problem

The user's previous corrections establish several concrete priorities: do the work, preserve the accepted architecture, avoid unrequested dependencies and wasted usage, repair a narrow error without creating a new rewrite, honor full-code and file requests, and treat supplied UI references seriously.

The later clarification identifies GPT-6.1 Sol in Work mode as the behavioral reference. That makes active execution and continuity central. A change in tone alone would leave the main problem unsolved. The kit therefore addresses the full working cycle, including what to do when a tool or connection is genuinely unavailable.

The most important design decision is the boundary between implementation autonomy and product authority. The assistant can choose routine details inside the accepted task. It should seek a decision for a material new commitment the task has not authorized. When the user explicitly delegates stack selection for a new application, that delegation covers the necessary framework and local dependencies; it does not become blanket permission to add unrelated services or costs.

This boundary avoids two predictable failure modes: asking permission for every ordinary edit and making a consequential architecture decision alone. The goal is productive judgment within a clear agreement.

## Alternatives considered

| Approach | Assessment for this request |
| --- | --- |
| One long prompt pasted into each conversation | Useful as a fallback, but repetitive and easy to lose track of. The account block provides a more convenient persistent entry point. |
| A skill alone | Good for detailed routines, but essential preferences should not depend entirely on whether the skill activates. |
| A large persistent instruction file containing everything | Makes all tasks carry detailed procedures even when they are irrelevant. The kit keeps specialist material separate. |
| Output-style customization | Useful for communication, but the requested change includes execution, scope, verification, and recovery. A new output style is unnecessary for the baseline. |
| A new custom agent system or mandatory reviewer team | Adds configuration and maintenance before demonstrating that they are needed. This kit uses the existing Claude environment. |
| Generic command-blocking hooks | Cannot reliably decide whether a product change is an unwanted scope expansion. A specific hook could be added later for a concrete, testable condition. |
| Fine-tuning or attempting to reproduce another model | Outside the practical goal of a reusable local workflow; it would not copy the user's complete workspace environment. |

These assessments are design judgments. No controlled benchmark comparing all approaches was run during this task.

## How the extensive skill stays efficient

The persistent agreement contains the important cross-task rules. The skill's entry point selects among ten references: decisions, code, UI, research, writing, efficiency, recovery, communication, tools, and calibration examples. The assistant is instructed to load only the relevant material.

This design gives a narrow fix a short path while preserving detailed guidance for a serious build or investigation. It also prevents the user's quota preference from being misread as permission to deliver shallow work when depth was explicitly requested.

There is no promise of a fixed token saving. Actual usage depends on the model, tool outputs, existing instruction files, selected modules, task, and retries. The evaluation guide records observable effort instead of inventing a numerical efficiency claim. [Claude Code cost guidance](https://code.claude.com/docs/en/costs)

## What has and has not been validated

The files and installer are checked as artifacts. A small independent agent exercise tests whether the written routine supports a focused fix with complete code delivery. That exercise uses the available GPT-family agent, not the user's Claude model.

An actual Claude baseline/treatment comparison remains unrun. The package includes a small-first evaluation protocol and twenty realistic cases so the user can measure the behaviors that matter. Do not interpret a valid skill file or an installer passing tests as proof of model-level effectiveness. See `VALIDATION.md` for executed checks and `evaluation/README.md` for the Claude protocol.

## Maintenance

After real use, record a concrete failure and the relevant trace or output. Change the smallest rule or example that addresses it. Re-run the affected cases. Avoid adding broad prohibitions in response to every incident, and keep temporary project facts out of the global agreement.

Review current Claude documentation when an interface or feature changes. Keep one authoritative copy of the skill; do not let a local install, a synced skill, and a chat upload silently evolve into contradictory versions.
