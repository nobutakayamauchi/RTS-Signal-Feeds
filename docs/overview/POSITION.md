# POSITION

RTS-Signal-Feeds is the **fresh signal intelligence layer** in the RTS ecosystem.
It registers external information sources, classifies incoming signals, and produces structured summaries for downstream routing.

## What this repository does
- Maintains a source/feed registry for candidate external signals.
- Defines category taxonomy for signal classification.
- Provides templates for signal records and digest summaries.
- Defines governance and routing policy for handoff to downstream systems.

## What this repository does NOT do (in this skeleton)
- It does not execute scraping/harvesting implementations.
- It does not store canonical manifests for Skills, MCP Packs, Talent Registry, Hermes drive, or trust records.
- It does not publish to SNS.
- It does not assert truth from external signals without verification.
