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

class CoreMixin:
    def __init__(self, home: Path):
        self.home = home.expanduser().resolve()
        ensure_dir(self.home)
        self.config = Config(self.home)
        self.registry = Registry(self.home)
        self.overlays = OverlayManager(self.home)
        ensure_dir(self.home / 'staging')

    def close(self) -> None:
        self.registry.close()

    def create_plan(self, tx_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        txid = new_id('txn')
        plan = {'format': 2, 'id': txid, 'type': tx_type, 'created_at': now_iso(), **payload}
        self.registry.create_transaction(txid, tx_type, plan)
        return plan

    def _target_path(self, pkg: Dict[str, Any], target_name: str) -> Path:
        root_text = self.config.targets.get(target_name)
        if not root_text:
            raise TransactionError(f'target is not configured: {target_name}')
        root = Path(root_text).expanduser().resolve()
        return safe_child(root, root / pkg['name'])

    def installed_root(self, pkg: Dict[str, Any], *, allow_drift: bool = False) -> Path:
        """Return an installed target path; prefer a path matching the registered hash."""
        candidates: List[Tuple[Path, str | None]] = []
        for target_name in pkg.get('targets', []):
            try:
                path = self._target_path(pkg, target_name)
            except TransactionError:
                continue
            if not path.is_dir():
                continue
            try:
                digest = tree_hash(path)
            except Exception:
                digest = None
            if digest == pkg.get('effective_hash'):
                return path
            candidates.append((path, digest))
        if allow_drift and candidates:
            return candidates[0][0]
        observed = pkg.get('source', {}).get('observed_path')
        if allow_drift and observed:
            path = Path(observed).expanduser().resolve()
            if path.is_dir():
                return path
        if not pkg.get('targets'):
            raise TransactionError(f'package {pkg.get("name", pkg.get("id"))} is registered but not installed')
        raise TransactionError(f'no clean installed target found for {pkg.get("name", pkg.get("id"))}')

    def package_install_state(self, pkg: Dict[str, Any]) -> Dict[str, Any]:
        if not pkg.get('targets'):
            return {'state': 'registered_only', 'installed_targets': [], 'missing_targets': [], 'drift_targets': []}
        installed: List[str] = []
        missing: List[str] = []
        drift: List[str] = []
        for target in pkg.get('targets', []):
            try:
                path = self._target_path(pkg, target)
            except TransactionError:
                missing.append(target)
                continue
            if not path.is_dir():
                missing.append(target)
                continue
            try:
                digest = tree_hash(path)
            except Exception:
                drift.append(target)
                continue
            if digest == pkg.get('effective_hash'):
                installed.append(target)
            else:
                drift.append(target)
        state = 'installed' if installed and not missing and not drift else ('partial' if installed else 'not_installed')
        return {'state': state, 'installed_targets': installed, 'missing_targets': missing, 'drift_targets': drift}

    def _materialize_recorded(self, pkg: Dict[str, Any]):
        source = pkg.get('source', {})
        if not source.get('canonical_url') or source.get('resolution_status') == 'UNRESOLVED':
            raise TransactionError('UNRESOLVED SOURCE: package content cannot be reconstructed')
        tracking = pkg.get('tracking', {})
        provider = source.get('provider')
        exact_ref = tracking.get('resolved_commit') or source.get('commit')
        if not exact_ref and provider in {'github', 'gitlab', 'git'}:
            exact_ref = tracking.get('resolved_ref')
        resolver = SourceResolver()
        try:
            return resolver.materialize(
                source['canonical_url'],
                package_path=source.get('package_path') if source.get('package_path') not in {None, '.'} else None,
                explicit_ref=exact_ref if provider in {'github', 'gitlab', 'git'} else None,
            )
        except SourceError as exc:
            raise TransactionError(f'could not reconstruct registered source: {exc}') from exc

    def _verify_materialized(self, pkg: Dict[str, Any], materialized: Any) -> None:
        digest = tree_hash(materialized.package_root)
        if digest != pkg['artifact_hash']:
            raise TransactionError(
                f'resolved source no longer matches reviewed artifact: expected {pkg["artifact_hash"]}, got {digest}'
            )

    def _effective_root(self, pkg: Dict[str, Any], materialized: Any, tmp_root: Path) -> Path:
        self._verify_materialized(pkg, materialized)
        if not pkg.get('overlay_hash'):
            if pkg['effective_hash'] != pkg['artifact_hash']:
                raise TransactionError('effective hash differs from artifact hash without an overlay')
            return materialized.package_root
        dest = tmp_root / 'effective'
        result = self.overlays.apply(pkg['id'], pkg['overlay_hash'], materialized.package_root, dest)
        if not result['clean']:
            raise TransactionError('overlay conflict blocks materialization')
        digest = tree_hash(dest)
        if digest != pkg['effective_hash']:
            raise TransactionError(f'effective overlay hash mismatch: expected {pkg["effective_hash"]}, got {digest}')
        return dest

    def _materialize_targets(self, pkg: Dict[str, Any], source_root: Path) -> List[str]:
        targets = list(pkg.get('targets', []))
        if not targets:
            raise TransactionError('no install target configured')
        applied: List[Tuple[Path, Path | None]] = []
        installed: List[str] = []
        try:
            for target_name in targets:
                root_text = self.config.targets.get(target_name)
                if not root_text:
                    raise TransactionError(f'unknown target during apply: {target_name}')
                root = Path(root_text).expanduser().resolve()
                ensure_dir(root)
                dest = safe_child(root, root / pkg['name'])
                stage = safe_child(root, root / ('.minmax-stage-' + pkg['id']))
                backup = safe_child(root, root / ('.minmax-backup-' + pkg['id']))
                if stage.exists():
                    shutil.rmtree(stage)
                if backup.exists():
                    shutil.rmtree(backup)
                copy_tree(source_root, stage)
                if tree_hash(stage) != pkg['effective_hash']:
                    raise TransactionError(f'target staging hash mismatch: {target_name}')
                had_dest = dest.exists()
                if had_dest:
                    os.replace(dest, backup)
                os.replace(stage, dest)
                applied.append((dest, backup if had_dest else None))
                installed.append(target_name)
            for _, backup in applied:
                if backup and backup.exists():
                    shutil.rmtree(backup)
            return installed
        except Exception:
            for dest, backup in reversed(applied):
                if dest.exists():
                    shutil.rmtree(dest)
                if backup and backup.exists():
                    os.replace(backup, dest)
            raise

    def _write_delivery_archive(self, source_root: Path, output: str) -> str:
        output_path = Path(output).expanduser().resolve()
        if output_path.suffix.lower() != '.zip':
            output_path = output_path.with_suffix('.zip')
        ensure_dir(output_path.parent)
        with tempfile.TemporaryDirectory(prefix='minmax-delivery-') as tmp:
            clean = Path(tmp) / 'skill'
            copy_tree(source_root, clean)
            archive_base = output_path.with_suffix('')
            made = Path(shutil.make_archive(str(archive_base), 'zip', root_dir=clean))
            if made != output_path:
                if output_path.exists():
                    output_path.unlink()
                made.replace(output_path)
        return str(output_path)
