# 217 — PROJECT_BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX

## Scopo

Fix immediato del bug di routing della Home + audit/registry formale degli entrypoint di battaglia e dei flussi auto-resolve.

## Problema osservato

- Quasi tutte le modalità risolvono la battaglia in automatico (auto-resolve).
- Il pulsante centrale PLAY della Home era l'unico entrypoint che portava direttamente al simulatore visuale `combat.tsx`.
- Comportamento corretto richiesto: il PLAY centrale della Home deve aprire **Storia** (`/story`), NON `/combat`.
- Tutti gli altri flussi auto-resolve devono essere documentati ma **non convertiti** in questo pack.

## Modifiche eseguite

### 1. Routing fix — `frontend/constants/homeAssetsManifest.ts`

Before:

```ts
play:       '/combat',
```

After:

```ts
// PROJECT_BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX v28:
// Il PLAY centrale della Home apre lo Story/Campaign hub (`/story`), NON la
// route diretta del simulatore visuale `/combat`. La route `/combat` resta
// disponibile come direct/dev/QA entrypoint per il visual battle player e
// verrà ricablata in futuro tramite un pack dedicato di Story/Mode visual
// battle wiring (contract-safe, no duplicate rewards). NON ripristinare
// `play: '/combat'` qui senza un pack dedicato.
play:       '/story',
```

`HOME_ROUTES.battle = '/story'` rimane invariato (già corretto).

### 2. Registry creato

`data/design/battle_entrypoints/battle_entrypoint_registry_v1.json` traccia tutti gli entrypoint di battaglia conosciuti con il loro tipo di risoluzione (visual / auto-resolve / audit_required) e la policy globale.

Entries: `home_play`, `home_mode_battle_button`, `story_stage_battle`, `direct_visual_combat_route`, `raid`, `tower`, `pvp`.

Global policy:
- `do_not_direct_home_play_to_combat` = true
- `do_not_convert_all_autoresolve_modes_in_one_pack` = true
- `future_visual_battle_wiring_requires_contract` = true
- `reward_duplication_guard_required` = true
- `db_write_audit_required` = true

### 3. Proof marker creato

`data/design/battle_entrypoints/battle_entrypoint_routing_fix_proof_marker_v1.json` documenta tutti i booleani di sicurezza (DB writes=0, battle_engine_changed=false, combat_tsx_behavior_changed=false, story_battle_endpoint_changed=false, reward/EXP/economy/gacha/BP/VIP/shop/Material Raid/Gem Socket/Rune/Artifact/Divine Weapon = unchanged).

### 4. Validator dedicato

`backend/scripts/validate_project_battle_entrypoint_routing_and_autoresolve_audit_fix_v1.py` verifica:

- `HOME_ROUTES.play` = `/story` (e NON `/combat`)
- `HOME_ROUTES.battle` = `/story`
- `combat.tsx` esiste e contiene ancora `/api/battle/simulate`
- `story.tsx` esiste e contiene ancora `/api/story/battle`
- Proof marker + registry presenti e coerenti
- Suite runner contiene esattamente una tupla per il pack
- Nessun token DB write / reward / EXP / economy / gacha introdotto nei file modificati

### 5. Suite runner

Aggiunta una sola tupla OPTIONAL v28 con sentinel:
- `PUBLIC_SYNC_TAG_v28_BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX`
- `BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX_REGISTRATION_SENTINEL`
- tuple: `('PROJECT-BATTLE-ENTRYPOINT-ROUTING-AND-AUTORESOLVE-AUDIT-FIX', 'validate_project_battle_entrypoint_routing_and_autoresolve_audit_fix_v1.py')`

## File NON toccati

- `backend/battle_engine.py` (MD5 invariato)
- `backend/.env`, `backend/routes/artifacts.py`, `frontend/app/battlepass.tsx`, `frontend/app/vip.tsx` (MD5 invariati)
- `frontend/app/combat.tsx` (intatto, no behavior changes)
- `frontend/app/story.tsx` (auto-resolve preservato, intatto)
- `backend/server.py` (nessuna modifica)
- `backend/routes/material_raid_preview.py`, `backend/routes/gem_socket_preview.py`, `backend/routes/forge.py`
- Tutti i runtime di Material Raid / Gem Socket / Rune / Artifact / Divine Weapon
- Character Bible, hero final_numbers

## Garanzie

- `db_writes` = 0
- Nessuna conversione auto-resolve → visual combat
- Nessuna modifica a `/api/battle/simulate`, `/api/story/battle`
- Nessuna modifica a reward/EXP/economy/gacha/BP/VIP/shop
- Tuple count v28 = 1 (no duplicate)

## Verdict atteso

- Locale: `PROJECT_BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
- Pubblico (dopo Save to GitHub + verifica): `PROJECT_BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX_COMPLETE_PUBLIC_REPO_VERIFIED`

## Prossimi pack consigliati

1. `PROJECT_STORY_VISUAL_BATTLE_WIRING_DESIGN_PACK`
2. `PROJECT_MODE_BATTLE_ENTRYPOINT_REGISTRY_EXPANSION_PACK`
3. `PROJECT_MATERIAL_RAID_GEM_TRACK_PREVIEW_UNLOCK_PACK`
