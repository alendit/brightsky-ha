# Repository Guidelines

## Architecture Guidance

Use this section to evaluate decomposition, dependency direction, side-effect placement, interface design, and testability.

### Hard Constraints
- Shape work packages around useful stopping points that move toward the final direction. If work stopped after the package, the project should be better off than not building it; this does not need to hold for every internal slice.
- Treat available information explicitly. Make likely changes easy, keep uncertain decisions local and reversible, and model stable behavior directly. Use small module, adapter, function, data-mapping, or config boundaries to keep uncertain decisions contained. Add an abstraction only when the contract is real, stable enough to name, and makes the next likely change cheaper.
- Give each behavior a clear owning component.
- Prefer application services over putting business logic into UI, transport, webhook, or tool handlers.
- Keep dependencies flowing from unstable code toward stable code.
- Keep core policy isolated from side effects.
- Do not mix unrelated domains into one coordinating component.
- Introduce abstractions only when they make a concrete likely change easier.
- Do not create shared interfaces that implementations can only satisfy by narrowing behavior, ignoring requirements, or throwing.
- Make compatibility expectations explicit. Keep legacy handling or legacy paths only when a real compatibility requirement exists; otherwise remove obsolete paths by default and mention that cleanup explicitly.
- Do not add fallback paths, broad defensive handling, or error swallowing unless that layer can make a correct domain decision; unexpected errors should surface to the top and fail in obvious ways.

### Required Self-Check For Design-Sensitive Changes
1. If this work package stopped here, would the project be better off than if it had not been built?
2. What final direction does this move toward?
3. Which decisions are likely to change, uncertain, or stable, and are uncertain ones local and reversible instead of hidden behind speculative abstraction?
4. What component owns this behavior, and why?
5. Does this change increase or reduce coupling?
6. Did any dependency start pointing the wrong way?
7. Could any side effect be moved outward into an adapter or shell?
8. Are the abstractions and interfaces semantically real?
9. What compatibility expectations apply, and were obsolete paths removed unless required?
10. What legacy code can we remove now?
11. Where are expected errors handled, and where do unexpected errors surface?
12. What tests prove the core behavior independently of the full system? If the design changed, would tests change narrowly, or would unrelated tests need rewrites?
