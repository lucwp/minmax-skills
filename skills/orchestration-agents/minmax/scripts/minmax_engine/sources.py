from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .common import ensure_dir, normalize_path_text
from .inspector import find_skill_roots

SEMVER_RE = re.compile(r'^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:\+[0-9A-Za-z.-]+)?$')

MAX_DOWNLOAD_BYTES = 64 * 1024 * 1024
MAX_ARCHIVE_FILES = 10_000
MAX_EXTRACTED_BYTES = 64 * 1024 * 1024
MAX_SINGLE_FILE_BYTES = 32 * 1024 * 1024
MAX_COMPRESSION_RATIO = 200


class SourceError(RuntimeError):
    pass


class MultiplePackagesError(SourceError):
    def __init__(self, roots: List[str]):
        super().__init__('source contains multiple installable skill roots')
        self.roots = roots


@dataclass
class MaterializedSource:
    package_root: Path
    source: Dict[str, Any]
    tracking: Dict[str, Any]
    aliases: List[str]
    cleanup_root: Optional[Path] = None

    def cleanup(self) -> None:
        if self.cleanup_root and self.cleanup_root.exists():
            shutil.rmtree(self.cleanup_root, ignore_errors=True)


def _run_git(args: List[str], cwd: Path | None = None) -> str:
    try:
        result = subprocess.run(['git', *args], cwd=str(cwd) if cwd else None, check=True, capture_output=True, text=True, timeout=30)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
        detail = getattr(exc, 'stderr', '') or str(exc)
        raise SourceError(f'git operation failed: {detail.strip()}') from exc
    return result.stdout


def _semver_key(tag: str) -> Optional[Tuple[int, int, int]]:
    m = SEMVER_RE.match(tag)
    return tuple(map(int, m.groups())) if m else None


def _git_default_branch(repo_url: str) -> str:
    out = _run_git(['ls-remote', '--symref', repo_url, 'HEAD'])
    for line in out.splitlines():
        if line.startswith('ref:') and line.endswith('\tHEAD'):
            ref = line.split()[1]
            if ref.startswith('refs/heads/'):
                return ref[len('refs/heads/'):]
    return 'main'


def _git_tags(repo_url: str) -> List[str]:
    out = _run_git(['ls-remote', '--tags', '--refs', repo_url])
    tags = []
    for line in out.splitlines():
        if '\trefs/tags/' in line:
            tags.append(line.split('\trefs/tags/', 1)[1])
    return tags


def _choose_ref(repo_url: str, branch: str | None, explicit_ref: str | None) -> Dict[str, Any]:
    if branch:
        return {'mode': 'branch', 'ref': branch, 'resolved_type': 'branch', 'resolved_ref': branch}
    if explicit_ref:
        return {'mode': 'explicit', 'ref': explicit_ref, 'resolved_type': 'ref', 'resolved_ref': explicit_ref}
    tags = _git_tags(repo_url)
    semver = [(key, tag) for tag in tags if (key := _semver_key(tag)) is not None]
    if semver:
        tag = sorted(semver)[-1][1]
        return {'mode': 'stable', 'ref': None, 'resolved_type': 'release', 'resolved_ref': tag}
    default = _git_default_branch(repo_url)
    return {'mode': 'stable', 'ref': None, 'resolved_type': 'default_branch', 'resolved_ref': default}


def _clone(repo_url: str, ref: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix='minmax-git-'))
    dst = tmp / 'repo'
    try:
        try:
            _run_git(['clone', '--depth', '1', '--branch', ref, '--single-branch', repo_url, str(dst)])
        except SourceError:
            # Commit SHAs are not valid --branch values. Fall back to an exact shallow fetch.
            if dst.exists():
                shutil.rmtree(dst, ignore_errors=True)
            _run_git(['init', str(dst)])
            _run_git(['remote', 'add', 'origin', repo_url], cwd=dst)
            _run_git(['fetch', '--depth', '1', 'origin', ref], cwd=dst)
            _run_git(['checkout', '--detach', 'FETCH_HEAD'], cwd=dst)
    except SourceError:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return tmp


