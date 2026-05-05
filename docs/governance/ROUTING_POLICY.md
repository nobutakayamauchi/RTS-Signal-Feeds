# ROUTING_POLICY

## Objective
Route summarized signals into appropriate RTS downstream surfaces.

## Downstream targets (references only)
- RTS-Skills
- RTS-Talent-Registry
- RTS-MCP-Packs
- SNS idea generation

## Routing constraints in this repository
- This repo stores routing intent and templates only.
- It must not embed downstream canonical manifests.
- It must not execute SNS publish workflows.

## Suggested decision hints
- ai_tools -> RTS-Skills, SNS idea generation
- social_growth -> SNS idea generation
- mcp_connectors -> RTS-MCP-Packs
- security_governance -> RTS-Skills, trust/risk review queue
- competitor_market -> SNS idea generation, RTS-Skills strategy notes
- external_talent_updates -> RTS-Talent-Registry
