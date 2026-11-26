"""Bounded USLM-shaped ingestion; no legal-effect inference."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET

NS = '{http://xml.house.gov/schemas/uslm/1.0}'
LEVELS = {NS + n for n in ('section', 'subsection', 'paragraph', 'subparagraph', 'clause', 'subclause', 'item', 'subitem')}


def ingest(raw, *, edition, source_url, scope, expected_sections):
    """Parse an explicitly scoped XML document, with exact byte custody hash.

    Only USLM 1.x section-rooted trees or containing documents are supported.
    Scope is fixture or partial; complete corpus claims are deliberately unsupported.
    """
    if not edition or not source_url.startswith('https://') or scope not in {'fixture', 'partial'}:
        raise ValueError('explicit edition, HTTPS source and bounded scope required')
    if re.search(r'<!\s*(DOCTYPE|ENTITY)', raw.decode('utf-8'), re.I) or b'\x00' in raw:
        raise ValueError('DTD/entity declarations prohibited')
    root = ET.fromstring(raw)
    sections = list(root.iter(NS + 'section'))
    actual = [s.get('identifier') for s in sections]
    if not actual or len(actual) != len(set(actual)) or set(actual) != set(expected_sections):
        raise ValueError('section inventory mismatch')
    nodes, edges, notes, references, seen = [], [], [], [], set()
    digest = hashlib.sha256(raw).hexdigest()

    def visit(el, parent=None, position=None):
        ident = el.get('identifier')
        if not ident or not ident.startswith('/us/usc/') or ident in seen:
            raise ValueError('missing or duplicate provision identifier')
        if parent and not ident.startswith(parent + '/'):
            raise ValueError('child identifier outside parent')
        seen.add(ident)
        children = []
        fragments = []
        for index, child in enumerate(el):
            if child.tag in LEVELS:
                children.append((index, child))
            elif child.tag == NS + 'notes':
                notes.append({'owner': ident, 'position': index, 'xml': ET.tostring(child, encoding='unicode')})
            else:
                if any(d.tag in LEVELS for d in child.iter()):
                    raise ValueError('unsupported wrapped provision')
                fragments.append({'position': index, 'xml': ET.tostring(child, encoding='unicode')})
                for ref in child.iter(NS + 'ref'):
                    references.append({'source': ident, 'target': ref.get('href'), 'text': ''.join(ref.itertext())})
        nodes.append({'id': ident, 'kind': el.tag.removeprefix(NS), 'leading_text': el.text or '', 'xml_fragments': fragments, 'tail': el.tail or ''})
        if parent:
            edges.append({'source': parent, 'target': ident, 'type': 'contains', 'position': position})
        for index, child in children:
            visit(child, ident, index)

    for section in sections:
        visit(section)
    for ref in references:
        ref['status'] = 'resolved' if ref['target'] in seen else 'unresolved'
    return {'schema_version': 1, 'edition': edition, 'source_url': source_url, 'scope': scope,
            'sha256': digest, 'byte_count': len(raw), 'nodes': nodes, 'edges': edges,
            'notes': notes, 'references': references}


def canonical_json(graph):
    return json.dumps(graph, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n'
