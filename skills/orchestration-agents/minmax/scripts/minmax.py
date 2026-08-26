#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from minmax_engine.common import tree_hash
from minmax_engine.discovery import fingerprint, resolution_summary, score_candidate, search_queries
from minmax_engine.inspector import inspect
from minmax_engine.render import render_compact, render_global_update, render_install_plan, render_update_plan, should_use_ansi
from minmax_engine.sources import MultiplePackagesError, SourceError, SourceResolver
from minmax_engine.transactions import PackageManager, TransactionError
from minmax_engine.registry import AmbiguousPackageError

_OUTPUT_MODE = 'compact'


def emit(payload: Any, exit_code: int = 0, renderer=None) -> None:
    if _OUTPUT_MODE == 'json':
        print(json.dumps(payload, separators=(',', ':'), sort_keys=True))
    elif renderer is not None:
        print(renderer(payload, ansi=should_use_ansi(_OUTPUT_MODE)))
    else:
        print(render_compact(payload, ansi=should_use_ansi(_OUTPUT_MODE)))
    raise SystemExit(exit_code)


def parse_target(values: List[str]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for value in values:
        if '=' not in value:
            raise ValueError(f'target must be NAME=PATH: {value}')
        name, path = value.split('=', 1)
        name = name.strip()
        if not name or not path.strip():
            raise ValueError(f'invalid target: {value}')
        result[name] = str(Path(path).expanduser().resolve())
    return result


def source_is_unresolved(pkg: Dict[str, Any]) -> bool:
    source = pkg.get('source', {})
    return (
        source.get('resolution_status') == 'UNRESOLVED'
        or source.get('provider') in {'unresolved', 'local-adopted'}
        or source.get('origin_known') is False
        or not source.get('canonical_url')
    )


def source_args_for_package(pkg: Dict[str, Any]) -> Dict[str, Any]:
    source = pkg['source']
    if source_is_unresolved(pkg):
        raise TransactionError('UNRESOLVED SOURCE: discover and confirm the package origin before checking upstream')
    branch = pkg['tracking'].get('ref') if pkg['tracking'].get('mode') == 'branch' else None
    return {
        'source_ref': source['canonical_url'],
        'package_path': source.get('package_path') if source.get('package_path') not in {None, '.'} else None,
        'branch': branch,
        'explicit_ref': None,
    }


def unresolved_item(pm: PackageManager, pkg: Dict[str, Any]) -> Dict[str, Any]:
    fp = fingerprint(pm.installed_root(pkg, allow_drift=True))
    return {
        'package_id': pkg['id'], 'name': pkg['name'], 'status': 'UNRESOLVED SOURCE',
        'artifact_hash': pkg['artifact_hash'], 'search_queries': search_queries(fp),
        'observed_path': pkg.get('source', {}).get('observed_path') or pkg.get('source', {}).get('canonical_url'),
    }


def cmd_setup(pm: PackageManager, args: argparse.Namespace) -> None:
    targets = parse_target(args.target)
    plan = pm.plan_setup(targets, scan=args.scan)
    emit({'action': 'review_required', 'plan': plan})


def cmd_scan(pm: PackageManager, args: argparse.Namespace) -> None:
    emit(pm.scan_installed())


def cmd_install(pm: PackageManager, args: argparse.Namespace) -> None:
    resolver = SourceResolver()
    materialized = resolver.materialize(args.source, package_path=args.package_path, branch=args.branch, explicit_ref=args.ref)
    try:
        plan = pm.plan_install(materialized, args.target or None, output=args.output)
    finally:
        materialized.cleanup()
    emit({'action': 'review_required', 'plan': plan}, renderer=lambda payload, ansi: render_install_plan(payload['plan'], ansi=ansi))


def _remote_unchanged(resolver: SourceResolver, pkg: Dict[str, Any]) -> bool:
    current_commit = pkg.get('source', {}).get('commit') or pkg.get('tracking', {}).get('resolved_commit')
    if not current_commit:
        return False
    probe = resolver.probe(**source_args_for_package(pkg))
    return bool(probe and probe.get('commit') == current_commit)


def cmd_check(pm: PackageManager, args: argparse.Namespace) -> None:
    resolver = SourceResolver()
    results = []
    unresolved = []
    inventory = pm.scan_installed()
    for pkg in pm.registry.list_packages():
        item = {'package_id': pkg['id'], 'name': pkg['name'], 'pinned': pkg['pinned']}
        install_state = pm.package_install_state(pkg)
        if install_state['state'] != 'installed':
            item.update({'status': install_state['state'], 'install_state': install_state})
            results.append(item)
            continue
        if source_is_unresolved(pkg):
            unresolved.append(unresolved_item(pm, pkg))
            item.update({'status': 'source_unresolved'})
            results.append(item)
            continue
        try:
            if _remote_unchanged(resolver, pkg):
                item.update({'status': 'up_to_date', 'installed_hash': pkg['artifact_hash'], 'candidate_hash': pkg['artifact_hash']})
                results.append(item)
                continue
            materialized = resolver.materialize(**source_args_for_package(pkg))
            try:
                candidate_hash = tree_hash(materialized.package_root)
                item.update({
                    'status': 'update_available' if candidate_hash != pkg['artifact_hash'] else 'up_to_date',
                    'installed_hash': pkg['artifact_hash'], 'candidate_hash': candidate_hash,
                    'candidate_tracking': materialized.tracking, 'candidate_source': materialized.source,
                })
            finally:
                materialized.cleanup()
        except Exception as exc:
            item.update({'status': 'check_failed', 'error': str(exc)})
        results.append(item)
    emit({
        'packages': results,
        'updates_available': sum(1 for x in results if x['status'] == 'update_available'),
        'unresolved_sources': unresolved,
        'unmanaged': inventory['unmanaged'],
    })

def _global_update(pm: PackageManager) -> Dict[str, Any]:
    resolver = SourceResolver()
    plans = []
    unresolved = []
    up_to_date = []
    failures = []
    inventory = pm.scan_installed()
    packages = pm.registry.list_packages()
    for pkg in packages:
        install_state = pm.package_install_state(pkg)
        if install_state['state'] != 'installed':
            failures.append({'package_id': pkg['id'], 'name': pkg['name'], 'status': install_state['state']})
            continue
        if source_is_unresolved(pkg):
            unresolved.append(unresolved_item(pm, pkg))
            continue
        try:
            if _remote_unchanged(resolver, pkg):
                up_to_date.append({'package_id': pkg['id'], 'name': pkg['name']})
                continue
            materialized = resolver.materialize(**source_args_for_package(pkg))
            try:
                if tree_hash(materialized.package_root) == pkg['artifact_hash']:
                    up_to_date.append({'package_id': pkg['id'], 'name': pkg['name']})
                    continue
                if pkg['pinned']:
                    failures.append({'package_id': pkg['id'], 'name': pkg['name'], 'status': 'pinned_update_available'})
                    continue
                plans.append(pm.plan_update(pkg, materialized))
            finally:
                materialized.cleanup()
        except Exception as exc:
            failures.append({'package_id': pkg['id'], 'name': pkg['name'], 'status': 'check_failed', 'error': str(exc)})
    return {
        'action': 'global_update_review', 'plans': plans, 'unresolved_sources': unresolved,
        'unmanaged': inventory['unmanaged'], 'up_to_date': up_to_date, 'failures': failures,
        'summary': {
            'managed': len(packages), 'plans': len(plans), 'unresolved': len(unresolved),
            'unmanaged': len(inventory['unmanaged']), 'up_to_date': len(up_to_date), 'failures': len(failures),
        },
    }

def cmd_update(pm: PackageManager, args: argparse.Namespace) -> None:
    if not args.package:
        emit(_global_update(pm), renderer=render_global_update)
    pkg = pm.registry.get_package(args.package)
    if not pkg:
        emit({'error': 'package_not_found', 'package': args.package}, 2)
    install_state = pm.package_install_state(pkg)
    if install_state['state'] != 'installed':
        emit({'error': 'package_not_installed', 'package': pkg['name'], 'install_state': install_state}, 2)
    if source_is_unresolved(pkg):
        emit({'action': 'source_resolution_required', **unresolved_item(pm, pkg)}, 2)
    resolver = SourceResolver()
    try:
        if _remote_unchanged(resolver, pkg):
            emit({'status': 'up_to_date', 'package_id': pkg['id'], 'name': pkg['name']})
    except Exception:
        pass
    materialized = resolver.materialize(**source_args_for_package(pkg))
    try:
        if tree_hash(materialized.package_root) == pkg['artifact_hash']:
            emit({'status': 'up_to_date', 'package_id': pkg['id'], 'name': pkg['name']})
        plan = pm.plan_update(pkg, materialized)
    finally:
        materialized.cleanup()
    emit({'action': 'review_required', 'plan': plan}, renderer=lambda payload, ansi: render_update_plan(payload['plan'], ansi=ansi))

def _local_root_for_discovery(pm: PackageManager, args: argparse.Namespace) -> tuple[Path, Dict[str, Any] | None]:
    if args.package:
        pkg = pm.registry.get_package(args.package)
        if not pkg:
            raise TransactionError('package not found')
        return pm.installed_root(pkg, allow_drift=True), pkg
    if args.path:
        root = Path(args.path).expanduser().resolve()
        if not root.is_dir():
            raise TransactionError('local skill path not found')
        return root, None
    raise TransactionError('provide a package or --path')


def cmd_discover_source(pm: PackageManager, args: argparse.Namespace) -> None:
    local_root, pkg = _local_root_for_discovery(pm, args)
    local_fp = fingerprint(local_root)
    resolver = SourceResolver()
    scored = []
    failures = []
    for ref in args.candidate:
        try:
            materialized = resolver.materialize(ref, package_path=args.package_path)
            try:
                candidate_fp = fingerprint(materialized.package_root)
                result = score_candidate(local_fp, candidate_fp, materialized.source)
                result['reference'] = ref
                result['tracking'] = materialized.tracking
                result['aliases'] = materialized.aliases
                scored.append(result)
            finally:
                materialized.cleanup()
        except Exception as exc:
            failures.append({'reference': ref, 'error': str(exc)})
    scored.sort(key=lambda x: x['confidence'], reverse=True)
    resolution = resolution_summary(scored)
    emit({
        'package_id': pkg['id'] if pkg else None,
        'name': local_fp['name'], 'resolution': resolution,
        'search_queries': search_queries(local_fp), 'candidates': scored, 'failures': failures,
        'rule': 'name match alone is never sufficient for automatic source binding',
    })


def cmd_link_source(pm: PackageManager, args: argparse.Namespace) -> None:
    pkg = pm.registry.get_package(args.package)
    if not pkg:
        emit({'error': 'package_not_found', 'package': args.package}, 2)
    local_fp = fingerprint(pm.installed_root(pkg, allow_drift=True))
    resolver = SourceResolver()
    materialized = resolver.materialize(args.source, package_path=args.package_path, branch=args.branch, explicit_ref=args.ref)
    try:
        resolution = score_candidate(local_fp, fingerprint(materialized.package_root), materialized.source)
        if resolution['status'] == 'REJECTED':
            emit({'error': 'source_not_linkable', 'resolution': resolution}, 2)
        plan = pm.plan_link_source(pkg, materialized, resolution)
    finally:
        materialized.cleanup()
    emit({'action': 'review_required', 'plan': plan})


def cmd_inspect(pm: PackageManager, args: argparse.Namespace) -> None:
    resolver = SourceResolver()
    materialized = resolver.materialize(args.source, package_path=args.package_path, branch=args.branch, explicit_ref=args.ref)
    try:
        result = inspect(materialized.package_root)
        result['source'] = materialized.source
        result['tracking'] = materialized.tracking
        result['artifact_hash'] = tree_hash(materialized.package_root)
        result['aliases'] = materialized.aliases
    finally:
        materialized.cleanup()
    emit(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='minmax', description='MinMax Package Manager - deterministic package engine for AI skills')
    parser.add_argument('--home', default='~/.minmax', help='MinMax registry/config path (metadata only)')
    parser.add_argument('--format', choices=['compact', 'json', 'ansi'], default='compact', help='compact by default; use json for full machine-readable detail')
    sub = parser.add_subparsers(dest='command', required=True)

    p = sub.add_parser('setup')
    p.add_argument('--scan', action='store_true', default=False)
    p.add_argument('--target', action='append', default=[], help='NAME=PATH')

    sub.add_parser('scan')

    p = sub.add_parser('install')
    p.add_argument('source')
    p.add_argument('--package-path')
    p.add_argument('--branch')
    p.add_argument('--ref')
    p.add_argument('--target', action='append', default=[])
    p.add_argument('--output', help='create a user-facing installable zip; required when no writable target is configured')

    p = sub.add_parser('inspect')
    p.add_argument('source')
    p.add_argument('--package-path')
    p.add_argument('--branch')
    p.add_argument('--ref')

    sub.add_parser('check')
    p = sub.add_parser('update')
    p.add_argument('package', nargs='?')

    p = sub.add_parser('discover-source')
    p.add_argument('package', nargs='?')
    p.add_argument('--path')
    p.add_argument('--candidate', action='append', default=[])
    p.add_argument('--package-path')

    p = sub.add_parser('link-source')
    p.add_argument('package')
    p.add_argument('source')
    p.add_argument('--package-path')
    p.add_argument('--branch')
    p.add_argument('--ref')

    p = sub.add_parser('apply')
    p.add_argument('plan_id')

    sub.add_parser('status')
    sub.add_parser('drift')
    sub.add_parser('recover')

    p = sub.add_parser('pin')
    p.add_argument('package')
    p = sub.add_parser('unpin')
    p.add_argument('package')

    p = sub.add_parser('track')
    p.add_argument('package')
    p.add_argument('--branch', required=True)

    p = sub.add_parser('rollback')
    p.add_argument('package')
    p.add_argument('--steps', type=int, default=1)

    p = sub.add_parser('adopt-overlay')
    p.add_argument('package')
    p.add_argument('--target', required=True)

    sub.add_parser('sync-targets')

    p = sub.add_parser('cloud-config')
    p.add_argument('--path', required=True)
    p = sub.add_parser('sync-cloud')
    p.add_argument('--direction', choices=['push', 'pull'], required=True)

    p = sub.add_parser('export-state')
    p.add_argument('--output', required=True)
    p = sub.add_parser('import-state')
    p.add_argument('archive')

    return parser


def main() -> None:
    global _OUTPUT_MODE
    parser = build_parser()
    args = parser.parse_args()
    _OUTPUT_MODE = args.format
    home = Path(args.home).expanduser().resolve()
    pm = PackageManager(home)
    try:
        if args.command == 'setup':
            cmd_setup(pm, args)
        if args.command == 'scan':
            cmd_scan(pm, args)
        if args.command == 'install':
            cmd_install(pm, args)
        if args.command == 'inspect':
            cmd_inspect(pm, args)
        if args.command == 'check':
            cmd_check(pm, args)
        if args.command == 'update':
            cmd_update(pm, args)
        if args.command == 'discover-source':
            cmd_discover_source(pm, args)
        if args.command == 'link-source':
            cmd_link_source(pm, args)
        if args.command == 'apply':
            emit(pm.apply(args.plan_id))
        if args.command == 'status':
            emit(pm.status())
        if args.command == 'drift':
            emit(pm.drift())
        if args.command == 'recover':
            emit(pm.recover())
        if args.command in {'pin', 'unpin'}:
            pkg = pm.registry.get_package(args.package)
            if not pkg:
                emit({'error': 'package_not_found'}, 2)
            emit({'action': 'review_required', 'plan': pm.plan_pin(pkg, args.command == 'pin')})
        if args.command == 'track':
            pkg = pm.registry.get_package(args.package)
            if not pkg:
                emit({'error': 'package_not_found'}, 2)
            emit({'action': 'review_required', 'plan': pm.plan_track_branch(pkg, args.branch)})
        if args.command == 'rollback':
            pkg = pm.registry.get_package(args.package)
            if not pkg:
                emit({'error': 'package_not_found'}, 2)
            emit({'action': 'review_required', 'plan': pm.plan_rollback(pkg, args.steps)})
        if args.command == 'adopt-overlay':
            pkg = pm.registry.get_package(args.package)
            if not pkg:
                emit({'error': 'package_not_found'}, 2)
            emit({'action': 'review_required', 'plan': pm.plan_adopt_overlay(pkg, args.target)})
        if args.command == 'sync-targets':
            emit({'action': 'review_required', 'plan': pm.plan_sync_targets()})
        if args.command == 'cloud-config':
            emit({'action': 'review_required', 'plan': pm.plan_cloud_config(args.path)})
        if args.command == 'sync-cloud':
            emit({'action': 'review_required', 'plan': pm.plan_cloud_sync(args.direction)})
        if args.command == 'export-state':
            emit(pm.export_state(args.output))
        if args.command == 'import-state':
            emit({'action': 'review_required', 'plan': pm.plan_import_state(args.archive)})
        parser.error('unhandled command')
    except MultiplePackagesError as exc:
        emit({'error': 'multiple_packages', 'package_roots': exc.roots, 'hint': 'repeat with --package-path PATH'}, 2)
    except SourceError as exc:
        emit({'error': 'source_error', 'message': str(exc)}, 2)
    except AmbiguousPackageError as exc:
        emit({'error': 'ambiguous_package', 'name': exc.name, 'package_ids': exc.package_ids, 'hint': 'repeat with an exact package id or alias'}, 2)
    except TransactionError as exc:
        emit({'error': 'transaction_error', 'message': str(exc)}, 3)
    except ValueError as exc:
        emit({'error': 'integrity_error', 'message': str(exc)}, 4)
    except Exception as exc:
        emit({'error': 'operational_error', 'message': str(exc)}, 5)
    finally:
        pm.close()


if __name__ == '__main__':
    main()
