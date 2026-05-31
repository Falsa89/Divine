# 221 — PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v29d

## Scopo

Terzo (e ultimo programmato) micro-pack di sync per risolvere il bug persistente di stale-push del `backend/scripts/run_hero_skill_kit_validator_suite.py` su GitHub main. Dopo che v29b e v29c hanno entrambi pubblicato marker e doc ma non sono riusciti a rinfrescare il blob del suite runner, v29d adotta una strategia **più forte** del semplice commento aggiuntivo.

## Catena dei commit

- Parent v29: `0c6601b4` — contract + design + doc 218 + validator + tupla suite (locale OK, pubblico parziale).
- Sync v29b: `9f030a88` — marker + doc 219 + sentinel `RESYNC_v29b` (locale OK, pubblico ancora stale).
- Sync v29c: `7a565897` — marker + doc 220 + sentinel `RESYNC_v29c` (locale OK, pubblico ancora stale).
- Sync v29d (questo): strategia rafforzata su 3 fronti simultanei.

## Strategia v29d (stronger blob refresh)

### A. Blocco diagnostico in cima al file

Inserito immediatamente dopo lo shebang `#!/usr/bin/env python3`, prima di qualsiasi altro `PUBLIC_SYNC_TAG` storico: un blocco di ~50 righe `PUBLIC_SYNC_DIAGNOSTIC_BLOCK_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_V29D` che contiene tutti e 4 i sentinel `v29/v29b/v29c/v29d`, l'ID validator, il file validator, l'inline sentinel REGISTRATION_SENTINEL, il tuple_count atteso (1), il tier atteso (OPTIONAL), i flag di safety (db_writes=0, runtime_semantics_changed=false, ...) e il path di escalation se il bug persiste.

### B. Tupla rilocata in cima al blocco OPTIONAL

La tupla `('PROJECT-VISUAL-BATTLE-ROUTING-CONTRACT-AND-GUILD-WAR-REPLAY-POLICY', '...v1.py')` è stata RIMOSSA dalla posizione precedente (fondo blocco OPTIONAL, riga ~1672) e INSERITA come **prima entry** dell'OPTIONAL list (riga 370 attuale), subito dopo `OPTIONAL = [`, con un blocco di commento ricco di tutti i 5 sentinel canonici inline (v29/v29b/v29c/v29d/REGISTRATION_SENTINEL) + cross-reference ai 11 file design/doc/proof correlati (parent + v29b + v29c + v29d).

Nella posizione vecchia (fondo OPTIONAL, dopo la tupla v28 `BATTLE-ENTRYPOINT-ROUTING-AND-AUTORESOLVE-AUDIT-FIX`) è stato lasciato un commento esplicativo che indica la rilocazione e la motivazione, **senza duplicare la tupla**.

### C. Tuple count = 1

Verificato via `grep -c "('PROJECT-VISUAL-BATTLE-ROUTING-CONTRACT-AND-GUILD-WAR-REPLAY-POLICY'"` → `1`.

### D. Tier preservato

La tupla resta nell'array `OPTIONAL` (mai promossa a `REQUIRED`). Verifica programmatica via offset: tuple at offset 25764, OPTIONAL list range 23127-35542 → dentro OPTIONAL.

## File modificati / creati

- 🔧 `backend/scripts/run_hero_skill_kit_validator_suite.py` (UNICO file modificato): blocco diagnostico top + tupla rilocata + nota di rilocazione in posizione precedente.
- 🆕 `data/design/battle_visual_routing/battle_visual_routing_contract_suite_runner_sync_fix_v29d_marker_v1.json` — proof marker v29d.
- 🆕 `docs/divine/221_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v29d.md` — questo documento.

## File NON toccati

- Tutti i 7 file parent v29 (contract, guild war policy, roadmap, proof marker, registry v2, doc 218, validator): **UNCHANGED**.
- Marker e doc v29b/v29c: **UNCHANGED**.
- `frontend/app/story.tsx`, `frontend/app/combat.tsx`, `frontend/constants/homeAssetsManifest.ts`: **UNCHANGED**.
- `backend/battle_engine.py`, `backend/server.py`, `backend/.env`, `backend/routes/artifacts.py`: **UNCHANGED**.
- `backend/routes/material_raid_preview.py`, `backend/routes/gem_socket_preview.py`, `backend/routes/forge.py`: **UNCHANGED**.
- `frontend/app/battlepass.tsx`, `frontend/app/vip.tsx`: **UNCHANGED**.
- Economy / gacha / BP / VIP / shop / IAP / Material Raid / Gem Socket / Rune / Artifact / Divine Weapon runtime: **UNCHANGED**.
- Character Bible / hero final_numbers: **UNCHANGED**.

## Garanzie

- `db_writes` = 0
- `runtime_semantics_changed` = false
- `parent_contract_changed` = false
- Tuple count parent = **1** (no duplicate)
- Tuple tier = **OPTIONAL** (never REQUIRED)
- MD5 invarianti su `battle_engine.py`, `.env`, `artifacts.py`, `battlepass.tsx`, `vip.tsx` → invariate.
- Validator parent: **[PASS]**
- Suite: **pass=711, fail=18** (baseline OPTIONAL invariata)

## Escalation policy

Se anche dopo v29d il blob pubblico del `suite_runner.py` resta stale (token v29 non visibili / tupla v29 non eseguita su GitHub Actions/CI), il problema deve essere classificato come:

**`PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_STALE_PLATFORM_BUG_PERSISTENT_ESCALATE`**

E NON si deve procedere con ulteriori sync-fix v29e+. Le opzioni alternative sono:

1. Edit manuale del file direttamente dall'interfaccia web di GitHub.
2. Bypass del meccanismo "Save to GitHub" con un push diretto via CLI.
3. Apertura ticket di supporto piattaforma.

## Verdict atteso

- Locale: `PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_SUITE_RUNNER_SYNC_FIX_v29d_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
- Pubblico (dopo Save to GitHub + verifica blob suite runner): `PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_COMPLETE_PUBLIC_REPO_VERIFIED`
