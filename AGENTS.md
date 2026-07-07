# AGENTS Instructions for RTS-Signal-Feeds

## Scope

These instructions apply to the entire repository.

## Required reading

Before editing, read:

1. `README.md`
2. `docs/STATUS.md`
3. `docs/NEXT.md`

## Purpose

This repository is a **frozen non-executable signal intelligence skeleton** for the RTS ecosystem.

It describes how external signals may be registered, summarized, scored, and routed as candidate attention inputs.

It is not an ingestion runtime.

It is not a publishing system.

It is not a source of truth.

## Hard boundaries

- Do not add executable ingestion/scraping implementations.
- Do not add API keys, secrets, credentials, or private links.
- Do not include full manifests for RTS-Skills, RTS-Talent-Registry, RTS-MCP-Packs, Hermes drive, or RTS trust records.
- Do not implement SNS publishing.
- Do not implement automatic live routing.
- Do not treat external signals as facts without review.
- Do not turn this repository into RTS core, RTS-AGE, or runtime infrastructure.

## Signal epistemics

All external signals are candidate inputs for attention and triage, not truth by default.

Always separate:

- confirmed_facts
- assumptions
- unverified
- risks

## Freeze boundary

Treat the next pass as freeze review and signal inventory, not expansion.

If an item implies executable ingestion, scraping, automatic publishing, live routing, or treating unverified material as fact, mark it as `RISKY` and do not expand it.

If this repository is not needed for current work, leave it frozen.

## Change style

- Keep docs and templates lightweight and explicit.
- Prefer additive edits; avoid destructive rewrites.
- Prefer review-boundary documentation over implementation.

## Validation

For documentation-only changes, report changed files and confirm that no executable ingestion code, scraping implementation, secrets, private links, automatic publishing, live routing, canonical downstream manifest storage, or runtime behavior was added.
