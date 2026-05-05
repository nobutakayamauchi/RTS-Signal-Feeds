# RTS-Signal-Feeds
Fresh signal intelligence layer for the RTS ecosystem: source registry, feed scoring, daily and weekly digests, and routing of external signals into skills, talent updates, MCP discovery, and social ideas.

## Pre-test Skeleton (Minimal)
This repository now includes a minimal non-executable skeleton for:
- source registration and category classification,
- signal summary templates,
- routing intent toward RTS-Skills / RTS-Talent-Registry / RTS-MCP-Packs / SNS idea generation.

### Guardrails
- External signals are treated as candidates for attention, not truth.
- Signal artifacts explicitly separate: `confirmed_facts`, `assumptions`, `unverified`, and `risks`.
- No scraping implementation, API key handling, downstream canonical manifest storage, or SNS publish execution is included.
