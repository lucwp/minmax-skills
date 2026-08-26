from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List

from .cloud import package_state_hash
from .common import ensure_dir, now_iso, sha256_file, write_json
from .sources import MAX_DOWNLOAD_BYTES, MAX_ARCHIVE_FILES, MAX_EXTRACTED_BYTES, MAX_SINGLE_FILE_BYTES, MAX_COMPRESSION_RATIO


def export_state(home: Path, packages: List[Dict[str, Any]], output: Path) -> Dict[str, Any]:
    output = output.expanduser().resolve()
    ensure_dir(output.parent)
    with tempfile.TemporaryDirectory(prefix='minmax-export-') as tmp:
        root = Path(tmp) / 'state'
        ensure_dir(root)
        state = {'format': 1, 'exported_at': now_iso(), 'state_hash': package_state_hash(packages), 'packages': packages}
        write_json(root / 'state.json', state)
        # Persist only metadata plus local overlay deltas. Package contents stay source-backed.
        src = home / 'overlays'
        if src.exists():
            shutil.copytree(src, root / 'overlays')
        archive_base = output.with_suffix('') if output.suffix == '.zip' else output
        made = Path(shutil.make_archive(str(archive_base), 'zip', root_dir=root))
        if made != output:
            if output.exists():
                output.unlink()
            made.replace(output)
    return {'output': str(output), 'sha256': sha256_file(output), 'state_hash': state['state_hash'], 'package_count': len(packages)}


def stage_import(home: Path, archive: Path) -> Dict[str, Any]:
    archive = archive.expanduser().resolve()
    if not zipfile.is_zipfile(archive):
        raise ValueError('state import must be a zip archive')
    staging = ensure_dir(home / 'staging' / ('import-' + sha256_file(archive)[:16]))
    if any(staging.iterdir()):
        shutil.rmtree(staging)
        ensure_dir(staging)
    if archive.stat().st_size > MAX_DOWNLOAD_BYTES:
        raise ValueError('state archive exceeds compressed size limit')
    with zipfile.ZipFile(archive) as zf:
        members = zf.infolist()
        total = sum(m.file_size for m in members if not m.is_dir())
        if len(members) > MAX_ARCHIVE_FILES or total > MAX_EXTRACTED_BYTES:
            raise ValueError('state archive exceeds extraction limits')
        if archive.stat().st_size > 0 and total / archive.stat().st_size > MAX_COMPRESSION_RATIO:
            raise ValueError('state archive compression ratio exceeds safety limit')
        for member in members:
            mode = (member.external_attr >> 16) & 0o170000
            if mode == 0o120000 or member.flag_bits & 0x1:
                raise ValueError(f'unsafe state archive entry: {member.filename}')
            if member.file_size > MAX_SINGLE_FILE_BYTES:
                raise ValueError(f'state archive entry exceeds size limit: {member.filename}')
            target = (staging / member.filename).resolve()
            try:
                target.relative_to(staging.resolve())
            except ValueError as exc:
                raise ValueError(f'unsafe state archive path: {member.filename}') from exc
            if member.is_dir():
                ensure_dir(target)
                continue
            ensure_dir(target.parent)
            with zf.open(member, 'r') as src, target.open('wb') as out:
                shutil.copyfileobj(src, out, length=1024 * 1024)
    state_path = staging / 'state.json'
    if not state_path.is_file():
        raise ValueError('state archive is missing state.json')
    state = json.loads(state_path.read_text(encoding='utf-8'))
    if package_state_hash(state.get('packages', [])) != state.get('state_hash'):
        raise ValueError('state archive package-state hash mismatch')
    return {'archive': str(archive), 'archive_hash': sha256_file(archive), 'staging': str(staging), 'state': state}
