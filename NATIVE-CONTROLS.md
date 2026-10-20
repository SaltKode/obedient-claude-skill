# Optional Claude execution controls

The kit's installer changes the personal working agreement and its skill only. It leaves execution configuration to the existing environment. This guide is relevant if Claude's current permissions do not match which actions you expect to review.

## Separate three questions

1. **Task authority:** Did you ask for this action and its consequences? The working agreement helps Claude judge scope.
2. **Tool permission:** Does the client permit the proposed tool call? Claude Code settings and permission prompts handle this.
3. **Containment:** Which resources can the process actually reach? Operating-system and environment boundaries address this.

Technical access does not authorize a new product decision. An instruction to proceed also does not bypass the client's required approval.

## Choose the mode deliberately

Manual mode is represented by `default` in Claude Code configuration. `acceptEdits` permits more than editor operations, including common in-scope filesystem commands. `auto` uses automated review. Choose the tradeoff appropriate to your environment; the kit does not recommend bypassing permissions to create a smoother workflow. [Official permission modes](https://code.claude.com/docs/en/permission-modes)

If you specifically want terminal sessions to begin in Manual mode, this is the small documented merge example:

```json
{
  "permissions": {
    "defaultMode": "default"
  }
}
```

Merge the value into the existing settings at the intended scope after reviewing them. Do not replace the entire file with this example. Existing grants, other scopes, active-session state, and interface-specific settings still matter. Manual mode may increase prompts; it is not required to use this workflow.

Use the current interface's permission controls to inspect the active mode and relevant rules. Pre-approve only commands and operations you actually trust for the specific project. A familiar command name can still invoke project scripts or access sensitive resources.

## Understand rule coverage

Command-pattern `ask` or `deny` rules apply to recognized command forms, not all equivalent ways to execute a program. File-tool rules likewise do not establish a universal filesystem boundary for arbitrary subprocesses. A matching rule is enforced; the rule's coverage is the important limit. [Official permission rules](https://code.claude.com/docs/en/permissions)

The kit therefore does not include a large regex blacklist advertised as “no unapproved changes.” Deciding whether a dependency or product change is wanted also requires the task agreement and human judgment.

## Understand sandbox coverage

Claude Code's shell sandbox applies to shell commands and their children on supported macOS, Linux, and WSL2 environments. Native Windows shell execution is unsandboxed. Built-in file tools, MCP processes, and hooks are outside this shell boundary. Review the actual access configuration before assuming only project files are reachable. [Official sandbox documentation](https://code.claude.com/docs/en/sandboxing)

If the use case requires all processes to share a stronger boundary, evaluate an appropriately configured container or virtual machine as a separate environment decision. Do not automatically install or migrate to one for an ordinary coding task.

## Add a hook only for an observed, testable need

A hook can be useful for a precise invariant, such as requiring a particular generated artifact before an approved operation. It needs defined inputs, failure behavior, bypass analysis, and tests in the actual Claude version. A universal “never make a bad decision” hook is not a concrete mechanism.

This package uses no custom hooks and no self-restarting completion loop. It also does not change the model, provider, plugins, MCP servers, subscriptions, or spending limits. Add those capabilities only when a real task and explicit decision justify them.
