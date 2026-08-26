from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .cloud import CloudStore, package_state_hash
from .common import copy_tree, ensure_dir, new_id, now_iso, package_id, read_skill_name, safe_child, tree_hash
from .config import Config
from .discovery import fingerprint, search_queries
from .inspector import classify_update_risk, diff_inspections, inspect
from .overlay import OverlayManager
from .registry import Registry
from .sources import SourceError, SourceResolver
from .state_transfer import export_state, stage_import
from .render import build_visual_diff
from .transaction_errors import TransactionError

class OpsMixin:
    def plan_sync_targets(self) -> Dict[str, Any]:
        drift = self.drift()['drift']
        package_ids = sorted(set(item['package_id'] for item in drift))
        expected = {pkg['id']: pkg['effective_hash'] for pkg in self.registry.list_packages() if pkg['id'] in package_ids}
        return self.create_plan('target-sync', {'package_ids': package_ids, 'expected_effective_hashes': expected, 'drift': drift})

    def export_state(self, output: str) -> Dict[str, Any]:
        return export_state(self.home, self.registry.list_packages(), Path(output))

    def plan_import_state(self, archive: str) -> Dict[str, Any]:
        staged = stage_import(self.home, Path(archive))
        return self.create_plan('import-state', {
            'archive': staged['archive'], 'archive_hash': staged['archive_hash'],
            'staging': staged['staging'], 'state_hash': staged['state']['state_hash'],
            'packages': staged['state']['packages'],
        })

    def plan_cloud_config(self, path: str) -> Dict[str, Any]:
        resolved = str(Path(path).expanduser().resolve())
        return self.create_plan('cloud-config', {'from': self.config.cloud_path, 'to': resolved})

    def plan_cloud_sync(self, direction: str) -> Dict[str, Any]:
        if direction not in {'push', 'pull'}:
            raise TransactionError('cloud direction must be push or pull')
        if not self.config.cloud_path:
            raise TransactionError('cloud path is not configured')
        cloud = CloudStore(Path(self.config.cloud_path))
        remote = cloud.read_state()
        remote_revision = remote.get('revision') if remote else None
        packages = self.registry.list_packages()
        local_hash = package_state_hash(packages)
        if direction == 'pull' and not remote:
            raise TransactionError('cloud state does not exist')
        return self.create_plan('cloud-sync', {
            'direction': direction, 'expected_remote_revision': remote_revision,
            'expected_local_state_hash': local_hash,
            'remote_state_hash': remote.get('state_hash') if remote else None,
        })

    def recover(self) -> Dict[str, Any]:
        recovered = []
        for tx in self.registry.incomplete_transactions():
            if tx['state'] not in {'APPLYING', 'FAILED', 'APPROVED', 'STAGED'}:
                continue
            # Target writes are transactional and self-restoring. Recovery only clears stale transaction state.
            self.registry.set_transaction_state(tx['id'], 'ROLLED_BACK')
            recovered.append(tx['id'])
        return {'recovered': recovered, 'count': len(recovered)}

    def status(self) -> Dict[str, Any]:
        packages = self.registry.list_packages()
        states = {pkg['id']: self.package_install_state(pkg) for pkg in packages}
        return {
            'home': str(self.home), 'device_id': self.config.device_id,
            'managed_packages': len(packages), 'installed': sum(1 for s in states.values() if s['state'] == 'installed'),
            'registered_only': sum(1 for s in states.values() if s['state'] == 'registered_only'),
            'pinned': sum(1 for p in packages if p['pinned']),
            'overlays': sum(1 for p in packages if p.get('overlay_hash')),
            'targets': self.config.targets, 'cloud_path': self.config.cloud_path,
            'incomplete_transactions': self.registry.incomplete_transactions(),
            'packages': [{**pkg, 'install_state': states[pkg['id']]} for pkg in packages],
        }

    def drift(self) -> Dict[str, Any]:
        findings = []
        for pkg in self.registry.list_packages():
            expected = pkg['effective_hash']
            for target in pkg.get('targets', []):
                root_text = self.config.targets.get(target)
                if not root_text:
                    findings.append({'package_id': pkg['id'], 'package': pkg['name'], 'target': target, 'state': 'target_unconfigured', 'expected_hash': expected})
                    continue
                path = Path(root_text).expanduser().resolve() / pkg['name']
                if not path.is_dir():
                    findings.append({'package_id': pkg['id'], 'package': pkg['name'], 'target': target, 'state': 'missing', 'expected_hash': expected})
                    continue
                try:
                    actual = tree_hash(path)
                except Exception as exc:
                    findings.append({'package_id': pkg['id'], 'package': pkg['name'], 'target': target, 'state': 'error', 'error': str(exc)})
                    continue
                if actual != expected:
                    findings.append({'package_id': pkg['id'], 'package': pkg['name'], 'target': target, 'state': 'drift', 'expected_hash': expected, 'actual_hash': actual})
        return {'drift': findings, 'count': len(findings)}

