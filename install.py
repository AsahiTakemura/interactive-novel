#!/usr/bin/env python3
"""Install both Codex skills, backing up updates and preserving user memories.

Python 3.9+, standard library only. No network or shell commands.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
MANAGED = {
    'yoshino-tone': (
        'SKILL.md', 'agents/openai.yaml',
        'references/character-model.md', 'references/dialogue-examples.md',
        'references/source-notes.md', 'references/continuity.md',
    ),
    'interactive-novel': ('SKILL.md', 'README.md', 'scripts/selector.py'),
}
MEMORIES = ('profile.md', 'continuity.md', 'fiction.md')


def is_link(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & 0x400)


def check_path(path, root):
    path.relative_to(root)
    current = path
    while current != root:
        if is_link(current):
            raise ValueError(f'Refusing symbolic link or junction: {current}')
        current = current.parent
    path.resolve().relative_to(root)


def regular_bytes(path):
    check_path(path, PACKAGE)
    if not path.is_file():
        raise ValueError(f'Missing or non-regular input file: {path}')
    return path.read_bytes()


def verify_package():
    manifest = PACKAGE / 'SHA256SUMS.txt'
    if not manifest.exists():
        return
    for line in regular_bytes(manifest).decode('utf-8').splitlines():
        digest, relative = line.split('  ', 1)
        actual = hashlib.sha256(regular_bytes(PACKAGE / relative)).hexdigest()
        if actual != digest:
            raise ValueError(f'Package checksum mismatch: {relative}')


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.skill-', delete=False) as file:
        temporary = Path(file.name)
        file.write(data)
    try:
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def install(codex_root, agents_root=None, dry_run=False):
    codex = Path(codex_root).expanduser().resolve()
    agents = Path(agents_root or Path.home() / '.agents').expanduser().resolve()
    for root in (codex, agents):
        if root.exists() and not root.is_dir():
            raise ValueError(f'Skill home is not a directory: {root}')
    verify_package()
    novel_codex = codex / 'skills' / 'interactive-novel'
    novel_agents = agents / 'skills' / 'interactive-novel'
    for path, root in ((novel_codex, codex), (novel_agents, agents)):
        check_path(path, root)
    if novel_codex.exists() and novel_agents.exists() and novel_codex != novel_agents:
        raise ValueError('Duplicate interactive-novel installs exist in both homes. Resolve the duplicate before updating.')
    novel_root = agents if novel_agents.exists() else codex
    targets = {
        'yoshino-tone': (codex / 'skills' / 'yoshino-tone', codex),
        'interactive-novel': (novel_root / 'skills' / 'interactive-novel', novel_root),
    }
    plans = []
    # Validate all inputs and destinations before changing either skill.
    for name, (target, root) in targets.items():
        source = PACKAGE / 'skills' / name
        if target == source or PACKAGE in target.parents or target in PACKAGE.parents:
            raise ValueError('Install destinations must be separate from this package.')
        check_path(target, root)
        if target.exists() and not target.is_dir():
            raise ValueError(f'Target is not a directory: {target}')
        content = {relative: regular_bytes(source / relative) for relative in MANAGED[name]}
        if not content['SKILL.md'].decode('utf-8-sig').startswith('---'):
            raise ValueError(f'{name}/SKILL.md is missing its metadata frontmatter.')
        if name == 'yoshino-tone':
            for memory in MEMORIES:
                destination = target / 'memory' / memory
                check_path(destination, root)
                if destination.exists():
                    if not destination.is_file():
                        raise ValueError(f'Existing memory is not a file: {destination}')
                else:
                    content[f'memory/{memory}'] = regular_bytes(PACKAGE / 'memory-templates' / memory)
        changed = {}
        for relative, data in content.items():
            destination = target / relative
            check_path(destination, root)
            if destination.exists() and not destination.is_file():
                raise ValueError(f'Existing destination is not a file: {destination}')
            if not destination.exists() or destination.read_bytes() != data:
                changed[relative] = data
        if changed:
            if target.exists():
                for existing in target.rglob('*'):
                    check_path(existing, root)
            plans.append((name, target, content, changed))
    if not plans:
        print('Both skills are already up to date.')
        return
    for name, target, _, changed in plans:
        print(f'Target: {target}\nFiles to install: {", ".join(changed)}')
    if dry_run:
        print('Dry run: no files changed.')
        return
    # Back up every existing target before writing any managed file.
    for name, target, _, _ in plans:
        if target.exists():
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            backup = codex / 'backups' / f'{name}-{stamp}'
            check_path(backup, codex)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(target, backup)
            print(f'Previous skill backed up to: {backup}')
    for name, target, content, changed in plans:
        for relative, data in changed.items():
            atomic_write(target / relative, data)
        for relative, data in content.items():
            if (target / relative).read_bytes() != data:
                raise OSError(f'Verification failed for {name}/{relative}')
        print(f'Installed and verified: {name}')
    print('Existing memories, progress, custom files and AGENTS.md were preserved.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-home', default=os.environ.get('CODEX_HOME') or str(Path.home() / '.codex'))
    parser.add_argument('--agents-home', default=str(Path.home() / '.agents'))
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        install(args.codex_home, args.agents_home, args.dry_run)
    except (OSError, ValueError) as error:
        print(f'Install stopped: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
