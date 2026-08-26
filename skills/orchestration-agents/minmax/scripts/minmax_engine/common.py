from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable

IGNORED_NAMES = {'.git', '__pycache__', '.DS_Store'}


def now_iso() -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def atomic_write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    fd, tmp = tempfile.mkstemp(prefix=path.name + '.', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True) + '\n')


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob('*')):
        if not path.is_file() and not path.is_symlink():
            continue
        rel = path.relative_to(root)
        if any(part in IGNORED_NAMES for part in rel.parts):
            continue
        if path.is_symlink():
            target = path.resolve()
            try:
                target.relative_to(root.resolve())
            except ValueError as exc:
                raise ValueError(f'symlink escapes package root: {rel}') from exc
        yield path


def tree_manifest(root: Path) -> Dict[str, str]:
    root = root.resolve()
    manifest: Dict[str, str] = {}
    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            manifest[rel] = 'symlink:' + os.readlink(path)
        else:
            manifest[rel] = sha256_file(path)
    return manifest


def tree_hash(root: Path) -> str:
    payload = json.dumps(tree_manifest(root), sort_keys=True, separators=(',', ':')).encode('utf-8')
    return sha256_bytes(payload)


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    ensure_dir(dst.parent)
    shutil.copytree(src, dst, symlinks=False, ignore=shutil.ignore_patterns('.git', '__pycache__', '.DS_Store'))


def safe_child(root: Path, child: Path) -> Path:
    root = root.expanduser().resolve()
    child = child.expanduser().resolve()
    try:
        child.relative_to(root)
    except ValueError as exc:
        raise ValueError(f'path escapes allowed root: {child}') from exc
    return child


def new_id(prefix: str) -> str:
    return f'{prefix}_{uuid.uuid4().hex[:16]}'


def package_id(source_identity: str, package_path: str) -> str:
    raw = f'{source_identity}::{package_path}'.encode('utf-8')
    return 'pkg_' + hashlib.sha256(raw).hexdigest()[:20]


def read_skill_name(root: Path) -> str:
    entry = root / 'SKILL.md'
    if not entry.exists():
        entry = root / 'skill.md'
    if entry.exists():
        try:
            text = entry.read_text(encoding='utf-8', errors='replace')
            if text.startswith('---'):
                end = text.find('\n---', 3)
                if end != -1:
                    for line in text[3:end].splitlines():
                        if line.strip().startswith('name:'):
                            value = line.split(':', 1)[1].strip().strip('"\'')
                            if value:
                                return value
        except OSError:
            pass
    return root.name


def normalize_path_text(path: Path) -> str:
    return str(path.expanduser().resolve())
