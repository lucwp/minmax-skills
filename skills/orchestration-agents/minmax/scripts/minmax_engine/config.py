from __future__ import annotations

import os
import re
import uuid
from pathlib import Path
from typing import Dict, Optional

from .common import atomic_write_text, ensure_dir


def _quote(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return bytes(value[1:-1], 'utf-8').decode('unicode_escape')
    return value


class Config:
    def __init__(self, home: Path):
        self.home = home.expanduser().resolve()
        self.path = self.home / 'config.toml'
        self.device_id = ''
        self.targets: Dict[str, str] = {}
        self.cloud_path: Optional[str] = None
        self.last_cloud_revision: Optional[str] = None
        self.last_cloud_state_hash: Optional[str] = None
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.device_id = 'dev_' + uuid.uuid4().hex[:16]
            return
        section = ''
        for raw in self.path.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('[') and line.endswith(']'):
                section = line[1:-1]
                continue
            if '=' not in line:
                continue
            key, value = [x.strip() for x in line.split('=', 1)]
            value = _unquote(value)
            if section == 'targets':
                self.targets[key] = value
            elif section == 'cloud':
                if key == 'path':
                    self.cloud_path = value or None
                elif key == 'last_revision':
                    self.last_cloud_revision = value or None
                elif key == 'last_state_hash':
                    self.last_cloud_state_hash = value or None
            elif not section and key == 'device_id':
                self.device_id = value
        if not self.device_id:
            self.device_id = 'dev_' + uuid.uuid4().hex[:16]

    def save(self) -> None:
        ensure_dir(self.home)
        lines = [f'device_id = {_quote(self.device_id)}', '', '[targets]']
        for name in sorted(self.targets):
            lines.append(f'{name} = {_quote(self.targets[name])}')
        lines.extend(['', '[cloud]'])
        lines.append(f'path = {_quote(self.cloud_path or "")}')
        lines.append(f'last_revision = {_quote(self.last_cloud_revision or "")}')
        lines.append(f'last_state_hash = {_quote(self.last_cloud_state_hash or "")}')
        atomic_write_text(self.path, '\n'.join(lines) + '\n')

    def detect_targets(self) -> Dict[str, str]:
        candidates = {
            'codex': Path.home() / '.codex' / 'skills',
            'claude': Path.home() / '.claude' / 'skills',
            'cursor': Path.home() / '.cursor' / 'skills',
            'opencode': Path.home() / '.config' / 'opencode' / 'skills',
        }
        found = {}
        for name, path in candidates.items():
            if path.exists() and path.is_dir():
                found[name] = str(path.resolve())
        return found
