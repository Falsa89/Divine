# 282 — AUDIT_BUNDLE_CHECKSUM_DRY_RUN (v48 Track A)

## Sintesi
Utility deterministica che calcola un checksum SHA-256 consolidato del bundle
audit dei pack v37-v48 (markers, contracts, validators, routes, utils, docs).

## Garanzie strict
- Read-only filesystem access; NO file writes
- NO DB / Redis / persistent ledger
- `db_writes=0`, `persisted=false`, `live_apply_allowed=false`
- `read_only=true`, `alert_dispatched=false`, `external_sink_used=false`

## Algoritmo
- Path collection: sort lexicografico
- Line endings normalization: CRLF → LF
- Hashing: per-file SHA-256, poi rolling SHA-256 su `path\0sha256\n`
- Output: `{checksum_sha256, file_count, included_files, missing_files, ...}`

## API pubblica
- `build_audit_bundle_checksum()` -> dict
- `build_config_block()` -> dict
- `_test_reset()` -> None
