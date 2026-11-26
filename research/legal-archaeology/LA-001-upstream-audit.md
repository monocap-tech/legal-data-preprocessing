# LA-001 — Upstream infrastructure audit

Date: 2026-11-25. Baseline: `d0952593ce0b834f4abaf03f6a1975dc407014a8`. Upstream: QuantLaw/legal-data-preprocessing (BSD-2-Clause). This is a static source audit, not a successful pipeline replay.

## Findings

| ID | Evidence at baseline | Finding | Required closure |
|---|---|---|---|
| A01 | README.md; requirements.txt; .github/workflows/tests.yml | Documented runtime Python 3.7, pinned NumPy 1.19.4, pandas 1.2.0, NetworkX 2.4, QuantLaw 0.0.5; development requirements are mostly unpinned. | Reproduce legacy environment separately; establish supported runtime and tested lockfile. |
| A02 | statics.py; __main__.py | Defaults are 1994–2019 for statutes and 1998–2019 for regulations (exclusive upper bound 2020); explicit --snapshots exists, but does not constrain every ingestion step. | Explicit, verified edition manifest; test current-year handling without assuming availability. |
| A03 | download_us_code_data.py | Archive discovery depends on exact anchor text and XHTML path pattern; no explicit timeout, checksum manifest, atomic download or explicit failure on non-200. All matching archives are downloaded. | Bounded selection, verified source metadata, hash, timeout, atomic custody, fail-closed error handling. |
| A04 | download_us_reg_data.py | Download years hard-coded 1996–2020 inclusive; existing ZIP treated as complete without verification. | Separate later CFR coverage from statutes milestone; validate all retained archives. |
| A05 | statutes_pipeline_steps/us_prepare_input.py; us_to_xml.py | Input names and historical HTML comment structure assumed; parser includes edition-specific repairs and structural assertions. | Fixture-based schema drift and text preservation tests; reject incomplete parsing. |
| A06 | statutes_pipeline_steps/hierarchy_graph.py; crossreference_graph.py; snapshot_mapping_edgelist.py | Uses NetworkX gpickle APIs and Python pickle. Cross-reference graphs already export compressed node and edge CSVs, so portable output is partially present. | Preserve CSV exports; define versioned schemas and round-trip tests; never load untrusted pickle. |
| A07 | tests/; .github/workflows/tests.yml | Five test modules (common, two German reference parse, snapshot mapping index, US regulation XML). Legacy workflow is master-push only, uses moving action refs and old Codecov integration. | Add US statute source-to-graph fixtures and isolated modern test runner; do not enable inherited workflow as-is. |
| A08 | statics.py; __main__.py | Working-directory-relative data paths; skip-existing behavior does not bind outputs to input hashes. | Explicit workspace, source/build manifests, deterministic output and stale-output invalidation. |

## Scope and architecture decision

Preserve original upstream source and license. Add new development under `legal_archaeology/` and research notes under `research/legal-archaeology/`. Initially target US federal statutes; CFR, German law, state law and historical expansion are separate milestones. Use official OLRC sources; compare contemporary USLM XML with inherited annual XHTML rather than assuming format interchangeability. Historical mapping edges are heuristic candidate correspondences, not proof of legal continuity.

## LA-002 acceptance criteria

1. Explicitly identify official source edition, URL, retrieval date, file size, SHA-256 and upstream release identifier where available.
2. Start with a bounded Title 17 fixture including section 109 and nested clauses; verify text and citation IDs against official source; retain notes and distinguish source text from interpretation.
3. Produce deterministic, portable nodes and edges with typed relation and provenance. Mark unresolved references explicitly; a statute graph need not be acyclic.
4. Test repeatability, malformed/partial input, duplicate identity, missing references, and edition separation. No full-corpus scan until fixture passes.
5. Only after bounded replay, scale to one explicitly selected complete US Code edition, recording title/section counts, rejected inputs, and gaps. A downloaded corpus is not proof that each provision is currently effective.
6. Retain original source bytes or a verifiable retrieval manifest, test results and run metadata. No dormancy finding without separate evidence of legal effect and actual institutional use.

## Verification boundary

Read-only inspection of baseline files through GitHub succeeded. Local runtime is Python 3.13.5; Python 3.7 was not found and direct GitHub clone failed DNS resolution. No dependency installation, inherited tests, live archive downloads, or pipeline execution was completed. No assertion of compatibility, corpus completeness, security vulnerability absence, or successful reproduction is made. LA-001 static inventory complete; executable baseline reproduction remains OPEN. No upstream code or workflow modification is included.
