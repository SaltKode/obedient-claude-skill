# UI and product work

## Understand the screen's job

Identify who uses the screen, what they need to decide or do, and what information must remain visible. Use the user's reference and current product to establish the intended density, hierarchy, and interaction model.

If the user asks for an exact visual match, make that reference the acceptance target. If they ask for improvement, identify specific usability or visual problems and make an internally consistent design decision. Do not substitute an unrelated generic dashboard for a supplied design.

Inspect the real application when it is available. Confirm the existing framework, design tokens, component library, icon system, navigation, and backend connections. A screenshot alone cannot prove how every hidden interaction behaves; distinguish observed features from reasonable implementation assumptions.

## Translate a reference into implementation decisions

Examine overall composition before individual details: column widths, margins, grouping, header height, navigation, content density, and spacing rhythm. Then assess typography, contrast, color roles, borders, radii, icons, elevation, and states.

Keep an inventory of the controls and information the user expects. If a trading assistant must show sentiment, geopolitical events, storage levels, or other context, preserve those requirements while organizing them clearly. Do not invent live feeds or claim sample data is connected.

Use the reference's hierarchy to decide what is prominent, what can be compact, and what belongs in a secondary view. Match the stated goal rather than adding fashionable effects. Motion, decoration, and oversized headings should support the product's use.

## Build with the established system

Reuse current layout primitives, components, tokens, and assets. Extend them when needed. Prefer a small, coherent set of changes over a new parallel component system.

Do not add an animation framework, icon library, design-system package, or hosted asset service merely because it is familiar. Check what already exists. Seek a decision for a new dependency when the current stack cannot reasonably meet the requested result.

Preserve functional wiring during a visual change. Keep navigation targets, form behavior, permissions, data boundaries, and accessibility semantics unless the task explicitly changes them. A styled placeholder is not a finished feature when the user requested a working application.

If the user requests a concept image, produce the concept in the appropriate medium. If they request actual interface implementation or production icons, deliver usable code or assets. Do not treat a presentation image as a functional interface.

## Cover the relevant interaction states

Consider loading, empty, error, disabled, focused, selected, and overflow states where the changed component needs them. Avoid inventing elaborate flows that the task never requested.

Use semantic elements and readable contrast. Preserve keyboard access and a visible focus state. Check that truncation, long labels, real content, and narrow viewports do not hide essential actions. A design that works only with ideal placeholder text is incomplete.

For personal-use software, prioritize the user's daily workflow and the current operating model. Do not impose generic multi-tenant onboarding, billing, or enterprise administration when the project does not need them.

## Inspect the rendered result

Run the available application or preview and inspect screenshots at a representative viewport. Compare the largest visual differences first: composition, spacing, typography, density, and missing elements. Refine those before small decorative details.

Exercise the primary interaction affected by the change. A screenshot checks appearance; it does not verify a form submission, data refresh, or permission boundary. Use the relevant evidence for each claim.

If browser or screenshot tools are unavailable, state that visual fidelity has not been checked in a render. Deliver the code or artifact you can produce, with a clear next verification step. Do not announce an exact match based only on source inspection.

Stop when the requested visual and functional criteria are met. Do not endlessly redesign the screen because a different aesthetic is possible. Keep optional alternatives concise and separate from the completed work.

## Preserve product identity

Keep a product's name separate from its team or company attribution. If the team name is replaceable, use the existing branding configuration or a proportionate equivalent. Avoid embedding a temporary brand into database identities, security identifiers, package names, and URLs without a real requirement.

For projects with hosted and commercial editions, consult the current project profile. Do not merge editions, expose private branding, or infer a new update relationship from this general routine. Project architecture belongs to the project, and a visual request does not authorize revising it.

## Deliver clearly

Show the result when the environment supports it. Explain the consequential design decisions, what works, what was visually checked, and any missing integration. Use the user's requested output format. The deliverable should be useful without a long lecture on design terminology.
