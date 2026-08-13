# /goal — Challenger Discovery Sweep v0

Date: **2026-08-14**

Status: `FULL_CRAWLER_KILLED / DISCOVERY_SWEEP_GLUE_SURVIVES`

## Problem

Before creating a new program or constructing an external challenger, ULTIMATE LOOP needs a fresh view of the surrounding implementation landscape.

The required outcome is not "crawl the whole internet." That claim is not provable.

The required outcome is:

1. search the current landscape broadly enough to expose credible existing holders, adjacent implementations, architectural alternatives, and known failure modes;
2. preserve source identity, freshness, query/coverage history, and unresolved gaps;
3. expand the search frontier when new terms, products, architectures, dependencies, or source classes are discovered;
4. stop only at an explicit evidence-bounded saturation state;
5. feed material candidates into METEOR without granting promotion authority.

## Raison d'être attack

### Attack A — manual one-off search only

Verdict: `FAIL FOR REPEATED BUILD/CHALLENGER GATES`.

Manual research can discover candidates, but repeated manual sweeps do not by themselves preserve:

- which source classes were covered;
- which queries were actually executed;
- which areas were blocked or unsearched;
- when the evidence was captured;
- whether later rounds produced new material candidates;
- a reproducible stop condition.

### Attack B — build a general-purpose web crawler

Verdict: `KILL AS OWNED CORE`.

General crawling, JavaScript rendering, URL queues, retry/rate-limit behavior, sitemap discovery, and site extraction already have mature external holders.

The missing responsibility is not page fetching. It is **landscape coverage control and evidence-bound saturation** across heterogeneous external holders.

### Attack C — keep the existing Signal Feeds skeleton only

Verdict: `INSUFFICIENT`.

RTS-Signal-Feeds already has source registry, taxonomy, signal templates, scorecards, provenance-minded handling, and routing intent, but it explicitly stopped before executable ingestion/search orchestration.

That makes it the right host, but the current skeleton does not enforce a pre-build discovery sweep.

## Surviving responsibility

`DISCOVERY_SWEEP_GLUE`

The owned layer is intentionally small:

```text
FROZEN SUBJECT / WORKLOAD
-> SOURCE-CLASS COVERAGE PLAN
-> EXTERNAL SEARCH / FEED / API / CRAWLER ADAPTERS
-> NORMALIZED CANDIDATE EVIDENCE
-> QUERY FRONTIER EXPANSION
-> MATERIALITY REVIEW
-> COVERAGE + SATURATION VALIDATION
-> SEARCH_SATURATED_UNDER_CURRENT_EVIDENCE
-> METEOR
```

External systems remain responsible for actual search, crawling, browser execution, API access, and feed retrieval.

## Hard invariants

- `SEARCH_SATURATED_UNDER_CURRENT_EVIDENCE != COMPLETE_WEB_KNOWLEDGE`
- `EXTERNAL_SIGNAL != VERIFIED_TRUTH`
- `DISCOVERY != PROMOTION_AUTHORITY`
- required source classes that are unsearched or blocked fail closed;
- unresolved candidate materiality fails closed;
- duplicate sightings do not manufacture novelty;
- a new material candidate reopens the search frontier;
- source acquisition remains adapter-replaceable.

## v0 implementation budget

Owned implementation:

- one stdlib-only evaluator/CLI;
- one focused test module;
- request/evidence examples;
- no scheduler;
- no always-on daemon;
- no database;
- no browser runtime;
- no search-engine implementation;
- no scraping bypass layer;
- no stored credentials;
- no autonomous build or promotion.

Expected owned code size: **well under 500 lines including focused tests**, excluding docs/examples.

## Trigger policy

Run a fresh sweep:

- before authorizing a new program that overlaps an existing market/tool category;
- before constructing an external challenger for METEOR;
- when DARWIN receives a material new-capability or architecture-change trigger;
- when a previously rejected build is reconsidered after a meaningful era change.

Emergency restoration may use a bounded exception when delay would materially worsen recovery, but the missing sweep becomes explicit debt and cannot be used to claim long-term superiority.

## Verdict

`BUILD THE THIN DISCOVERY SWEEP CONTROL LAYER.`

`DO NOT BUILD A GENERAL WEB CRAWLER.`

The first executable occupant is `scripts/discovery_sweep.py`.
