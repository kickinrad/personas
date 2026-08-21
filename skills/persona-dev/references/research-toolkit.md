# Capability discovery

Read this reference when a persona needs a new tool, integration, skill, hook,
or reusable worker.

Search the active runtime catalog and installed capabilities first. Then check
maintained official or upstream components. Create a local component only when
the role has a distinct trigger or procedure that existing capability cannot
satisfy.

| Need | Preferred shape |
|---|---|
| Existing external service connection | runtime plugin, app, or MCP binding |
| Mature deterministic operation | installed CLI |
| Repeated multi-step role procedure | persona-local skill |
| Isolated one-run investigation or review | fresh runtime worker |
| Independently reusable delegated pipeline | persona-local agent |
| Lifecycle enforcement | one narrow hook |
| Deterministic transformation | `tools/` script |
| Role-local explanatory depth | `docs/` reference |
| Durable knowledge or current state | its canonical owner |

Keep credentials and local configuration outside committed templates.
Installing or connecting a capability requires explicit approval. Record an
executable dependency in the owning component; a knowledge citation is never an
installation edge.

Verify one positive control in the target persona and one isolation control
showing the capability does not fire outside its declared trigger.
