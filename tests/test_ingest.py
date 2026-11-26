import unittest
import xml.etree.ElementTree as ET
from legal_archaeology.ingest import ingest, canonical_json

BASE = '/us/usc/t17/s109'
URL = 'https://uscode.house.gov/us/usc/119-121/t17/s109/'
FIXTURE = f'''<section xmlns="http://xml.house.gov/schemas/uslm/1.0" identifier="{BASE}"><num>109</num><subsection identifier="{BASE}/b"><paragraph identifier="{BASE}/b/1"><subparagraph identifier="{BASE}/b/1/B"><chapeau>This subsection does not apply to—</chapeau><clause identifier="{BASE}/b/1/B/ii"><content>a computer program embodied in or used in conjunction with a limited purpose computer that is designed for playing video games and may be designed for other purposes.</content></clause></subparagraph></paragraph></subsection><subsection identifier="{BASE}/d"><content>Test reference <ref href="{BASE}/b">internal</ref> and <ref href="/us/usc/t17/s106">external</ref>.</content></subsection><notes><note>Fixture note, not enacted text.</note></notes></section>'''.encode()


def run(raw=FIXTURE, **kw):
    return ingest(raw, **({'edition': '119-121', 'source_url': URL, 'scope': 'fixture', 'expected_sections': [BASE]} | kw))


class IngestionTests(unittest.TestCase):
    def test_nested_clause(self):
        g = run()
        n = next(n for n in g['nodes'] if n['id'].endswith('/ii'))
        self.assertIn('designed for playing video games', n['xml_fragments'][0]['xml'])
        self.assertEqual(len(g['nodes']), 6)
        self.assertEqual(len(g['edges']), 5)

    def test_notes_and_references(self):
        g = run()
        self.assertEqual(len(g['notes']), 1)
        self.assertEqual([r['status'] for r in g['references']], ['resolved', 'unresolved'])
        self.assertNotIn('Fixture note', str(g['nodes']))

    def test_determinism_and_edition(self):
        self.assertEqual(canonical_json(run()), canonical_json(run()))
        self.assertNotEqual(canonical_json(run()), canonical_json(run(edition='other')))
        self.assertNotEqual(run()['sha256'], run(FIXTURE + b' ')['sha256'])

    def test_missing_section(self):
        with self.assertRaises(ValueError):
            run(expected_sections=[BASE, '/us/usc/t17/s106'])

    def test_duplicate_identifier(self):
        with self.assertRaises(ValueError):
            run(FIXTURE.replace(b'/s109/d', b'/s109/b'))

    def test_bad_input(self):
        with self.assertRaises(ET.ParseError):
            run(FIXTURE[:-20])
        with self.assertRaises(ValueError):
            run(b'<!DOCTYPE section>' + FIXTURE)
        with self.assertRaises(ValueError):
            run(scope='complete')

    def test_wrong_parent(self):
        with self.assertRaises(ValueError):
            run(FIXTURE.replace(b'/s109/b/1/B/ii', b'/s109/b/1/ii'))
