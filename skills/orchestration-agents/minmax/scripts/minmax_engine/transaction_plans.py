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

class PlanningMixin:
    def plan_setup(self, targets: Dict[str, str], scan: bool = True) -> Dict[str, Any]:
        proposed_targets = dict(self.config.targets)
        proposed_targets.update(targets)
        if scan and not targets:
            proposed_targets.update(self.config.detect_targets())
        adopted_by_id: Dict[str, Dict[str, Any]] = {}
        for target_name, root_text in proposed_targets.items():
            root = Path(root_text).expanduser().resolve()
            if not root.is_dir():
                continue
            for child in sorted(root.iterdir()):
                if not child.is_dir() or not ((child / 'SKILL.md').exists() or (child / 'skill.md').exists()):
                    continue
                resolved = str(child.resolve())
                digest = tree_hash(child)
                name = read_skill_name(child)
                sid = 'unresolved:' + digest
                pid = package_id('package:' + digest, name)
                if pid in adopted_by_id:
                    item = adopted_by_id[pid]
                    item['targets'] = sorted(set([*item['targets'], target_name]))
                    item['aliases'] = list(dict.fromkeys([*item.get('aliases', []), resolved]))
                    observed = item['source'].setdefault('observed_paths', [])
                    if resolved not in observed:
                        observed.append(resolved)
                    continue
                adopted_by_id[pid] = {
                    'id': pid, 'name': name,
                    'source': {
                        'provider': 'unresolved', 'canonical_url': None, 'stable_id': sid, 'package_path': '.',
                        'origin_known': False, 'resolution_status': 'UNRESOLVED', 'observed_path': resolved,
                        'observed_paths': [resolved],
                    },
                    'tracking': {'mode': 'unresolved', 'ref': None, 'resolved_type': 'content', 'resolved_ref': None},
                    'artifact_hash': digest, 'effective_hash': digest, 'overlay_hash': None, 'pinned': False,
                    'targets': [target_name], 'trust': 'UNVERIFIED', 'risk': inspect(child)['risk'],
                    'aliases': [resolved],
                }
        adopted = sorted(adopted_by_id.values(), key=lambda x: (x['name'], x['id']))
        return self.create_plan('setup', {'targets': proposed_targets, 'adopted_packages': adopted})

    def scan_installed(self) -> Dict[str, Any]:
        managed = self.registry.list_packages()
        managed_paths = set()
        for pkg in managed:
            for target_name in pkg.get('targets', []):
                root_text = self.config.targets.get(target_name)
                if root_text:
                    managed_paths.add(str((Path(root_text).expanduser().resolve() / pkg['name']).resolve()))
        unmanaged = []
        seen = set()
        for target_name, root_text in sorted(self.config.targets.items()):
            root = Path(root_text).expanduser().resolve()
            if not root.is_dir():
                continue
            for child in sorted(root.iterdir()):
                if not child.is_dir() or not ((child / 'SKILL.md').is_file() or (child / 'skill.md').is_file()):
                    continue
                resolved = str(child.resolve())
                if resolved in seen or resolved in managed_paths:
                    continue
                seen.add(resolved)
                fp = fingerprint(child)
                unmanaged.append({
                    'name': fp['name'], 'path': resolved, 'target': target_name,
                    'artifact_hash': fp['tree_hash'], 'source_status': 'UNRESOLVED SOURCE',
                    'search_queries': search_queries(fp),
                })
        unresolved = []
        for pkg in managed:
            source = pkg.get('source', {})
            if not source.get('origin_known', source.get('provider') not in {'unresolved', 'local-adopted'}) or source.get('resolution_status') == 'UNRESOLVED':
                try:
                    fp = fingerprint(self.installed_root(pkg, allow_drift=True))
                    queries = search_queries(fp)
                except Exception:
                    queries = [pkg['name']]
                unresolved.append({
                    'package_id': pkg['id'], 'name': pkg['name'], 'artifact_hash': pkg['artifact_hash'],
                    'source_status': 'UNRESOLVED SOURCE', 'search_queries': queries,
                    'observed_path': source.get('observed_path') or source.get('canonical_url'),
                })
        return {'managed': managed, 'unresolved_sources': unresolved, 'unmanaged': unmanaged}

    def plan_link_source(self, current: Dict[str, Any], materialized: Any, resolution: Dict[str, Any]) -> Dict[str, Any]:
        if resolution.get('status') == 'REJECTED':
            raise TransactionError('candidate source evidence is insufficient')
        current_source = current.get('source', {})
        if current_source.get('origin_known') and current_source.get('resolution_status') != 'UNRESOLVED':
            current_key = (current_source.get('stable_id'), current_source.get('package_path', '.'))
            candidate_key = (materialized.source.get('stable_id'), materialized.source.get('package_path', '.'))
            if current_key != candidate_key:
                raise TransactionError('package already has a different verified source; explicit source switch is required')
        candidate_source = dict(materialized.source)
        candidate_source.update({'origin_known': True, 'resolution_status': 'RESOLVED'})
        candidate_hash = tree_hash(materialized.package_root)
        baseline_exact = candidate_hash == current['artifact_hash']
        risk = 'LOW' if baseline_exact and resolution.get('status') == 'CONFIRMED' else 'HIGH'
        reasons = [] if risk == 'LOW' else ['source linked without an exact current-artifact match; review first update carefully']
        return self.create_plan('link-source', {
            'package_id': current['id'], 'current_source': current_source, 'current_tracking': current['tracking'],
            'candidate_source': candidate_source, 'candidate_tracking': dict(materialized.tracking),
            'candidate_artifact_hash': candidate_hash, 'baseline_exact': baseline_exact,
            'resolution': resolution, 'risk': {'level': risk, 'reasons': reasons},
            'aliases': materialized.aliases,
        })

    def plan_install(self, materialized: Any, requested_targets: List[str] | None = None, output: str | None = None) -> Dict[str, Any]:
        inspection = inspect(materialized.package_root)
        artifact_hash = tree_hash(materialized.package_root)
        source = dict(materialized.source)
        source.update({'origin_known': True, 'resolution_status': 'RESOLVED'})
        tracking = dict(materialized.tracking)
        source_identity = source['stable_id']
        pid = package_id(source_identity, source.get('package_path', '.'))
        name = read_skill_name(materialized.package_root)
        if not name or '/' in name or '\\' in name or name in {'.', '..'}:
            raise TransactionError('invalid package name in SKILL.md')

        existing = self.registry.get_package(pid)
        if existing and existing['artifact_hash'] != artifact_hash:
            raise TransactionError(f'package already registered as {existing["name"]}; use update for changed content')

        requested = list(requested_targets or [])
        unknown_targets = [t for t in requested if t not in self.config.targets]
        if unknown_targets:
            raise TransactionError('unknown targets: ' + ', '.join(unknown_targets))
        defaults = sorted(self.config.targets) if not requested else []
        previous = list(existing.get('targets', [])) if existing else []
        targets = sorted(set([*previous, *requested, *defaults]))
        delivery_output = str(Path(output).expanduser().resolve()) if output else None
        if not targets and not delivery_output:
            raise TransactionError('no install target is configured; provide --output to create an installable zip')

        trust = 'VERIFIED' if source.get('provider') == 'github' else ('KNOWN' if source.get('provider') in {'gitlab', 'git', 'archive', 'local'} else 'UNVERIFIED')
        pkg = {
            'id': pid, 'name': name, 'source': source, 'tracking': tracking,
            'artifact_hash': artifact_hash, 'effective_hash': artifact_hash,
            'overlay_hash': existing.get('overlay_hash') if existing else None,
            'pinned': bool(existing.get('pinned')) if existing else False,
            'targets': targets, 'trust': existing.get('trust', trust) if existing else trust,
            'risk': inspection['risk'],
        }
        return self.create_plan('install', {
            'package': pkg, 'existing_artifact_hash': existing['artifact_hash'] if existing else None,
            'aliases': materialized.aliases, 'inspection': inspection,
            'risk': {'level': inspection['risk'], 'reasons': inspection['risk_reasons']},
            'external_skill_requirements': inspection['external_skill_requirements'],
            'delivery_output': delivery_output,
        })

    def plan_update(self, current: Dict[str, Any], materialized: Any) -> Dict[str, Any]:
        if current['pinned']:
            raise TransactionError('package is pinned')
        current_source = current.get('source', {})
        if not current_source.get('origin_known', current_source.get('provider') not in {'unresolved', 'local-adopted'}) or current_source.get('resolution_status') == 'UNRESOLVED':
            raise TransactionError('UNRESOLVED SOURCE: resolve and confirm package origin before updating')
        expected_source = (current_source.get('stable_id'), current_source.get('package_path', '.'))
        candidate_source = (materialized.source.get('stable_id'), materialized.source.get('package_path', '.'))
        if expected_source != candidate_source:
            raise TransactionError('source identity changed; explicit source switch is required')

        old_root = self.installed_root(current)
        new_inspection = inspect(materialized.package_root)
        old_inspection = inspect(old_root)
        diff = diff_inspections(old_inspection, new_inspection)
        visual_diff = build_visual_diff(old_root, materialized.package_root, diff)
        risk = classify_update_risk(new_inspection, diff)
        artifact_hash = tree_hash(materialized.package_root)
        effective_hash = artifact_hash
        overlay_result = {'clean': True, 'conflicts': []}
        if current.get('overlay_hash'):
            overlay_result = self.overlays.simulate(current['id'], current['overlay_hash'], materialized.package_root)
            if overlay_result['clean']:
                with tempfile.TemporaryDirectory(prefix='minmax-effective-') as tmp:
                    dest = Path(tmp) / 'files'
                    self.overlays.apply(current['id'], current['overlay_hash'], materialized.package_root, dest)
                    effective_hash = tree_hash(dest)
            else:
                risk = {'level': 'HIGH' if risk['level'] != 'CRITICAL' else 'CRITICAL', 'reasons': list(dict.fromkeys([*risk['reasons'], 'local overlay conflicts with upstream']))}
        candidate = dict(current)
        candidate.update({
            'source': {**dict(materialized.source), 'origin_known': True, 'resolution_status': 'RESOLVED'},
            'tracking': dict(materialized.tracking), 'artifact_hash': artifact_hash,
            'effective_hash': effective_hash, 'trust': current.get('trust', 'UNVERIFIED'), 'risk': risk['level'],
        })
        return self.create_plan('update', {
            'package_id': current['id'], 'current': current, 'candidate': candidate,
            'aliases': materialized.aliases, 'diff': diff, 'visual_diff': visual_diff,
            'inspection': new_inspection, 'risk': risk, 'overlay': overlay_result,
            'external_skill_requirements': new_inspection['external_skill_requirements'],
        })

    def plan_pin(self, current: Dict[str, Any], pinned: bool) -> Dict[str, Any]:
        return self.create_plan('pin' if pinned else 'unpin', {'package_id': current['id'], 'from': current['pinned'], 'to': pinned})

    def plan_track_branch(self, current: Dict[str, Any], branch: str) -> Dict[str, Any]:
        if not branch.strip():
            raise TransactionError('branch cannot be empty')
        tracking = dict(current['tracking'])
        tracking.update({'mode': 'branch', 'ref': branch.strip(), 'resolved_type': 'branch'})
        return self.create_plan('track', {'package_id': current['id'], 'from': current['tracking'], 'to': tracking})

    def plan_rollback(self, current: Dict[str, Any], steps: int = 1) -> Dict[str, Any]:
        history = self.registry.history(current['id'])
        if steps < 1 or len(history) < steps:
            raise TransactionError('requested rollback history is not available')
        target = history[steps - 1]
        candidate = dict(current)
        candidate.update({
            'artifact_hash': target['artifact_hash'], 'effective_hash': target['effective_hash'],
            'overlay_hash': target.get('overlay_hash'), 'source': target['source'], 'tracking': target['tracking'],
        })
        return self.create_plan('rollback', {'package_id': current['id'], 'current': current, 'candidate': candidate, 'history_steps': steps})

    def plan_adopt_overlay(self, current: Dict[str, Any], target_name: str) -> Dict[str, Any]:
        if target_name not in self.config.targets:
            raise TransactionError(f'unknown target: {target_name}')
        local = self._target_path(current, target_name)
        if not local.is_dir():
            raise TransactionError(f'package not present at target: {target_name}')
        materialized = self._materialize_recorded(current)
        try:
            if tree_hash(materialized.package_root) != current['artifact_hash']:
                raise TransactionError('current upstream base can no longer be reconstructed exactly')
            overlay = self.overlays.create(current['id'], materialized.package_root, local)
        finally:
            materialized.cleanup()
        effective_hash = tree_hash(local)
        return self.create_plan('adopt-overlay', {'package_id': current['id'], 'overlay': overlay, 'effective_hash': effective_hash, 'target': target_name})
