# RTS-Signal-Feeds Status

Status: FREEZE / SIGNAL-SKELETON / REVIEW BEFORE USE

RTS-Signal-Feeds is a non-executable signal intelligence skeleton for the RTS ecosystem.

Its purpose is to describe how external signals may be registered, summarized, scored, and routed as candidate attention inputs.

It is not RTS core.

It is not RTS-AGE.

It is not an ingestion runtime.

It is not a scraping system.

It is not a publishing system.

It is not a source of truth.

## Current Position

This repository should remain frozen unless there is a concrete signal-review task.

The current skeleton may be useful as a reference for source registration, feed scoring, summary templates, digest shape, and routing intent.

However, it should not become active collection, publishing, or routing infrastructure by default.

Allowed by default:

- clarify signal boundaries
- document signal templates
- document source registry fields
- document scoring and routing assumptions
- improve separation of confirmed facts, assumptions, unverified material, and risks
- classify existing signal artifacts as draft, stale, risky, or archive candidates
- preserve the repository as a non-executable signal skeleton

Prohibited by default:

- adding executable ingestion code
- adding scraping implementations
- adding automatic publishing
- adding SNS posting execution
- adding API keys, secrets, credentials, or private links
- storing canonical downstream manifests
- treating external signals as facts without review
- routing signals into live operations automatically
- turning this repository into RTS core, RTS-AGE, or runtime infrastructure

## Boundary

RTS defines canonical protocol and reconstructability rules.

RTS-AGE may prepare implementation artifacts under review boundaries.

RTS-Skills, RTS-Talent-Registry, RTS-MCP-Packs, and RTS-Hermes-Drive own their own component definitions.

RTS-Signal-Feeds should only describe candidate signal intake and routing metadata.

It should not absorb upstream manifests, create live ingest pipelines, or publish external outputs.

## Freeze Definition

This repository is considered safely frozen when:

1. Its signal-skeleton role is explicit.
2. External signals are treated as attention candidates, not truth.
3. Epistemic fields are preserved: confirmed facts, assumptions, unverified material, and risks.
4. Runtime ingestion, scraping, publishing, and automatic routing are prohibited by default.
5. Future edits require a concrete signal-review purpose.

## Current Decision

Keep this repository frozen.

Treat it as a signal intelligence skeleton and archive-adjacent reference.

Do not expand it into live collection, publishing, automatic routing, or runtime infrastructure without a separate decision record.
