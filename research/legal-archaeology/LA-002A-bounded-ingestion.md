# LA-002A — Bounded ingestion prototype

Status: fixture replay PASS; official XML replay OPEN (2026-11-25).

## Evidence
Official OLRC section: https://uscode.house.gov/us/usc/119-121/t17/s109/ (laws in effect through Public Law 119-121, October 9, 2026). The wording of §109(b)(1)(B)(ii) in the fixture was checked against this page. Fixture hierarchy and references are constructed for testing, not a downloaded official XML representation; the test text under (d) and note are synthetic, not legal authority. No claim of completeness or legal effect.

The same official section prints §109(e), but the effective-date note to Pub. L. 101-650 §804(c), as amended, terminates application of the §803 amendment to performances or displays on or after October 1, 1995. Treat this as a candidate temporal-effect case for later verification, not a conclusion from graph traversal. Original statutory source: 104 Stat. 5134–5136; amendment: 108 Stat. 4974. Preserve statutory notes distinctly from enacted section text.

## Implementation
`legal_archaeology/ingest.py`: dependency-free bounded XML adapter. Explicit edition, source URL, expected section inventory and fixture/partial scope; byte count and SHA-256; ordered fragments and containment edges; separate notes; explicit reference resolution within supplied input; canonical JSON. A resolved reference is a matching identifier, not a legal interpretation. Input data hashes do not authenticate the source or prove the edition label. Only a restricted USLM-shaped UTF-8 subset is tested. External references, references without markup, notes outside sections, full USLM schema compliance and exact reconstruction of original XML are not yet covered.

## Verification
Python 3.13.5, command from isolated local copy: `python -m unittest discover -s tests -v`. Seven tests passed after fixing two test mutations that used /109 instead of /s109 and therefore did not change their inputs. Tested nested clause, separate notes and reference status, deterministic output/edition distinction, missing section, duplicate identifier, malformed/DTD input and incorrect parent.

Tested Git blob hashes (confirmed identical on remote branch):
- legal_archaeology/ingest.py: a6b218dd7f1a6fa065cb95d79b12899d7953a336
- tests/test_ingest.py: 103b65d934ff0327f910f282550f4f9b97c7ab17

Direct OLRC archive fetch failed DNS resolution in execution environment; official XML bytes, release manifest, section inventory, full Title 17 replay and contemporary corpus ingestion remain OPEN. No inherited tests or CI executed. Original upstream implementation and workflow unchanged.

## Next gate: LA-002B
Acquire a pinned official Title 17 XML archive; record URL, edition, retrieval time, byte count and hash; inspect actual USLM namespace/identifiers/notes; adapt and test against genuine §109 and §106; compare full section text and notes to authoritative display; record all unresolved references and coverage gaps. Only then scale to the full edition. No dormancy conclusions from fixtures.
