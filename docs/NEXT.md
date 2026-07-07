# RTS-Signal-Feeds Next Actions

The next goal is freeze review, not expansion.

## Next Tasks

1. Confirm whether existing source, signal, and routing templates are still useful.
2. Classify each signal artifact as ready, draft, stale, duplicate, risky, move, or archive.
3. Confirm that no executable ingestion code is present.
4. Confirm that no API keys, credentials, private links, or live publishing behavior are present.
5. Confirm that external signals are described as attention candidates, not facts by default.
6. Confirm that downstream manifests are referenced only and not stored as canonical copies.
7. Decide whether the repository should remain frozen, be archived, or receive a narrow signal-review update.

## Suggested Follow-up Files

```text
docs/inventory/signal_inventory.md
docs/contracts/signal_epistemic_contract.md
docs/governance/source_review_boundary.md
```

## Inventory Categories

Use these labels during the next pass:

- READY: safe as signal metadata or template material
- DRAFT: useful but incomplete
- STALE: likely outdated or superseded
- DUPLICATE: overlaps another signal template or source note
- RISKY: runtime, publishing, automatic routing, source quality, or epistemic risk needs review
- MOVE: belongs in another repository
- ARCHIVE: preserve for history only

## Signal Review Checklist

Each signal item should explicitly describe:

- name
- path
- signal type
- public source or reference
- summary purpose
- status label
- confirmed facts
- assumptions
- unverified material
- risks
- routing intent
- next smallest safe action

If an item implies executable ingestion, scraping, automatic publishing, live routing, or treating unverified material as fact, mark it as `RISKY` and do not expand it until reviewed.

## Do Not Do Yet

Do not:

- add executable ingestion code
- add scraping implementations
- add API keys, tokens, secrets, credentials, or private links
- add automatic publishing
- add SNS posting execution
- store canonical downstream manifests
- route signals into live operations automatically
- rewrite all signal templates at once

## Next Recommended Task

Create `docs/inventory/signal_inventory.md` only if this repository is intentionally reviewed again.

That file should list each known signal artifact with:

1. name
2. path
3. signal type
4. status label
5. public source or reference
6. epistemic risk
7. routing risk
8. runtime or publishing risk
9. next smallest safe action
