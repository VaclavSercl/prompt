#!/usr/bin/env python3
"""Read-only publication checks for this prompt library; not an agent runtime."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import stat
from pathlib import Path, PurePosixPath
from typing import Any

MAX_BYTES = 512 * 1024
POLICY = 'explicit-owner-selection-else-current-approved-role'

class ValidationError(ValueError):
    """The candidate cannot be published as a consistent approved selection."""

def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValidationError(message)

def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, f'duplicate JSON key: {key}')
        result[key] = value
    return result

def read_safe(root: Path, relative: str) -> bytes:
    require(isinstance(relative, str) and bool(relative), 'path must be nonempty text')
    path = PurePosixPath(relative)
    require(not path.is_absolute() and '\\' not in relative and ':' not in relative,
            'path must be repository-relative POSIX text')
    require(all(part not in ('', '.', '..') for part in relative.split('/')),
            'empty, dot and parent path components are forbidden')
    target = root
    for part in path.parts:
        target = target / part
        require(not target.is_symlink(), 'symlink paths are forbidden')
    require(target.is_file(), f'missing regular file: {relative}')
    require(target.resolve().is_relative_to(root), 'path escapes authorized root')
    before = target.stat()
    require(stat.S_ISREG(before.st_mode) and before.st_size <= MAX_BYTES,
            'unsupported file type or oversized input')
    with target.open('rb') as stream:
        data = stream.read(MAX_BYTES + 1)
    after = target.stat()
    require(len(data) <= MAX_BYTES, 'oversized input')
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
            'input changed while reading')
    require(not target.is_symlink(), 'input became a symlink')
    return data

def validate(root: Path) -> list[dict[str, str]]:
    """Validate the registry's defaults. This does not grant owner approval."""
    root = root.resolve(strict=True)
    raw = read_safe(root, 'PROMPT_REGISTRY.json')
    registry = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object)
    require(isinstance(registry, dict), 'registry must be an object')
    require(type(registry.get('schema_version')) is int and
            registry['schema_version'] == 1, 'unsupported registry schema')
    require(registry.get('kind') == 'owner-approved-prompt-registry', 'wrong registry kind')
    require(registry.get('selection_policy') == POLICY, 'unsupported selection policy')
    require(isinstance(registry.get('approval_basis'), str) and
            bool(registry['approval_basis'].strip()), 'approval provenance is missing')
    roles = registry.get('roles')
    require(isinstance(roles, dict) and 2 <= len(roles) <= 64, 'invalid roles mapping')
    require({'universal', 'infrastructure'} <= roles.keys(), 'required role is missing')
    require(all(isinstance(entry, dict) for entry in roles.values()), 'every role entry must be an object')
    seen_paths: set[str] = set()
    evidence: list[dict[str, str]] = []
    for role, entry in roles.items():
        require(isinstance(role, str) and bool(re.fullmatch(r'[a-z][a-z0-9_-]*', role)),
                'invalid role name')
        require(isinstance(entry, dict), f'invalid entry for {role}')
        require(entry.get('status') == 'approved', f'role {role} is not approved')
        name = entry.get('path')
        require(isinstance(name, str) and name.endswith('.md'), 'invalid document path')
        require(name not in seen_paths, 'multiple roles select the same document')
        seen_paths.add(name)
        data = read_safe(root, name)
        digest = entry.get('sha256')
        require(isinstance(digest, str) and bool(re.fullmatch(r'[a-f0-9]{64}', digest)),
                'invalid SHA-256 digest')
        require(hashlib.sha256(data).hexdigest() == digest, f'content digest mismatch: {role}')
        text = data.decode('utf-8')
        require(text.endswith('\n') and '\x00' not in text, 'invalid document text')
        require(not re.search(r'^(?:<<<<<<<|=======|>>>>>>>)', text, re.M), 'conflict markers')
        require(all(line == line.rstrip() for line in text.splitlines()), 'trailing whitespace')
        require(text.count(f'Canonical filename: `{Path(name).name}`') == 1,
                f'canonical filename mismatch: {role}')
        require(text.count(f'Prompt role: `{role}`') == 1, f'declared role mismatch: {role}')
        version = entry.get('declared_version')
        require(isinstance(version, str) and bool(re.fullmatch(r'\d+(?:_\d+)+', version)),
                'invalid declared version')
        require(Path(name).stem.endswith('_v' + version), 'filename version mismatch')
        heading = '\n'.join(text.splitlines()[:2])
        require(bool(re.search(r'\bv' + re.escape(version) + r'\b', heading)),
                'heading version mismatch')
        contract = entry.get('contract')
        require(isinstance(contract, str) and bool(contract), 'missing contract')
        require(text.count(f'Contract: `{contract}`') == 1, f'declared contract mismatch: {role}')
        requires = entry.get('requires')
        require(isinstance(requires, dict), 'dependencies must be a role-to-contract object')
        refs = re.findall(r'(?:Universal|Infrastructure)_Master_Prompt_v\d+(?:_\d+)+\.md', text)
        require(refs == [Path(name).name], 'version-pinned dependency or duplicated self filename')
        if role == 'universal':
            steps = re.findall(r'^## STEP (\d+) ', text, re.M)
            require(steps == [str(n) for n in range(1, 9)], 'eight-step scope is incomplete')
            require('## DELIVERY CONTRACT' in text, 'delivery contract is missing')
        if role == 'infrastructure':
            sections = re.findall(r'^## (\d+)\. ', text, re.M)
            require(sections == [str(n) for n in range(12)], 'infrastructure scope is incomplete')
            require(requires.get('universal') == roles['universal'].get('contract'),
                    'universal dependency is missing or incompatible')
        evidence.append({'role': role, 'path': name, 'version': version, 'sha256': digest})
    for role, entry in roles.items():
        for dependency, contract in entry['requires'].items():
            require(dependency in roles, f'missing dependency for {role}')
            require(roles[dependency]['contract'] == contract, 'incompatible dependency contract')
    visited: set[str] = set()
    active: set[str] = set()
    def visit(role: str) -> None:
        require(role not in active, 'cyclic prompt dependencies')
        if role in visited:
            return
        active.add(role)
        for dependency in roles[role]['requires']:
            visit(dependency)
        active.remove(role)
        visited.add(role)
    for role in roles:
        visit(role)
    require(read_safe(root, 'PROMPT_REGISTRY.json') == raw, 'registry changed during validation')
    for item in evidence:
        require(hashlib.sha256(read_safe(root, item['path'])).hexdigest() == item['sha256'],
                'document changed during validation')
    return evidence

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=Path('.'))
    args = parser.parse_args()
    try:
        evidence = validate(args.root)
    except (ValidationError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f'FAIL: {exc}')
        return 1
    print(json.dumps({'status': 'PASS', 'scope': 'document integrity, not runtime deployment',
                      'documents': evidence}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