def _git_ref_commit(repo_url: str, ref: str) -> str:
    out = _run_git(['ls-remote', repo_url, ref, f'{ref}^{{}}'])
    rows = [line.split('\t', 1) for line in out.splitlines() if '\t' in line]
    for commit, name in rows:
        if name.endswith('^{}'):
            return commit
    if rows:
        return rows[0][0]
    # Branch/tag shorthand may need a fully-qualified query.
    out = _run_git(['ls-remote', repo_url, f'refs/heads/{ref}', f'refs/tags/{ref}', f'refs/tags/{ref}^{{}}'])
    rows = [line.split('\t', 1) for line in out.splitlines() if '\t' in line]
    for commit, name in rows:
        if name.endswith('^{}'):
            return commit
    if rows:
        return rows[0][0]
    raise SourceError(f'could not resolve git ref: {ref}')


def _git_commit(repo: Path) -> str:
    return _run_git(['rev-parse', 'HEAD'], cwd=repo).strip()


def _github_parts(url: str) -> Optional[Dict[str, str]]:
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname not in {'github.com', 'www.github.com'}:
        return None
    parts = [p for p in parsed.path.split('/') if p]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    if repo.endswith('.git'):
        repo = repo[:-4]
    ref = ''
    package_path = ''
    if len(parts) >= 4 and parts[2] in {'tree', 'blob'}:
        ref = urllib.parse.unquote(parts[3])
        package_path = '/'.join(urllib.parse.unquote(p) for p in parts[4:])
        if parts[2] == 'blob' and package_path.lower().endswith('/skill.md'):
            package_path = package_path.rsplit('/', 1)[0]
        elif parts[2] == 'blob' and package_path.lower() == 'skill.md':
            package_path = ''
    return {'owner': owner, 'repo': repo, 'ref': ref, 'package_path': package_path}


def _gitlab_parts(url: str) -> Optional[Dict[str, str]]:
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname not in {'gitlab.com', 'www.gitlab.com'}:
        return None
    parts = [p for p in parsed.path.split('/') if p]
    if len(parts) < 2:
        return None
    marker = parts.index('-') if '-' in parts else -1
    if marker >= 2:
        repo_parts = parts[:marker]
        tail = parts[marker + 1:]
    else:
        repo_parts = parts
        tail = []
    repo = repo_parts[-1]
    if repo.endswith('.git'):
        repo = repo[:-4]
    namespace = '/'.join(repo_parts[:-1])
    ref = ''
    package_path = ''
    if len(tail) >= 2 and tail[0] in {'tree', 'blob'}:
        ref = urllib.parse.unquote(tail[1])
        package_path = '/'.join(urllib.parse.unquote(p) for p in tail[2:])
        if tail[0] == 'blob' and package_path.lower().endswith('/skill.md'):
            package_path = package_path.rsplit('/', 1)[0]
        elif tail[0] == 'blob' and package_path.lower() == 'skill.md':
            package_path = ''
    return {'namespace': namespace, 'repo': repo, 'ref': ref, 'package_path': package_path}


def _github_repo_id(owner: str, repo: str) -> str:
    request = urllib.request.Request(
        f'https://api.github.com/repos/{owner}/{repo}',
        headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'minmax-package-manager'}
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode('utf-8'))
            if isinstance(payload.get('id'), int):
                return f'github:{payload["id"]}'
    except Exception:
        pass
    return f'github:{owner.lower()}/{repo.lower()}'


def _check_archive_budget(file_count: int, total_bytes: int, archive_bytes: int) -> None:
    if file_count > MAX_ARCHIVE_FILES:
        raise SourceError(f'archive contains too many entries: {file_count}')
    if total_bytes > MAX_EXTRACTED_BYTES:
        raise SourceError(f'archive expands beyond limit: {total_bytes} bytes')
    if archive_bytes > 0 and total_bytes / archive_bytes > MAX_COMPRESSION_RATIO:
        raise SourceError('archive compression ratio exceeds safety limit')


