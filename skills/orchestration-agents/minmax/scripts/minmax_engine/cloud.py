from __future__ import annotations

import json
import os
import shutil
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Iterator

from .common import ensure_dir, new_id, now_iso, sha256_bytes, write_json


def package_state_hash(packages: List[Dict[str, Any]]) -> str:
    stable = []
    for pkg in sorted(packages, key=lambda p: p['id']):
        stable.append({
            'id': pkg['id'], 'name': pkg['name'], 'source': pkg['source'], 'tracking': pkg['tracking'],
            'artifact_hash': pkg['artifact_hash'], 'effective_hash': pkg['effective_hash'],
            'overlay_hash': pkg.get('overlay_hash'), 'pinned': bool(pkg.get('pinned')), 'targets': sorted(pkg.get('targets', [])),
            'trust': pkg.get('trust', 'UNVERIFIED'), 'risk': pkg.get('risk', 'MEDIUM')
        })
    payload = json.dumps(stable, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return sha256_bytes(payload)


class CloudStore:
    LOCK_TIMEOUT_SECONDS = 30.0
    STALE_LOCK_SECONDS = 3600.0

    def __init__(self, path: Path):
        self.root = path.expanduser().resolve()
        ensure_dir(self.root)
        self.state_path = self.root / 'state.json'
        self.lock_path = self.root / '.minmax-sync.lock'

    def read_state(self) -> Dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        return json.loads(self.state_path.read_text(encoding='utf-8'))

    @contextmanager
    def _exclusive_lock(self) -> Iterator[None]:
        deadline = time.monotonic() + self.LOCK_TIMEOUT_SECONDS
        token = f'{os.getpid()}:{time.time()}'.encode('utf-8')
        while True:
            try:
                fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                with os.fdopen(fd, 'wb') as handle:
                    handle.write(token)
                break
            except FileExistsError:
                try:
                    age = time.time() - self.lock_path.stat().st_mtime
                    if age > self.STALE_LOCK_SECONDS:
                        self.lock_path.unlink(missing_ok=True)
                        continue
                except FileNotFoundError:
                    continue
                if time.monotonic() >= deadline:
                    raise RuntimeError('cloud sync lock timeout')
                time.sleep(0.025)
        try:
            yield
        finally:
            try:
                if self.lock_path.read_bytes() == token:
                    self.lock_path.unlink(missing_ok=True)
            except FileNotFoundError:
                pass

    def _copy_missing_tree(self, src_root: Path, dst_root: Path) -> None:
        if not src_root.exists():
            return
        for src in sorted(src_root.rglob('*')):
            rel = src.relative_to(src_root)
            dst = dst_root / rel
            if src.is_dir():
                ensure_dir(dst)
            elif src.is_file() and not dst.exists():
                ensure_dir(dst.parent)
                shutil.copy2(src, dst)

    def push(self, home: Path, packages: List[Dict[str, Any]], device_id: str, expected_revision: str | None) -> Dict[str, Any]:
        with self._exclusive_lock():
            current = self.read_state()
            current_revision = current.get('revision') if current else None
            if current_revision != expected_revision:
                raise RuntimeError('cloud revision changed after plan creation')
            # Cloud state stores registry metadata and overlay deltas, never full package copies.
            self._copy_missing_tree(home / 'overlays', self.root / 'overlays')
            revision = new_id('rev')
            state = {
                'format': 1, 'revision': revision, 'parent_revision': current_revision,
                'device_id': device_id, 'updated_at': now_iso(),
                'state_hash': package_state_hash(packages), 'packages': packages
            }
            write_json(self.state_path, state)
            return state

    def pull_assets(self, home: Path) -> None:
        self._copy_missing_tree(self.root / 'overlays', home / 'overlays')
