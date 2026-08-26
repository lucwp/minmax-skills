from __future__ import annotations

import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .common import read_skill_name, tree_hash, tree_manifest

URL_RE = re.compile(r'https?://[^\s)\]} >"\']+'.replace(' ', ''))


def _read_text(path: Path, limit: int = 200_000) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')[:limit]
    except OSError:
        return ''


def _entrypoint(root: Path) -> Path | None:
    for name in ('SKILL.md', 'skill.md'):
        path = root / name
        if path.is_file():
            return path
    return None


def _frontmatter(text: str) -> Dict[str, str]:
    if not text.startswith('---'):
        return {}
    end = text.find('\n---', 3)
    if end < 0:
        return {}
    result: Dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip().lower()
        if key in {'name', 'description', 'publisher', 'author', 'repository', 'source', 'homepage'}:
            result[key] = value.strip().strip('"\'')
    return result


def fingerprint(root: Path) -> Dict[str, Any]:
    root = root.resolve()
    entry = _entrypoint(root)
    text = _read_text(entry) if entry else ''
    meta = _frontmatter(text)
    manifest = tree_manifest(root)
    urls = sorted(set(URL_RE.findall(text)))
    for extra in ('README.md', 'readme.md', 'agents/openai.yaml', 'minmax.toml'):
        path = root / extra
        if path.is_file():
            urls.extend(URL_RE.findall(_read_text(path, 50_000)))
    urls = sorted(set(urls))
    return {
        'name': meta.get('name') or read_skill_name(root),
        'description': meta.get('description', ''),
        'publisher': meta.get('publisher') or meta.get('author') or '',
        'declared_repository': meta.get('repository') or meta.get('source') or meta.get('homepage') or '',
        'urls': urls,
        'entrypoint_text': text,
        'manifest': manifest,
        'tree_hash': tree_hash(root),
        'top_level': sorted(p.name for p in root.iterdir()),
    }


def search_queries(local: Dict[str, Any]) -> List[str]:
    queries: List[str] = []
    name = local.get('name', '').strip()
    description = local.get('description', '').strip()
    publisher = local.get('publisher', '').strip()
    if name:
        queries.extend([
            f'"{name}" "SKILL.md"',
            f'"{name}" AI skill GitHub',
            f'"{name}" SkillsMP',
            f'"{name}" GitLab skill',
        ])
    if name and publisher:
        queries.append(f'"{name}" "{publisher}"')
    if description:
        phrase = ' '.join(description.split()[:14])
        if len(phrase) >= 18:
            queries.append(f'"{phrase}"')
    for url in local.get('urls', []):
        if any(host in url for host in ('github.com/', 'gitlab.com/', 'skillsmp.com/')):
            queries.insert(0, url)
    return list(dict.fromkeys(q for q in queries if q))[:10]


def _ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b, autojunk=False).ratio()


def _jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _normalize_url(value: str) -> str:
    value = value.strip().rstrip('/').lower()
    return value[:-4] if value.endswith('.git') else value


