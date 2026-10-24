"""Portable input integrity checks; no API, source download, or sandbox needed."""
import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('restore_main_preparation', ROOT/'scripts/restore_main_preparation.py')
restore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(restore)


class FrozenPreparationTest(unittest.TestCase):
    def test_shipped_inventory_and_extracted_metadata(self):
        manifest, payload = restore.load_bundle(restore.DEFAULT_BUNDLE)
        self.assertEqual(manifest['questions'], 200)
        self.assertEqual(set(manifest['source_counts'].values()), {40})
        self.assertEqual(len(payload['files']), 1160)
        self.assertEqual(sum(k.endswith('/tasks.jsonl') for k in payload['files']), 40)
        self.assertEqual(sum(k.endswith('/pilot_manifest.json') for k in payload['files']), 160)
        for text in payload['files'].values():
            json.loads(text)

    def test_path_relocation_is_one_pass_and_preserves_scientific_content(self):
        value = {'package': '/old/repo/runs/reference/prepared/task',
                 'source': '/old/repo/external/sources/native',
                 'facts': ['unchanged scientific fact', 0.125, True, None]}
        result = restore.relocate(value, '/old/repo', '/old/repo/runs/reference/prepared',
                                  Path('/old/repo-copy'), Path('/old/repo-copy/runs/new/prepared'))
        self.assertEqual(result['package'], '/old/repo-copy/runs/new/prepared/task')
        self.assertEqual(result['source'], '/old/repo-copy/external/sources/native')
        self.assertEqual(result['facts'], value['facts'])
        self.assertEqual(value['package'], '/old/repo/runs/reference/prepared/task')

    def test_rejects_traversal_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)/'root';root.mkdir()
            outside = Path(directory)/'outside';outside.mkdir()
            (root/'link').symlink_to(outside)
            for value in ['../outside/data', '/absolute', 'a/../../b', r'a\b', 'link/data']:
                with self.subTest(value=value), self.assertRaises(ValueError):
                    restore.safe_path(root, value)

    def test_archive_corruption_is_detected_before_unpacking(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            manifest = (restore.DEFAULT_BUNDLE/'manifest.json').read_bytes()
            (target/'manifest.json').write_bytes(manifest)
            raw = bytearray((restore.DEFAULT_BUNDLE/'preparation.json.gz').read_bytes())
            raw[len(raw)//2] ^= 1
            (target/'preparation.json.gz').write_bytes(raw)
            with self.assertRaisesRegex(ValueError, 'checksum'):
                restore.load_bundle(target)

    def test_existing_preparation_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory);(run/'prepared').mkdir()
            marker = run/'prepared/keep';marker.write_text('original')
            with self.assertRaisesRegex(ValueError, 'Refusing to replace'):
                restore.restore(Path('/nonexistent'), ROOT, run)
            self.assertEqual(marker.read_text(), 'original')


if __name__ == '__main__':
    unittest.main()
