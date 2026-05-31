# 223 — PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v30b

## Scopo

Micro-pack di sync per risolvere lo stato stale del `backend/scripts/run_hero_skill_kit_validator_suite.py` su GitHub main dopo il push del parent pack `PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT_PACK` (commit `e441fc1e`).

Strategia: la stessa che ha funzionato per la catena v29/v29b/v29c/v29d, applicata già al primo tentativo (v30b) invece di iterare con piccoli commenti che hanno fallito sul v29.

## Contesto

La main pubblica contiene già correttamente gli 8 file del parent v30:

- `data/design/story_visual_battle/story_visual_battle_wiring_contract_v1.json`
- `data/design/story_visual_battle/story_battle_instance_payload_contract_v1.json`
- `data/design/story_visual_battle/story_reward_idempotency_contract_v1.json`
- `data/design/story_visual_battle/story_visual_battle_transition_plan_v1.json`
- `data/design/story_visual_battle/story_visual_battle_wiring_contract_proof_marker_v1.json`
- `data/design/battle_entrypoints/battle_entrypoint_registry_v3.json`
- `docs/divine/222_STORY_VISUAL_BATTLE_WIRING_CONTRACT.md`
- `backend/scripts/validate_project_story_visual_battle_wiring_contract_v1.py`

Ma il `backend/scripts/run_hero_skill_kit_validator_suite.py` pubblico NON contiene ancora:

- sentinel `PUBLIC_SYNC_TAG_v30_STORY_VISUAL_BATTLE_WIRING_CONTRACT`
- sentinel `STORY_VISUAL_BATTLE_WIRING_CONTRACT_REGISTRATION_SENTINEL`
- tupla `('PROJECT-STORY-VISUAL-BATTLE-WIRING-CONTRACT', 'validate_project_story_visual_battle_wiring_contract_v1.py')`

## Strategia v30b (stronger blob refresh, applicata subito)

### A. Blocco diagnostico in cima al file

Inserito immediatamente dopo lo shebang `#!/usr/bin/env python3`, prima del blocco diagnostico V29D: un blocco `PUBLIC_SYNC_DIAGNOSTIC_BLOCK_STORY_VISUAL_BATTLE_WIRING_CONTRACT_V30B` di ~50 righe con entrambi i sentinel `v30/v30b`, ID validator, file validator, REGISTRATION_SENTINEL, tuple_count atteso (1), tier atteso (OPTIONAL), phase (PHASE_1), mode (DESIGN_CONTRACT_AUDIT_ONLY), e ~15 flag di safety (db_writes=0, runtime_semantics_changed=false, story_tsx_changed=false, ...).

### B. Tupla già in cima al blocco OPTIONAL

La tupla `('PROJECT-STORY-VISUAL-BATTLE-WIRING-CONTRACT', '...v1.py')` era già stata inserita dal pack v30 parent come **seconda entry** dell'OPTIONAL list (subito dopo la tupla v29 rilocata in cima dal v29d). Non serve rilocazione ulteriore.

### C. Sentinel inline v30b aggiunto

Nel commento sopra la tupla v30 è stato aggiunto `PUBLIC_SYNC_TAG_RESYNC_v30b_STORY_VISUAL_BATTLE_WIRING_CONTRACT` per coerenza con il blocco diagnostico in cima.

### D. Tuple count = 1, tier OPTIONAL

Verificato:
- `grep -c "('PROJECT-STORY-VISUAL-BATTLE-WIRING-CONTRACT'" → 1`
- offset tupla dentro OPTIONAL list (non REQUIRED) → OK

## File modificati / creati

- 🔧 `backend/scripts/run_hero_skill_kit_validator_suite.py` (UNICO file modificato): blocco diagnostico top v30b + sentinel inline `RESYNC_v30b` accanto al v30 nel commento sopra la tupla.
- 🆕 `data/design/story_visual_battle/story_visual_battle_wiring_contract_suite_runner_sync_fix_v30b_marker_v1.json` — proof marker v30b.
- 🆕 `docs/divine/223_STORY_VISUAL_BATTLE_WIRING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v30b.md` — questo documento.

## File NON toccati

- Tutti gli 8 file parent v30 (contract, payload, idempotency, transition plan, proof marker, registry v3, doc 222, validator): **UNCHANGED**.
- `frontend/app/story.tsx`, `frontend/app/combat.tsx`, `frontend/constants/homeAssetsManifest.ts`: **UNCHANGED**.
- `backend/battle_engine.py`, `backend/server.py`, `backend/.env`, `backend/routes/artifacts.py`: **UNCHANGED**.
- `backend/routes/material_raid_preview.py`, `backend/routes/gem_socket_preview.py`, `backend/routes/forge.py`: **UNCHANGED**.
- `frontend/app/battlepass.tsx`, `frontend/app/vip.tsx`: **UNCHANGED**.
- Economy / gacha / BP / VIP / shop / IAP / Material Raid / Gem Socket / Rune / Artifact / Divine Weapon / Guild War runtime: **UNCHANGED**.
- Character Bible / hero final_numbers: **UNCHANGED**.

## Garanzie

- `db_writes` = 0
- `runtime_semantics_changed` = false
- `parent_contract_changed` = false
- Tuple count parent = **1** (no duplicate)
- Tuple tier = **OPTIONAL** (never REQUIRED)
- MD5 invarianti su `battle_engine.py`, `.env`, `artifacts.py`, `battlepass.tsx`, `vip.tsx` → invariate.
- Validator parent: **[PASS]**
- Suite: **pass=712, fail=18** (baseline OPTIONAL invariata)

## Escalation policy

Se anche dopo v30b il blob pubblico del `suite_runner.py` resta stale, classificare come:

**`PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT_SUITE_RUNNER_STALE_PLATFORM_BUG_PERSISTENT_ESCALATE`**

e ricorrere a edit manuale GitHub web / push CLI diretto / ticket di supporto piattaforma.

## Verdict atteso

- Locale: `PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v30b_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
- Pubblico (dopo Save to GitHub + verifica blob suite runner): `PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT_COMPLETE_PUBLIC_REPO_VERIFIED`