def _safe_extract_zip(archive: Path, dst: Path) -> None:
    archive_bytes = archive.stat().st_size
    with zipfile.ZipFile(archive) as zf:
        members = zf.infolist()
        total = sum(m.file_size for m in members if not m.is_dir())
        _check_archive_budget(len(members), total, archive_bytes)
        for member in members:
            if member.flag_bits & 0x1:
                raise SourceError(f'encrypted archive entries are not allowed: {member.filename}')
            mode = (member.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise SourceError(f'archive symlinks are not allowed: {member.filename}')
            if member.file_size > MAX_SINGLE_FILE_BYTES:
                raise SourceError(f'archive entry exceeds size limit: {member.filename}')
            target = (dst / member.filename).resolve()
            try:
                target.relative_to(dst.resolve())
            except ValueError as exc:
                raise SourceError(f'unsafe archive path: {member.filename}') from exc
            if member.is_dir():
                ensure_dir(target)
                continue
            ensure_dir(target.parent)
            with zf.open(member, 'r') as src, target.open('wb') as out:
                shutil.copyfileobj(src, out, length=1024 * 1024)


def _safe_extract_tar(archive: Path, dst: Path) -> None:
    archive_bytes = archive.stat().st_size
    with tarfile.open(archive, 'r:*') as tf:
        members = tf.getmembers()
        total = sum(m.size for m in members if m.isfile())
        _check_archive_budget(len(members), total, archive_bytes)
        for member in members:
            target = (dst / member.name).resolve()
            try:
                target.relative_to(dst.resolve())
            except ValueError as exc:
                raise SourceError(f'unsafe archive path: {member.name}') from exc
            if member.isdir():
                ensure_dir(target)
                continue
            if not member.isfile():
                raise SourceError(f'archive special files are not allowed: {member.name}')
            if member.size > MAX_SINGLE_FILE_BYTES:
                raise SourceError(f'archive entry exceeds size limit: {member.name}')
            ensure_dir(target.parent)
            src = tf.extractfile(member)
            if src is None:
                raise SourceError(f'could not read archive entry: {member.name}')
            with src, target.open('wb') as out:
                shutil.copyfileobj(src, out, length=1024 * 1024)


def _download(url: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix='minmax-http-'))
    parsed = urllib.parse.urlparse(url)
    name = Path(parsed.path).name or 'download'
    dst = tmp / name
    request = urllib.request.Request(url, headers={'User-Agent': 'minmax-package-manager'})
    try:
        with urllib.request.urlopen(request, timeout=60) as response, dst.open('wb') as handle:
            length = response.headers.get('Content-Length')
            if length and int(length) > MAX_DOWNLOAD_BYTES:
                raise SourceError('download exceeds safety limit')
            total = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_DOWNLOAD_BYTES:
                    raise SourceError('download exceeds safety limit')
                handle.write(chunk)
    except SourceError:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    except Exception as exc:
        shutil.rmtree(tmp, ignore_errors=True)
        raise SourceError(f'download failed: {exc}') from exc
    return dst


def _archive_to_dir(archive: Path) -> Tuple[Path, Path]:
    if archive.stat().st_size > MAX_DOWNLOAD_BYTES:
        raise SourceError('archive exceeds compressed size limit')
    tmp = Path(tempfile.mkdtemp(prefix='minmax-archive-'))
    dst = ensure_dir(tmp / 'unpacked')
    try:
        if zipfile.is_zipfile(archive):
            _safe_extract_zip(archive, dst)
        elif tarfile.is_tarfile(archive):
            _safe_extract_tar(archive, dst)
        else:
            raise SourceError('unsupported archive format')
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    children = [p for p in dst.iterdir() if p.name != '__MACOSX']
    root = children[0] if len(children) == 1 and children[0].is_dir() else dst
    return tmp, root

def _select_package_root(root: Path, package_path: str | None) -> Tuple[Path, str]:
    if package_path:
        candidate = (root / package_path).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError as exc:
            raise SourceError('package path escapes source root') from exc
        if not candidate.is_dir():
            raise SourceError(f'package path not found: {package_path}')
        if not ((candidate / 'SKILL.md').is_file() or (candidate / 'skill.md').is_file()):
            roots = find_skill_roots(candidate)
            if len(roots) == 1:
                candidate = candidate / roots[0]
            else:
                raise SourceError(f'no skill entrypoint at package path: {package_path}')
        return candidate, package_path.strip('/') or '.'
    if (root / 'SKILL.md').is_file() or (root / 'skill.md').is_file():
        return root, '.'
    roots = find_skill_roots(root)
    if len(roots) == 1:
        return root / roots[0], roots[0]
    if not roots:
        raise SourceError('no SKILL.md or skill.md found in source')
    raise MultiplePackagesError(roots)