def score_candidate(local: Dict[str, Any], candidate: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """Score package similarity and source provenance separately.

    Exact bytes prove artifact equivalence, not source identity. Automatic source
    confirmation requires provenance evidence embedded in the installed package.
    """
    evidence: List[Dict[str, Any]] = []
    strong: List[str] = []
    similarity = 0.0

    exact_hash = bool(local.get('tree_hash') and local['tree_hash'] == candidate.get('tree_hash'))
    if exact_hash:
        artifact_equivalence = 'EXACT'
        similarity = 1.0
        evidence.append({'signal': 'exact_tree_hash', 'scope': 'artifact', 'weight': 1.0})
    else:
        artifact_equivalence = 'SIMILAR'
        if local.get('name') and local['name'].lower() == candidate.get('name', '').lower():
            similarity += 0.10
            evidence.append({'signal': 'name_match', 'scope': 'similarity', 'weight': 0.10})

        description_similarity = _ratio(local.get('description', ''), candidate.get('description', ''))
        if description_similarity:
            weight = 0.15 * description_similarity
            similarity += weight
            evidence.append({'signal': 'description_similarity', 'scope': 'similarity', 'value': round(description_similarity, 3), 'weight': round(weight, 3)})

        entry_similarity = _ratio(local.get('entrypoint_text', ''), candidate.get('entrypoint_text', ''))
        if entry_similarity:
            weight = 0.30 * entry_similarity
            similarity += weight
            evidence.append({'signal': 'skill_content_similarity', 'scope': 'similarity', 'value': round(entry_similarity, 3), 'weight': round(weight, 3)})

        local_manifest = local.get('manifest', {})
        candidate_manifest = candidate.get('manifest', {})
        structure = _jaccard(local_manifest.keys(), candidate_manifest.keys())
        weight = 0.15 * structure
        similarity += weight
        evidence.append({'signal': 'structure_similarity', 'scope': 'similarity', 'value': round(structure, 3), 'weight': round(weight, 3)})

        local_hashes = set(local_manifest.values())
        candidate_hashes = set(candidate_manifest.values())
        hash_overlap = _jaccard(local_hashes, candidate_hashes)
        weight = 0.20 * hash_overlap
        similarity += weight
        evidence.append({'signal': 'file_hash_overlap', 'scope': 'artifact', 'value': round(hash_overlap, 3), 'weight': round(weight, 3)})
        if hash_overlap < 0.20:
            artifact_equivalence = 'DIFFERENT'

    canonical = _normalize_url(source.get('canonical_url', ''))
    declared = _normalize_url(local.get('declared_repository', ''))
    urls = {_normalize_url(u) for u in local.get('urls', [])}
    provenance_score = 0.0
    if canonical and (canonical == declared or canonical in urls):
        provenance_score = 1.0
        strong.append('embedded_source_match')
        evidence.append({'signal': 'embedded_source_match', 'scope': 'provenance', 'weight': 1.0})

    publisher = local.get('publisher', '').strip().lower()
    repository = source.get('repository', '').lower()
    publisher_match = bool(publisher and publisher in repository)
    if publisher_match:
        evidence.append({'signal': 'publisher_match', 'scope': 'hint', 'weight': 0.10})

    similarity = min(1.0, similarity)
    if provenance_score >= 1.0:
        status = 'CONFIRMED'
        confidence = 1.0
    elif exact_hash:
        status = 'PLAUSIBLE'
        confidence = 0.85
        strong.append('exact_artifact_equivalence_only')
    elif similarity >= 0.75:
        status = 'PLAUSIBLE'
        confidence = min(0.80, 0.45 + similarity * 0.35 + (0.05 if publisher_match else 0.0))
    else:
        status = 'REJECTED'
        confidence = min(0.49, similarity * 0.5 + (0.05 if publisher_match else 0.0))

    return {
        'status': status,
        'confidence': round(confidence, 3),
        'artifact_equivalence': artifact_equivalence,
        'similarity_score': round(similarity, 3),
        'provenance_score': round(provenance_score, 3),
        'strong_signals': sorted(set(strong)),
        'evidence': evidence,
        'source': source,
        'candidate': {
            'name': candidate.get('name'),
            'tree_hash': candidate.get('tree_hash'),
            'description': candidate.get('description', ''),
        },
    }


def resolution_summary(scored: List[Dict[str, Any]]) -> str:
    confirmed = [x for x in scored if x.get('status') == 'CONFIRMED']
    plausible = [x for x in scored if x.get('status') == 'PLAUSIBLE']
    if len(confirmed) == 1 and not plausible:
        return 'CONFIRMED'
    if len(confirmed) > 1 or len(plausible) > 1 or (confirmed and plausible):
        return 'AMBIGUOUS'
    if plausible:
        return 'PLAUSIBLE_REQUIRES_CONFIRMATION'
    return 'UNRESOLVED'
