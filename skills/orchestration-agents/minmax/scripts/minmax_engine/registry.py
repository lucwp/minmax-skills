from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .common import ensure_dir, now_iso, write_json


SCHEMA = '''
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS packages (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  source_json TEXT NOT NULL,
  tracking_json TEXT NOT NULL,
  artifact_hash TEXT NOT NULL,
  effective_hash TEXT NOT NULL,
  overlay_hash TEXT,
  pinned INTEGER NOT NULL DEFAULT 0,
  targets_json TEXT NOT NULL,
  trust TEXT NOT NULL,
  risk TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS aliases (
  alias TEXT PRIMARY KEY,
  package_id TEXT NOT NULL REFERENCES packages(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  package_id TEXT NOT NULL,
  artifact_hash TEXT NOT NULL,
  effective_hash TEXT NOT NULL,
  overlay_hash TEXT,
  source_json TEXT NOT NULL,
  tracking_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS transactions (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  state TEXT NOT NULL,
  plan_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
'''


class AmbiguousPackageError(RuntimeError):
    def __init__(self, name: str, package_ids: List[str]):
        super().__init__(f'ambiguous package name {name!r}; use a package id or alias: ' + ', '.join(package_ids))
        self.name = name
        self.package_ids = package_ids


class Registry:
    def __init__(self, home: Path):
        ensure_dir(home)
        self.path = home / 'registry.db'
        self.lock_path = home / 'minmax.lock'
        self.conn = sqlite3.connect(self.path, timeout=30.0)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute('PRAGMA busy_timeout=30000')
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    def _decode(self, row: sqlite3.Row) -> Dict[str, Any]:
        data = dict(row)
        for key in ('source_json', 'tracking_json', 'targets_json', 'plan_json'):
            if key in data:
                data[key[:-5]] = json.loads(data.pop(key))
        if 'pinned' in data:
            data['pinned'] = bool(data['pinned'])
        return data

    def list_packages(self) -> List[Dict[str, Any]]:
        rows = self.conn.execute('SELECT * FROM packages ORDER BY name, id').fetchall()
        return [self._decode(r) for r in rows]

    def get_package(self, key: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute('SELECT * FROM packages WHERE id=?', (key,)).fetchone()
        if row:
            return self._decode(row)
        alias = self.conn.execute('SELECT package_id FROM aliases WHERE alias=?', (key,)).fetchone()
        if alias:
            row = self.conn.execute('SELECT * FROM packages WHERE id=?', (alias['package_id'],)).fetchone()
            if row:
                return self._decode(row)
        rows = self.conn.execute('SELECT * FROM packages WHERE name=? ORDER BY id', (key,)).fetchall()
        if len(rows) == 1:
            return self._decode(rows[0])
        if len(rows) > 1:
            raise AmbiguousPackageError(key, [r['id'] for r in rows])
        return None

    def _upsert_package_no_commit(self, pkg: Dict[str, Any], aliases: List[str] | None = None) -> None:
        self.conn.execute(
            '''INSERT INTO packages(id,name,source_json,tracking_json,artifact_hash,effective_hash,overlay_hash,pinned,targets_json,trust,risk,updated_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
                 name=excluded.name, source_json=excluded.source_json, tracking_json=excluded.tracking_json,
                 artifact_hash=excluded.artifact_hash, effective_hash=excluded.effective_hash,
                 overlay_hash=excluded.overlay_hash, pinned=excluded.pinned, targets_json=excluded.targets_json,
                 trust=excluded.trust, risk=excluded.risk, updated_at=excluded.updated_at''',
            (
                pkg['id'], pkg['name'], json.dumps(pkg['source'], sort_keys=True), json.dumps(pkg['tracking'], sort_keys=True),
                pkg['artifact_hash'], pkg['effective_hash'], pkg.get('overlay_hash'), int(bool(pkg.get('pinned'))),
                json.dumps(sorted(set(pkg.get('targets', []))), sort_keys=True), pkg.get('trust', 'UNVERIFIED'), pkg.get('risk', 'MEDIUM'), now_iso()
            )
        )
        for alias_value in aliases or []:
            self.conn.execute('INSERT OR REPLACE INTO aliases(alias, package_id) VALUES(?,?)', (alias_value, pkg['id']))

    def upsert_package(self, pkg: Dict[str, Any], aliases: List[str] | None = None, *, write_lock: bool = True) -> None:
        self._upsert_package_no_commit(pkg, aliases)
        self.conn.commit()
        if write_lock:
            self.write_lock()

    def upsert_packages(self, entries: Sequence[Tuple[Dict[str, Any], List[str] | None]]) -> None:
        try:
            self.conn.execute('BEGIN IMMEDIATE')
            for pkg, aliases in entries:
                self._upsert_package_no_commit(pkg, aliases)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        self.write_lock()

    def add_history(self, pkg: Dict[str, Any]) -> None:
        self.conn.execute(
            'INSERT INTO history(package_id,artifact_hash,effective_hash,overlay_hash,source_json,tracking_json,created_at) VALUES(?,?,?,?,?,?,?)',
            (pkg['id'], pkg['artifact_hash'], pkg['effective_hash'], pkg.get('overlay_hash'), json.dumps(pkg['source'], sort_keys=True), json.dumps(pkg['tracking'], sort_keys=True), now_iso())
        )
        self.conn.commit()

    def history(self, package_id: str) -> List[Dict[str, Any]]:
        rows = self.conn.execute('SELECT * FROM history WHERE package_id=? ORDER BY id DESC', (package_id,)).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item['source'] = json.loads(item.pop('source_json'))
            item['tracking'] = json.loads(item.pop('tracking_json'))
            result.append(item)
        return result

    def create_transaction(self, txid: str, tx_type: str, plan: Dict[str, Any]) -> None:
        stamp = now_iso()
        self.conn.execute(
            'INSERT INTO transactions(id,type,state,plan_json,created_at,updated_at) VALUES(?,?,?,?,?,?)',
            (txid, tx_type, 'PLANNED', json.dumps(plan, sort_keys=True), stamp, stamp)
        )
        self.conn.commit()

    def get_transaction(self, txid: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute('SELECT * FROM transactions WHERE id=?', (txid,)).fetchone()
        return self._decode(row) if row else None

    def claim_transaction(self, txid: str) -> Dict[str, Any]:
        try:
            self.conn.execute('BEGIN IMMEDIATE')
            cur = self.conn.execute(
                "UPDATE transactions SET state='APPLYING', updated_at=? WHERE id=? AND state='PLANNED'",
                (now_iso(), txid),
            )
            if cur.rowcount != 1:
                row = self.conn.execute('SELECT * FROM transactions WHERE id=?', (txid,)).fetchone()
                self.conn.rollback()
                if row is None:
                    raise KeyError(txid)
                decoded = self._decode(row)
                raise RuntimeError(decoded['state'])
            row = self.conn.execute('SELECT * FROM transactions WHERE id=?', (txid,)).fetchone()
            self.conn.commit()
            return self._decode(row)
        except Exception:
            if self.conn.in_transaction:
                self.conn.rollback()
            raise

    def set_transaction_state(self, txid: str, state: str, plan: Dict[str, Any] | None = None) -> None:
        if plan is None:
            self.conn.execute('UPDATE transactions SET state=?, updated_at=? WHERE id=?', (state, now_iso(), txid))
        else:
            self.conn.execute('UPDATE transactions SET state=?, plan_json=?, updated_at=? WHERE id=?', (state, json.dumps(plan, sort_keys=True), now_iso(), txid))
        self.conn.commit()

    def incomplete_transactions(self) -> List[Dict[str, Any]]:
        rows = self.conn.execute("SELECT * FROM transactions WHERE state IN ('STAGED','APPROVED','APPLYING','FAILED','CONFLICT') ORDER BY created_at").fetchall()
        return [self._decode(r) for r in rows]

    def write_lock(self) -> None:
        lock = {'format': 1, 'packages': []}
        for pkg in self.list_packages():
            lock['packages'].append({
                'id': pkg['id'], 'name': pkg['name'], 'source': pkg['source'], 'tracking': pkg['tracking'],
                'artifact_hash': pkg['artifact_hash'], 'effective_hash': pkg['effective_hash'],
                'overlay_hash': pkg.get('overlay_hash'), 'pinned': pkg['pinned'], 'targets': pkg['targets']
            })
        write_json(self.lock_path, lock)