class SourceResolver:
    def __init__(self) -> None:
        self._probe_cache: Dict[Tuple[str, str | None, str | None], Dict[str, Any] | None] = {}

    def probe(self, source_ref: str, package_path: str | None = None, branch: str | None = None, explicit_ref: str | None = None) -> Dict[str, Any] | None:
        """Resolve remote git identity without cloning package contents.

        Returns None for sources that cannot be checked cheaply (local paths and generic archives).
        """
        source_ref = source_ref.strip()
        cache_key = (source_ref, branch, explicit_ref)
        if cache_key in self._probe_cache:
            cached = self._probe_cache[cache_key]
            return dict(cached) if isinstance(cached, dict) else None
        local_text = source_ref[7:] if source_ref.startswith('file://') else source_ref
        if Path(os.path.expanduser(local_text)).exists():
            self._probe_cache[cache_key] = None
            return None

        if 'skillsmp.com/' in source_ref:
            request = urllib.request.Request(source_ref, headers={'User-Agent': 'minmax-package-manager'})
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    body = html.unescape(response.read().decode('utf-8', errors='replace'))
            except Exception as exc:
                raise SourceError(f'could not read SkillsMP listing: {exc}') from exc
            matches = re.findall(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/(?:tree|blob)/[^\s"\'<>]+)?', body)
            if not matches:
                raise SourceError('SkillsMP listing did not expose a canonical GitHub source')
            result = self.probe(matches[0].rstrip(').,;'), package_path=package_path, branch=branch, explicit_ref=explicit_ref)
            if result is not None:
                result['discovered_via'] = 'skillsmp'
                self._probe_cache[cache_key] = dict(result)
                return dict(result)
            self._probe_cache[cache_key] = None
            return None

        github = _github_parts(source_ref)
        if github:
            repo_url = f"https://github.com/{github['owner']}/{github['repo']}.git"
            ref_info = _choose_ref(repo_url, branch, explicit_ref or github['ref'] or None)
            commit = _git_ref_commit(repo_url, ref_info['resolved_ref'])
            ref_info['resolved_commit'] = commit
            result = {'provider': 'github', 'commit': commit, 'tracking': ref_info}
            self._probe_cache[cache_key] = result
            return dict(result)

        gitlab = _gitlab_parts(source_ref)
        if gitlab:
            repo_url = f"https://gitlab.com/{gitlab['namespace']}/{gitlab['repo']}.git"
            ref_info = _choose_ref(repo_url, branch, explicit_ref or gitlab['ref'] or None)
            commit = _git_ref_commit(repo_url, ref_info['resolved_ref'])
            ref_info['resolved_commit'] = commit
            result = {'provider': 'gitlab', 'commit': commit, 'tracking': ref_info}
            self._probe_cache[cache_key] = result
            return dict(result)

        if source_ref.startswith('git+') or source_ref.endswith('.git') or source_ref.startswith('ssh://'):
            repo_url = source_ref[4:] if source_ref.startswith('git+') else source_ref
            ref_info = _choose_ref(repo_url, branch, explicit_ref)
            commit = _git_ref_commit(repo_url, ref_info['resolved_ref'])
            ref_info['resolved_commit'] = commit
            result = {'provider': 'git', 'commit': commit, 'tracking': ref_info}
            self._probe_cache[cache_key] = result
            return dict(result)
        self._probe_cache[cache_key] = None
        return None

    def materialize(self, source_ref: str, package_path: str | None = None, branch: str | None = None, explicit_ref: str | None = None) -> MaterializedSource:
        source_ref = source_ref.strip()
        aliases = [source_ref]

        local_text = source_ref[7:] if source_ref.startswith('file://') else source_ref
        local = Path(os.path.expanduser(local_text))
        if local.exists():
            if local.is_dir():
                package_root, normalized_path = _select_package_root(local.resolve(), package_path)
                source = {'provider': 'local', 'canonical_url': normalize_path_text(local), 'stable_id': 'local:' + normalize_path_text(local), 'package_path': normalized_path}
                tracking = {'mode': 'local', 'ref': None, 'resolved_type': 'content', 'resolved_ref': None}
                return MaterializedSource(package_root, source, tracking, aliases)
            if local.is_file():
                tmp, root = _archive_to_dir(local)
                package_root, normalized_path = _select_package_root(root, package_path)
                source = {'provider': 'archive', 'canonical_url': normalize_path_text(local), 'stable_id': 'file:' + normalize_path_text(local), 'package_path': normalized_path}
                tracking = {'mode': 'content', 'ref': None, 'resolved_type': 'content', 'resolved_ref': None}
                return MaterializedSource(package_root, source, tracking, aliases, tmp)

        if 'skillsmp.com/' in source_ref:
            request = urllib.request.Request(source_ref, headers={'User-Agent': 'minmax-package-manager'})
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    body = html.unescape(response.read().decode('utf-8', errors='replace'))
            except Exception as exc:
                raise SourceError(f'could not read SkillsMP listing: {exc}') from exc
            matches = re.findall(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/(?:tree|blob)/[^\s"\'<>]+)?', body)
            if not matches:
                raise SourceError('SkillsMP listing did not expose a canonical GitHub source')
            nested = self.materialize(matches[0].rstrip(').,;'), package_path=package_path, branch=branch, explicit_ref=explicit_ref)
            nested.aliases = list(dict.fromkeys([source_ref, *nested.aliases]))
            nested.source['discovered_via'] = 'skillsmp'
            return nested

        github = _github_parts(source_ref)
        if github:
            owner, repo = github['owner'], github['repo']
            repo_url = f'https://github.com/{owner}/{repo}.git'
            url_ref = github['ref'] or None
            path_from_url = github['package_path'] or None
            ref_info = _choose_ref(repo_url, branch, explicit_ref or url_ref)
            tmp = _clone(repo_url, ref_info['resolved_ref'])
            repo_root = tmp / 'repo'
            package_root, normalized_path = _select_package_root(repo_root, package_path or path_from_url)
            commit = _git_commit(repo_root)
            stable = _github_repo_id(owner, repo)
            source = {
                'provider': 'github', 'canonical_url': f'https://github.com/{owner}/{repo}', 'stable_id': stable,
                'repository': f'{owner}/{repo}', 'package_path': normalized_path, 'commit': commit
            }
            ref_info['resolved_commit'] = commit
            return MaterializedSource(package_root, source, ref_info, aliases, tmp)

        gitlab = _gitlab_parts(source_ref)
        if gitlab:
            namespace, repo = gitlab['namespace'], gitlab['repo']
            repo_url = f'https://gitlab.com/{namespace}/{repo}.git'
            url_ref = gitlab['ref'] or None
            path_from_url = gitlab['package_path'] or None
            ref_info = _choose_ref(repo_url, branch, explicit_ref or url_ref)
            tmp = _clone(repo_url, ref_info['resolved_ref'])
            repo_root = tmp / 'repo'
            package_root, normalized_path = _select_package_root(repo_root, package_path or path_from_url)
            commit = _git_commit(repo_root)
            stable = f'gitlab:{namespace.lower()}/{repo.lower()}'
            source = {
                'provider': 'gitlab', 'canonical_url': f'https://gitlab.com/{namespace}/{repo}', 'stable_id': stable,
                'repository': f'{namespace}/{repo}', 'package_path': normalized_path, 'commit': commit
            }
            ref_info['resolved_commit'] = commit
            return MaterializedSource(package_root, source, ref_info, aliases, tmp)

        if source_ref.startswith('git+') or source_ref.endswith('.git') or source_ref.startswith('ssh://'):
            repo_url = source_ref[4:] if source_ref.startswith('git+') else source_ref
            ref_info = _choose_ref(repo_url, branch, explicit_ref)
            tmp = _clone(repo_url, ref_info['resolved_ref'])
            repo_root = tmp / 'repo'
            package_root, normalized_path = _select_package_root(repo_root, package_path)
            commit = _git_commit(repo_root)
            stable = 'git:' + repo_url.lower().rstrip('/')
            source = {'provider': 'git', 'canonical_url': repo_url, 'stable_id': stable, 'package_path': normalized_path, 'commit': commit}
            ref_info['resolved_commit'] = commit
            return MaterializedSource(package_root, source, ref_info, aliases, tmp)

        if source_ref.startswith('http://') or source_ref.startswith('https://'):
            downloaded = _download(source_ref)
            parent = downloaded.parent
            try:
                tmp, root = _archive_to_dir(downloaded)
            except Exception:
                shutil.rmtree(parent, ignore_errors=True)
                raise
            shutil.rmtree(parent, ignore_errors=True)
            package_root, normalized_path = _select_package_root(root, package_path)
            source = {'provider': 'url', 'canonical_url': source_ref, 'stable_id': 'url:' + source_ref, 'package_path': normalized_path}
            tracking = {'mode': 'content', 'ref': None, 'resolved_type': 'content', 'resolved_ref': None}
            return MaterializedSource(package_root, source, tracking, aliases, tmp)

        raise SourceError(f'unsupported source: {source_ref}')
