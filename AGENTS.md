# AGENTS Instructions for RTS-Signal-Feeds

## Scope
These instructions apply to the entire repository.

## Purpose
This repository is a **pre-test signal intelligence skeleton** for the RTS ecosystem.

## Hard boundaries
- Do not add executable ingestion/scraping implementations.
- Do not add API keys, secrets, or credentials.
- Do not include full manifests for RTS-Skills, RTS-Talent-Registry, RTS-MCP-Packs, Hermes drive, RTS trust record.
- Do not implement SNS publishing.

## Signal epistemics
All external signals are candidate inputs for attention and triage, not truth by default.
Always separate:
- confirmed_facts
- assumptions
- unverified
- risks

## Change style
- Keep docs and templates lightweight and explicit.
- Prefer additive edits; avoid destructive rewrites.
