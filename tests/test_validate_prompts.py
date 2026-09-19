"""Fixture tests for publication checks; no network, agents, or GitHub writes."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('validate_prompts', BASE/'tools/validate_prompts.py')
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class PublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry = json.loads((BASE/'PROMPT_REGISTRY.json').read_text())
        for entry in self.registry['roles'].values():
            target = self.root/entry['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((BASE/entry['path']).read_bytes())
        self.write_registry()

    def write_registry(self) -> None:
        (self.root/'PROMPT_REGISTRY.json').write_text(json.dumps(self.registry)+'\n')

    def invalid(self) -> None:
        self.write_registry()
        with self.assertRaises((MODULE.ValidationError, OSError, UnicodeError, json.JSONDecodeError)):
            MODULE.validate(self.root)

    def test_valid_documents(self):
        self.assertEqual(len(MODULE.validate(self.root)), 2)

    def test_unreferenced_newer_file_is_not_selected(self):
        (self.root/'Universal_Master_Prompt_v999_999.md').write_text('unapproved draft\n')
        found = MODULE.validate(self.root)
        self.assertEqual(found[0]['path'], self.registry['roles']['universal']['path'])

    def test_missing_role(self):
        del self.registry['roles']['universal']
        self.invalid()

    def test_unapproved_role(self):
        self.registry['roles']['universal']['status'] = 'draft'
        self.invalid()

    def test_changed_document(self):
        with (self.root/self.registry['roles']['universal']['path']).open('a') as stream:
            stream.write('unexpected change\n')
        self.invalid()

    def test_missing_document(self):
        (self.root/self.registry['roles']['universal']['path']).unlink()
        self.invalid()

    def test_parent_path(self):
        self.registry['roles']['universal']['path'] = '../outside.md'
        self.invalid()

    def test_absolute_path(self):
        self.registry['roles']['universal']['path'] = '/outside.md'
        self.invalid()

    def test_symlink_document(self):
        entry = self.registry['roles']['universal']
        path = self.root/entry['path']
        actual = self.root/'actual.md'
        path.rename(actual)
        path.symlink_to(actual)
        self.invalid()

    def test_duplicate_role_json_key(self):
        text = json.dumps(self.registry).replace('"roles": {', '"roles": {}, "roles": {', 1)
        (self.root/'PROMPT_REGISTRY.json').write_text(text)
        with self.assertRaises(MODULE.ValidationError):
            MODULE.validate(self.root)

    def test_cyclic_dependencies(self):
        self.registry['roles']['universal']['requires'] = {'infrastructure':'incremental-infrastructure'}
        self.invalid()

    def test_contract_mismatch(self):
        self.registry['roles']['infrastructure']['requires']['universal'] = 'different-contract'
        self.invalid()

    def test_version_mismatch(self):
        self.registry['roles']['universal']['declared_version'] = '99_0'
        self.invalid()

    def test_boolean_schema_is_not_integer_schema(self):
        self.registry['schema_version'] = True
        self.invalid()

    def test_no_approval_provenance(self):
        self.registry['approval_basis'] = ''
        self.invalid()

    def test_version_pinned_dependency(self):
        entry = self.registry['roles']['infrastructure']
        path = self.root/entry['path']
        data = path.read_bytes()+b'Load Universal_Master_Prompt_v0_1.md\n'
        path.write_bytes(data)
        entry['sha256'] = hashlib.sha256(data).hexdigest()
        self.invalid()

    def test_missing_step_even_with_matching_digest(self):
        entry = self.registry['roles']['universal']
        path = self.root/entry['path']
        data = path.read_bytes().replace(b'## STEP 8 ', b'## OMITTED 8 ', 1)
        path.write_bytes(data)
        entry['sha256'] = hashlib.sha256(data).hexdigest()
        self.invalid()

    def test_malformed_dependency_entry_with_reordered_roles(self):
        self.registry['roles'] = {'infrastructure': self.registry['roles']['infrastructure'],
                                  'universal': None}
        self.invalid()

    def test_future_versions_require_only_new_documents_and_registry(self):
        for role, entry in self.registry['roles'].items():
            old_version = entry['declared_version']
            old_path = self.root/entry['path']
            new_name = entry['path'].replace('_v'+old_version, '_v17_4')
            data = old_path.read_bytes().replace(('v'+old_version).encode(), b'v17_4')
            (self.root/new_name).write_bytes(data)
            entry.update(path=new_name, declared_version='17_4',
                         sha256=hashlib.sha256(data).hexdigest())
        self.write_registry()
        self.assertEqual({item['version'] for item in MODULE.validate(self.root)}, {'17_4'})

    def test_multiple_roles_same_path(self):
        self.registry['roles']['extra'] = copy.deepcopy(self.registry['roles']['universal'])
        self.invalid()

if __name__ == '__main__':
    unittest.main()
