# 257 — MEGA_ECONOMY_SAFETY_ACCELERATION_5 v41 · Track D · Rollup

## Rollup del pack v41

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_5_OBSERVABILITY_SIGNOFF_AND_REQUEST_HASH_PACK_v41`  
**Track**: D (Rollup)  
**Modalità**: DESIGN_CONTRACT_AUDIT_ONLY  
**Runtime activation**: `false`  
**DB writes**: `0`

### Scopo

Validator rollup che esegue back-to-back i 3 validator di Track A/B/C e
asserisce le invarianti globali del pack v41:

- 5 file core MD5-locked invariati
- 4 tuple v41 nel suite runner (count = 1 ciascuna)
- Rollup marker presente e coerente
- Tutti i marker v37/v38/v39/v40 ancora presenti
- Registry v4 ancora presente con copertura 8/8 famiglie operation
- Nessun nuovo router FastAPI registrato in `server.py` (v41 è solo design)
- Sentinelle LOUD precedenti (v38c, v39b, v40) ancora presenti in `server.py`

### File creati / coinvolti

- **Validator rollup**: `backend/scripts/validate_mega_economy_safety_acceleration_5_v41_rollup.py`
- **Rollup marker**: `data/design/economy_safety/mega_economy_safety_acceleration_5_v41_rollup_marker_v1.json`
- **Doc**: questo file `docs/divine/257_*.md`
- **Suite runner**: aggiornato con 4 tuple `OPTIONAL` `count=1` ciascuna
  - `PROJECT-SHARED-REQUEST-HASH-IDEMPOTENCY-CONTRACT`
  - `PROJECT-ECONOMY-SAFETY-OBSERVABILITY-FOUNDATION`
  - `PROJECT-ECONOMY-SAFETY-PRE-SIGNOFF-ROLLBACK-BUNDLE`
  - `MEGA-ECONOMY-SAFETY-ACCELERATION-5-v41-ROLLUP`

### Conferme cross-pack

- v37 (Gem Socket + Material Raid)        → preview ancora attivo, ancora isolato
- v38 (Gear Forge + Rune/Scroll/Talisman) → preview ancora attivo, ancora isolato
- v39 (Artifact + Divine Weapon)           → preview ancora attivo, ancora isolato
- v40 (Battle Pass + Mail Claim)           → preview ancora attivo, ancora isolato

Copertura **8/8** famiglie operation preservata.

### Verdict atteso locale

```
MEGA_ECONOMY_SAFETY_ACCELERATION_5_OBSERVABILITY_SIGNOFF_AND_REQUEST_HASH_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

### Caveat noti

- `SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION` accettata.
- 18 OPTIONAL fails attesi nella suite master (6 Redis assenti + 12 legacy
  MD5 assertions). Nessun REQUIRED fail.
