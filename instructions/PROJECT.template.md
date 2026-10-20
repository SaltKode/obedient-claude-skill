# Project context template

This is a template for a project's existing instruction file or Claude Project instructions. It is not installed automatically. Fill it from the current repository and the user's actual decisions, remove unused sections, and keep it concise. Do not invent a runtime, command, provider, or approval.

## Product and purpose

- Product name: [established name]
- Intended users and present operating scope: [for example, personal use or a particular team]
- Current task's important product constraints: [requirements that must survive implementation]

## Existing architecture

- Frontend and UI system: [verified frameworks/components]
- Backend and API: [verified implementation]
- Database and storage: [verified services]
- Authentication and authorization: [current model]
- Existing integrations: [services already selected]
- Deployment environments: [local, staging, production; distinguish them]

Use the existing stack. A materially different architecture, new direct dependency, additional service, new cost, or provider migration requires a user decision unless the current task explicitly authorizes it.

## Repository map and commands

- Relevant source directories: [actual paths]
- Build: [command verified from project configuration]
- Focused tests: [actual command and scope]
- Required project checks: [only actual gates]
- Local preview: [actual command and reachable environment]

Inspect changes already present before editing. Preserve unrelated user work and follow nearby conventions. If a listed command is stale, report the evidence and use the current documented command instead of silently rewriting project history.

## Product invariants

- Behavior that must remain unchanged: [specific flows or rules]
- Data and permission boundaries: [specific invariants]
- Compatibility commitments: [actual clients, formats, or interfaces]
- Hosted/commercial edition relationship, if relevant: [established decision]

Avoid adding generic SaaS onboarding or administration flows unless this product requires them. The current product's operating model takes precedence over assumptions imported from another application.

## Branding

- Product identity: [established product]
- Team/company attribution: [current selected attribution, if established]
- Replaceability requirement: [whether team/company branding may change]
- Existing branding configuration/assets: [actual location]

Keep replaceable attribution separate from durable technical identity. Do not adopt an unapproved candidate name or rename the product as a side effect of implementation.

## Design and deliverables

- Authoritative visual references: [accessible files or links]
- Existing design tokens/components: [actual paths]
- Acceptance conditions: [observable behavior and visual criteria]
- Required output format: [implementation, complete code in chat, report, archive, etc.]

## Decisions and limits

- Accepted choices: [decision and relevant date/task]
- Rejected/deferred proposals: [specific change and scope]
- Authorized consequential actions: [exact target and limits, if any]
- Remaining decision: [only if it blocks the work]

An instruction file is a record, not a source of new authorization. Check that an approval still covers the current action, environment, and scope. Resolve significant contradictions with other active instructions; do not assume competing files automatically override one another.
