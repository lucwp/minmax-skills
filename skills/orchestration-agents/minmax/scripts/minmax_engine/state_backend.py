from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any, Dict, List

from .cloud import package_state_hash
from .common import ensure_dir, now_iso, sha256_bytes, write_json


BACKEND_FORMAT = 1
MAX_OVERLAY_PAYLOAD_BYTES = 16 * 1024 * 1024


def _iter_overlay_files(home: Path):
    root = home / 'overlays'
    if not root.exists():
        return
    for path in sorted(root.rglob('*')):
        if path.is_file():
            yield path.relative_to(root).as_posix(), path


def build_backend_state(home: Path, packages: List[Dict[str, Any]], config: Any) -> Dict[str, Any]:
    overlay_payloads: Dict[str, Dict[str, Any]] = {}
    total = 0
    for rel, path in _iter_overlay_files(home) or []:
        data = path.read_bytes()
        total += len(data)
        if total > MAX_OVERLAY_PAYLOAD_BYTES:
            raise ValueError('overlay payload exceeds backend export limit')
        overlay_payloads[rel] = {
            'sha256': sha256_bytes(data),
            'encoding': 'base64',
            'content': base64.b64encode(data).decode('ascii'),
        }
    return {
        'format': BACKEND_FORMAT,
        'kind': 'minmax-state-backend',
        'exported_at': now_iso(),
        'state_hash': package_state_hash(packages),
        'packages': packages,
        'targets': dict(config.targets),
        'target_lifecycle': dict(config.target_lifecycle),
        'backend': {
            'provider': config.state_backend_provider,
            'repository': config.state_backend_repository,
            'state_path': config.state_backend_state_path,
            'require_private': bool(config.state_backend_require_private),
        },
        'overlays': overlay_payloads,
    }


def export_backend_state(home: Path, packages: List[Dict[str, Any]], config: Any, output: Path) -> Dict[str, Any]:
    output = output.expanduser().resolve()
    ensure_dir(output.parent)
    state = build_backend_state(home, packages, config)
    write_json(output, state)
    return {
        'output': str(output),
        'state_hash': state['state_hash'],
        'package_count': len(packages),
        'overlay_file_count': len(state['overlays']),
    }


def read_backend_state(path: Path) -> Dict[str, Any]:
    path = path.expanduser().resolve()
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('format') != BACKEND_FORMAT or data.get('kind') != 'minmax-state-backend':
        raise ValueError('unsupported MinMax backend-state format')
    if package_state_hash(data.get('packages', [])) != data.get('state_hash'):
        raise ValueError('backend-state package hash mismatch')
    overlays = data.get('overlays', {})
    if not isinstance(overlays, dict):
        raise ValueError('backend-state overlays must be an object')
    total = 0
    for rel, item in overlays.items():
        if not rel or rel.startswith('/') or '..' in Path(rel).parts:
            raise ValueError(f'unsafe overlay path: {rel}')
        if item.get('encoding') != 'base64':
            raise ValueError(f'unsupported overlay encoding: {rel}')
        try:
            raw = base64.b64decode(item.get('content', ''), validate=True)
        except Exception as exc:
            raise ValueError(f'invalid overlay payload: {rel}') from exc
        total += len(raw)
        if total > MAX_OVERLAY_PAYLOAD_BYTES:
            raise ValueError('overlay payload exceeds backend import limit')
        if sha256_bytes(raw) != item.get('sha256'):
            raise ValueError(f'overlay hash mismatch: {rel}')
    return data


def restore_backend_overlays(home: Path, state: Dict[str, Any]) -> None:
    root = ensure_dir(home / 'overlays')
    for rel, item in state.get('overlays', {}).items():
        target = (root / rel).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError as exc:
            raise ValueError(f'unsafe overlay target path: {rel}') from exc
        ensure_dir(target.parent)
        target.write_bytes(base64.b64decode(item['content'], validate=True))
