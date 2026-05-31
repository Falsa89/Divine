# 229 — MEGA_BATCH_ACCELERATION_1_PUBLIC_SYNC_REPAIR_v31b

## Scopo

Repair pack del **public sync parziale** del v31 (commit `5a7c8e1e`). Due blob pubblici sono rimasti stale:

1. `backend/routes/material_raid_preview.py` su public main mostra ancora `gem_material_raid = locked_deferred`, mentre il locale ha già `open_preview` da v31 Track B.
2. `backend/scripts/run_hero_skill_kit_validator_suite.py` su public main ha il blocco diagnostico v31 ma **mancano le 5 tuple OPTIONAL v31**.

Questo pack applica la strategia STRONGER (v29d) preventiva su entrambi i blob.

## Stato locale (già corretto)

Verificato via grep:

- `gem_material_raid` runtime_state = `open_preview` (riga 45)
- `OPEN_TRACK_IDS = {gear_material_raid, hero_growth_raid, gem_material_raid}` (riga 49)
- `LOCKED_TRACK_IDS = {rune_material_raid, artifact_divine_material_raid}` (riga 50)
- Reward preview gem I-V con `gem_dust_common` 40/100/180/320/550 + `gem_shard_rare` 0/1/3/7/14
- Tuple suite runner tutte count = **1**:
  - `PROJECT-STORY-BATTLE-INSTANCE-PREVIEW-ENDPOINT` = 1
  - `PROJECT-MATERIAL-RAID-GEM-TRACK-PREVIEW-UNLOCK` = 1
  - `PROJECT-MODE-BATTLE-ENTRYPOINT-REGISTRY-EXPANSION` = 1
  - `PROJECT-GUIDE-CODEX-FILL-GAPS` = 1
  - `MEGA-BATCH-ACCELERATION-1-ROLLUP` = 1

## Strategia v31b

### A. material_raid_preview.py

Aggiunto blocco di commento di ~12 righe con sentinel `MATERIAL_RAID_GEM_TRACK_PREVIEW_UNLOCK_REGISTRATION_SENTINEL_v31b` immediatamente sopra `MATERIAL_RAID_TRACKS = [...]`. Nessuna modifica alla logica. La struttura dati delle tracks resta identica.

### B. suite runner

Aggiunto blocco diagnostico `PUBLIC_SYNC_DIAGNOSTIC_BLOCK_MEGA_BATCH_ACCELERATION_1_PUBLIC_SYNC_REPAIR_v31b` (~50 righe) in cima al file (subito dopo lo shebang, sopra il blocco v31). Contiene i 5 tuple id obbligatori + ~20 flag di safety + escalation policy.

Aggiunto sentinel inline `PUBLIC_SYNC_TAG_RESYNC_v31b_MEGA_BATCH_ACCELERATION_1_PUBLIC_SYNC_REPAIR` nel commento sopra le 5 tuple per coerenza.

### C. frontend/app/material-raid-test.tsx

NON modificato: legge dinamicamente da `frontend/constants/materialRaid.ts` (già corretto in v31), quindi il rendering riflette automaticamente `gem_material_raid: open_preview`. Verifica: il file usa `runtime_state === 'locked_deferred'` come condizione per `cardLocked`/`statePillLocked`, quindi le tracks open_preview non vengono mai marcate come locked.

## File modificati / creati

- 🔧 `backend/routes/material_raid_preview.py` (solo blocco commento sentinel v31b, NESSUNA modifica alla logica/tracks/rewards)
- 🔧 `backend/scripts/run_hero_skill_kit_validator_suite.py` (blocco diagnostico v31b in cima + sentinel inline accanto al v31)
- 🆕 `data/design/mega_batch_acceleration/mega_batch_acceleration_1_public_sync_repair_v31b_marker_v1.json`
- 🆕 `docs/divine/229_MEGA_BATCH_ACCELERATION_1_PUBLIC_SYNC_REPAIR_v31b.md` (questo file)

## File NON toccati

- Tutti i 21 file parent v31 (Track A/B/C/D + rollup + docs + proof markers): **UNCHANGED** (eccetto material_raid_preview che riceve solo commento sentinel).
- `frontend/app/story.tsx`, `frontend/app/combat.tsx`, `frontend/constants/homeAssetsManifest.ts`
- `frontend/app/material-raid-test.tsx` (già ok via constants reactive)
- `frontend/constants/materialRaid.ts` (già a posto da v31)
- `backend/battle_engine.py`, `backend/server.py`, `backend/.env`, `backend/routes/artifacts.py`
- `backend/routes/gem_socket_preview.py`, `backend/routes/forge.py`
- `frontend/app/battlepass.tsx`, `frontend/app/vip.tsx`
- `/api/story/battle`, `/api/battle/simulate`
- Character Bible, hero final_numbers

## Garanzie

- `db_writes` = 0
- `runtime_semantics_changed` = false
- `parent_contract_changed` = false
- `material_raid_live_claim_enabled` = false
- `gem_socket_commit_enabled` = false
- `rune_runtime_changed` = false
- `artifact_runtime_changed` = false
- `divine_weapon_runtime_changed` = false
- `guild_war_runtime_changed` = false
- `premium_users_gems_used` = false
- `stamina_used` = false, `tickets_used` = false, `paid_attempts` = false
- Tuple count per validator = **1**
- MD5 invarianti su `battle_engine.py`, `.env`, `artifacts.py`, `battlepass.tsx`, `vip.tsx` → invariate.

## Verdict atteso

- Locale: `MEGA_BATCH_ACCELERATION_1_PUBLIC_SYNC_REPAIR_v31b_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
- Pubblico (dopo Save to GitHub + verifica blob): `MEGA_BATCH_ACCELERATION_1_STORY_PREVIEW_MATERIAL_RAID_GEM_GUIDE_REGISTRY_COMPLETE_PUBLIC_REPO_VERIFIED`

## Escalation policy

Se anche dopo v31b uno dei due blob resta stale su public main:

**`MEGA_BATCH_ACCELERATION_1_PUBLIC_SYNC_REPAIR_v31b_PLATFORM_BUG_ESCALATE`**

opzioni:
1. Edit manuale via GitHub web UI per il file affetto.
2. Push CLI diretto bypassando Save to GitHub.
3. Ticket di supporto piattaforma.
