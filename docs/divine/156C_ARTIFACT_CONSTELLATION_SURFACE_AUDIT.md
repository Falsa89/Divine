# 156C — Artifact / Constellation Live Surface Audit (Track C)

Verdetto: `TRACK_C_ARTIFACT_CONSTELLATION_LIVE_SURFACE_AUDIT_READY_NOT_APPLIED`

## Surfaces rilevate
- `/artifacts-preview` — safe, locked/read-only ✅
- `/artifacts` — **LIVE**, espone pull/pull10/fuse + constellations pull/equip ⚠️
- Menu entry "Artefatti & Costellazioni" → `/artifacts` (live) ⚠️
- Banner gacha `artifact` e `constellation` presenti su `/gacha`

## Raccomandazione
Lock/redirect di `/artifacts` verso `/artifacts-preview` in pack dedicato `PROJECT_ARTIFACT_CONSTELLATION_SURFACE_LOCK_PACK` (priorità P1).
Nascondere/disabilitare banner artifact/constellation finché il gate artifact live non è firmato.

## Vincoli rispettati
- Nessuna mutazione DB, nessun cambio backend, nessun flag flip.
