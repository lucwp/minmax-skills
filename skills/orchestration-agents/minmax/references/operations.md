# MinMax Operations Reference

## Output modes

Default is compact:

```bash
python scripts/minmax.py --home ~/.minmax status
```

Use full JSON only for debugging/integration:

```bash
python scripts/minmax.py --home ~/.minmax --format json status
```

## Setup

```bash
python scripts/minmax.py --home ~/.minmax setup --scan
python scripts/minmax.py --home ~/.minmax setup --target codex=~/.codex/skills
python scripts/minmax.py --home ~/.minmax apply PLAN_ID
```

Setup adopts existing target skills by metadata/hash only. It never copies them into `~/.minmax`.

## Install directly to a runtime

```bash
python scripts/minmax.py --home ~/.minmax install SOURCE --target codex
python scripts/minmax.py --home ~/.minmax apply PLAN_ID
```

If `--target` is omitted, configured targets are used. The reviewed source is resolved again at apply time and must match the approved hash.

## ZIP fallback when direct installation is unavailable

```bash
python scripts/minmax.py --home ~/.minmax install SOURCE --output /path/to/skill.zip
python scripts/minmax.py --home ~/.minmax apply PLAN_ID
```

Result: package metadata is registered and the ZIP is produced, but the package remains `registered_only` until installed into a runtime target. Do not report it as installed.

## Scan/status

```bash
python scripts/minmax.py --home ~/.minmax scan
python scripts/minmax.py --home ~/.minmax status
python scripts/minmax.py --home ~/.minmax drift
```

## Check/update

```bash
python scripts/minmax.py --home ~/.minmax check
python scripts/minmax.py --home ~/.minmax update
python scripts/minmax.py --home ~/.minmax update PACKAGE
python scripts/minmax.py --home ~/.minmax apply PLAN_ID
```

Known Git packages use lightweight ref/commit probing first. Package content is cloned only when the remote identity changed or a content diff is required.

Global update does not automatically perform exhaustive web origin discovery for all unresolved packages. Resolve those selectively unless the user explicitly requests a deep/global resolution pass.

## Resolve a missing source

Find candidate origins externally, then score them:

```bash
python scripts/minmax.py --home ~/.minmax discover-source PACKAGE \
  --candidate SOURCE_A \
  --candidate SOURCE_B
```

After user resolution:

```bash
python scripts/minmax.py --home ~/.minmax link-source PACKAGE SOURCE
python scripts/minmax.py --home ~/.minmax apply PLAN_ID
```

## Pin / branch / rollback

```bash
python scripts/minmax.py --home ~/.minmax pin PACKAGE
python scripts/minmax.py --home ~/.minmax unpin PACKAGE
python scripts/minmax.py --home ~/.minmax track PACKAGE --branch BRANCH
python scripts/minmax.py --home ~/.minmax rollback PACKAGE --steps 1
```

Rollback reconstructs the historical source/ref and verifies its historical hash. It is intentionally not backed by a private MinMax copy of the old package.

## Overlays

```bash
python scripts/minmax.py --home ~/.minmax adopt-overlay PACKAGE --target codex
```

Only the user's delta is persisted. Full package contents remain source-backed.

## Target/cloud sync

```bash
python scripts/minmax.py --home ~/.minmax sync-targets
python scripts/minmax.py --home ~/.minmax cloud-config --path /synced/MinMax
python scripts/minmax.py --home ~/.minmax sync-cloud --direction push
python scripts/minmax.py --home ~/.minmax sync-cloud --direction pull
```

Cloud/state transfer stores registry metadata and overlay deltas, not package mirrors. A target sync re-resolves package sources.

## Exit codes

- `0`: success
- `2`: invalid selection / package not installed / source resolution needed
- `3`: stale plan, conflict, or blocked transaction
- `4`: integrity/security failure
- `5`: operational failure
