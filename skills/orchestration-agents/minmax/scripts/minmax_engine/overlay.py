from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .common import ensure_dir, sha256_bytes, tree_manifest, copy_tree, write_json


class OverlayManager:
    def __init__(self, home: Path):
        self.root = ensure_dir(home / 'overlays')

    def overlay_path(self, package_id: str, overlay_hash: str) -> Path:
        return self.root / package_id / overlay_hash

    def create(self, package_id: str, base: Path, local: Path) -> Dict[str, Any]:
        base_files = tree_manifest(base)
        local_files = tree_manifest(local)
        modified: Dict[str, Dict[str, str | None]] = {}
        deleted: Dict[str, str] = {}
        changed_paths = sorted(set(base_files) | set(local_files))

        with tempfile.TemporaryDirectory(prefix='minmax-overlay-') as tmp:
            tmp_root = Path(tmp)
            files_root = ensure_dir(tmp_root / 'files')
            for rel in changed_paths:
                b = base_files.get(rel)
                l = local_files.get(rel)
                if b == l:
                    continue
                if l is None:
                    deleted[rel] = b or ''
                    continue
                modified[rel] = {'base_hash': b, 'overlay_hash': l}
                src = local / rel
                dst = files_root / rel
                ensure_dir(dst.parent)
                shutil.copy2(src, dst)
            manifest = {'format': 1, 'modified': modified, 'deleted': deleted}
            payload = json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode('utf-8')
            overlay_hash = sha256_bytes(payload + json.dumps(tree_manifest(files_root), sort_keys=True).encode('utf-8'))
            dst = self.overlay_path(package_id, overlay_hash)
            if not dst.exists():
                ensure_dir(dst.parent)
                copy_tree(tmp_root, dst)
                write_json(dst / 'manifest.json', manifest)
        return {'overlay_hash': overlay_hash, 'manifest': manifest, 'changed_files': sorted(modified), 'deleted_files': sorted(deleted)}

    def load(self, package_id: str, overlay_hash: str) -> Dict[str, Any]:
        path = self.overlay_path(package_id, overlay_hash)
        if not path.exists():
            raise FileNotFoundError(f'overlay not found: {overlay_hash}')
        with (path / 'manifest.json').open('r', encoding='utf-8') as handle:
            manifest = json.load(handle)
        return {'path': path, 'manifest': manifest}

    def simulate(self, package_id: str, overlay_hash: str, new_base: Path) -> Dict[str, Any]:
        info = self.load(package_id, overlay_hash)
        manifest = info['manifest']
        new_files = tree_manifest(new_base)
        conflicts: List[str] = []
        for rel, meta in manifest.get('modified', {}).items():
            base_hash = meta.get('base_hash')
            overlay_hash_value = meta.get('overlay_hash')
            current = new_files.get(rel)
            if base_hash is None:
                if current is not None and current != overlay_hash_value:
                    conflicts.append(rel)
            elif current != base_hash and current != overlay_hash_value:
                conflicts.append(rel)
        for rel, base_hash in manifest.get('deleted', {}).items():
            current = new_files.get(rel)
            if current is not None and current != base_hash:
                conflicts.append(rel)
        return {'clean': not conflicts, 'conflicts': sorted(set(conflicts))}

    def apply(self, package_id: str, overlay_hash: str, new_base: Path, destination: Path) -> Dict[str, Any]:
        simulation = self.simulate(package_id, overlay_hash, new_base)
        if not simulation['clean']:
            return simulation
        info = self.load(package_id, overlay_hash)
        manifest = info['manifest']
        copy_tree(new_base, destination)
        for rel in manifest.get('deleted', {}):
            path = destination / rel
            if path.exists():
                path.unlink()
        for rel in manifest.get('modified', {}):
            src = info['path'] / 'files' / rel
            dst = destination / rel
            ensure_dir(dst.parent)
            shutil.copy2(src, dst)
        return {'clean': True, 'conflicts': []}
