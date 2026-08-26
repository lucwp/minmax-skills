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

class ApplyMixin:
    def _apply_package_content(self, pkg: Dict[str, Any], delivery_output: str | None = None) -> Dict[str, Any]:
        materialized = self._materialize_recorded(pkg)
        try:
            with tempfile.TemporaryDirectory(prefix='minmax-apply-') as tmp:
                effective = self._effective_root(pkg, materialized, Path(tmp))
                installed = self._materialize_targets(pkg, effective) if pkg.get('targets') else []
                delivered = self._write_delivery_archive(effective, delivery_output) if delivery_output else None
        finally:
            materialized.cleanup()
        return {'installed_targets': installed, 'delivery_output': delivered}

    def apply(self, txid: str) -> Dict[str, Any]:
        try:
            tx = self.registry.claim_transaction(txid)
        except KeyError:
            raise TransactionError(f'unknown plan: {txid}')
        except RuntimeError as exc:
            raise TransactionError(f'plan is not applicable from state {exc}')
        plan = tx['plan']
        tx_type = plan['type']
        try:
            result: Dict[str, Any] = {}
            if tx_type == 'setup':
                self.config.targets = dict(plan['targets'])
                self.config.save()
                entries = []
                for original in plan['adopted_packages']:
                    pkg = dict(original)
                    if not self.registry.get_package(pkg['id']):
                        aliases = pkg.pop('aliases', [])
                        entries.append((pkg, aliases))
                if entries:
                    self.registry.upsert_packages(entries)
            elif tx_type == 'install':
                pkg = dict(plan['package'])
                existing = self.registry.get_package(pkg['id'])
                expected = plan.get('existing_artifact_hash')
                if expected is None and existing is not None:
                    raise TransactionError('install plan is stale: package was registered after review')
                if expected is not None and (not existing or existing['artifact_hash'] != expected):
                    raise TransactionError('install plan is stale: registered package changed after review')
                result = self._apply_package_content(pkg, plan.get('delivery_output'))
                self.registry.upsert_package(pkg, plan.get('aliases', []))
                if result['installed_targets'] and result['delivery_output']:
                    result['install_state'] = 'INSTALLED_AND_EXPORTED'
                elif result['installed_targets']:
                    result['install_state'] = 'INSTALLED'
                else:
                    result['install_state'] = 'DELIVERED_NOT_INSTALLED'
            elif tx_type in {'update', 'rollback'}:
                pkg = dict(plan['candidate'])
                current = self.registry.get_package(pkg['id'])
                if not current:
                    raise TransactionError('package disappeared before apply')
                expected = plan['current']['artifact_hash']
                if current['artifact_hash'] != expected:
                    raise TransactionError('plan is stale: installed artifact changed after review')
                if tx_type == 'update' and not plan.get('overlay', {'clean': True})['clean']:
                    raise TransactionError('overlay conflict blocks update')
                result = self._apply_package_content(pkg)
                self.registry.add_history(current)
                self.registry.upsert_package(pkg, plan.get('aliases', []))
                result['install_state'] = 'INSTALLED'
            elif tx_type == 'link-source':
                pkg = self.registry.get_package(plan['package_id'])
                if not pkg:
                    raise TransactionError('package not found')
                if pkg.get('source') != plan['current_source'] or pkg.get('tracking') != plan['current_tracking']:
                    raise TransactionError('source-link plan is stale')
                pkg['source'] = plan['candidate_source']
                pkg['tracking'] = plan['candidate_tracking']
                pkg['trust'] = 'VERIFIED' if pkg['source'].get('provider') == 'github' else ('KNOWN' if pkg['source'].get('provider') in {'gitlab', 'git', 'archive', 'local'} else 'UNVERIFIED')
                self.registry.upsert_package(pkg, plan.get('aliases', []))
            elif tx_type in {'pin', 'unpin'}:
                pkg = self.registry.get_package(plan['package_id'])
                if not pkg:
                    raise TransactionError('package not found')
                if pkg['pinned'] != plan['from']:
                    raise TransactionError('plan is stale: pin state changed')
                pkg['pinned'] = bool(plan['to'])
                self.registry.upsert_package(pkg)
            elif tx_type == 'track':
                pkg = self.registry.get_package(plan['package_id'])
                if not pkg:
                    raise TransactionError('package not found')
                if pkg['tracking'] != plan['from']:
                    raise TransactionError('plan is stale: tracking policy changed')
                pkg['tracking'] = plan['to']
                self.registry.upsert_package(pkg)
            elif tx_type == 'adopt-overlay':
                pkg = self.registry.get_package(plan['package_id'])
                if not pkg:
                    raise TransactionError('package not found')
                pkg['overlay_hash'] = plan['overlay']['overlay_hash']
                pkg['effective_hash'] = plan['effective_hash']
                self.registry.upsert_package(pkg)
            elif tx_type == 'target-sync':
                installed = []
                for package_id_value in plan['package_ids']:
                    pkg = self.registry.get_package(package_id_value)
                    if not pkg:
                        raise TransactionError('package not found during target sync')
                    if pkg['effective_hash'] != plan['expected_effective_hashes'][package_id_value]:
                        raise TransactionError('target sync plan is stale')
                    installed.extend(self._apply_package_content(pkg)['installed_targets'])
                result['installed_targets'] = installed
            elif tx_type == 'import-state':
                staged = Path(plan['staging'])
                if not staged.is_dir():
                    raise TransactionError('staged import is missing')
                state_path = staged / 'state.json'
                if not state_path.is_file():
                    raise TransactionError('staged import state is missing')
                from .common import sha256_file
                archive_path = Path(plan['archive'])
                if not archive_path.is_file():
                    raise TransactionError('reviewed import archive is missing')
                if sha256_file(archive_path) != plan['archive_hash']:
                    raise TransactionError('import archive changed after review')
                src_root = staged / 'overlays'
                dst_root = self.home / 'overlays'
                if src_root.exists():
                    for src in sorted(src_root.rglob('*')):
                        rel = src.relative_to(src_root)
                        dst = dst_root / rel
                        if src.is_dir():
                            ensure_dir(dst)
                        elif src.is_file() and not dst.exists():
                            ensure_dir(dst.parent)
                            shutil.copy2(src, dst)
                entries = [(pkg, None) for pkg in plan['packages']]
                if entries:
                    self.registry.upsert_packages(entries)
            elif tx_type == 'cloud-config':
                if self.config.cloud_path != plan['from']:
                    raise TransactionError('cloud config plan is stale')
                self.config.cloud_path = plan['to']
                ensure_dir(Path(plan['to']))
                self.config.save()
            elif tx_type == 'cloud-sync':
                if not self.config.cloud_path:
                    raise TransactionError('cloud path is not configured')
                cloud = CloudStore(Path(self.config.cloud_path))
                remote = cloud.read_state()
                remote_revision = remote.get('revision') if remote else None
                if remote_revision != plan['expected_remote_revision']:
                    raise TransactionError('cloud sync plan is stale')
                local_packages = self.registry.list_packages()
                if package_state_hash(local_packages) != plan['expected_local_state_hash']:
                    raise TransactionError('local package state changed after cloud plan review')
                if plan['direction'] == 'push':
                    state = cloud.push(self.home, local_packages, self.config.device_id, remote_revision)
                    self.config.last_cloud_revision = state['revision']
                    self.config.last_cloud_state_hash = state['state_hash']
                    self.config.save()
                else:
                    if not remote:
                        raise TransactionError('cloud state disappeared')
                    if self.config.last_cloud_state_hash and self.config.last_cloud_state_hash != plan['expected_local_state_hash']:
                        raise TransactionError('local state diverged since the last cloud sync')
                    cloud.pull_assets(self.home)
                    entries = [(pkg, None) for pkg in remote.get('packages', [])]
                    if entries:
                        self.registry.upsert_packages(entries)
                    self.config.last_cloud_revision = remote['revision']
                    self.config.last_cloud_state_hash = remote['state_hash']
                    self.config.save()
            else:
                raise TransactionError(f'unsupported transaction type: {tx_type}')
            self.registry.set_transaction_state(txid, 'ACTIVE')
            return {'plan_id': txid, 'state': 'ACTIVE', 'type': tx_type, **result}
        except Exception:
            self.registry.set_transaction_state(txid, 'FAILED')
            raise
