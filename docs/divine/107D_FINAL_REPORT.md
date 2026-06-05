# Pack v107D — Final Report

**Verdict:**
`MEGA_RELEASE_ACCELERATION_59_TSX_MD5_SUPERSEDE_AND_REAL_BATTLE_LAUNCH_CONSUMER_BINDING_READY_WITH_PARTIAL_BINDING_GAPS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

**Codice pack:** `MEGA_RELEASE_ACCELERATION_59_v107D`
**Stato:** READY (con gap di binding parziali, dichiarati e documentati)
**Lingua:** Italiano
**Commit di partenza:** `7a10d6aefee53e5f19a0ce89c771591434094cfb`

---

## 1. Baseline pre-modifiche (fotografia onesta)

Eseguita prima di toccare qualunque file con `python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py`:

```
pass         = 1105
fail         = 23   (OPTIONAL FAIL, soglia target ≤ 30)
miss         = 0
required_fail= 0
exit_code    = 0
```

Quindi la suite era già sana e veniva accettata globalmente. Il pack v107D non parte da uno stato rotto.

---

## 2. Ragione della disambiguazione (chat utente vs design del pack v107D)

L'utente, nel messaggio di kickoff, aveva incluso tra i punti operativi:

> 9. applica binding reale su combat.tsx
> 10. aggiorna story.tsx con percorso player-facing verso pre-battle-lobby
> 11. marca /story/battle come QA/deprecated

Tuttavia i validator del pack v107D già presenti in `/app/backend/scripts/` (caricati dallo ZIP del pack stesso) richiedono **esplicitamente** che `combat.tsx` e `story.tsx` **NON** siano modificati in questo step e che il binding venga **DEFERRED a v108_pre / v107E_revised**.

Su esplicita richiesta dell'utente (risposta in chat dopo presentazione del conflitto), è stata adottata l'**Opzione A**:

> Rispetta il design effettivo dei validator v107D già presenti nel repo/container.
> Non forzare modifiche a combat.tsx o story.tsx in questo step se i validator v107D li dichiarano esplicitamente deferred.

Decisione registrata:

```
v107D = completamento coerente con i validator caricati
pre-battle-lobby.tsx = binding applicato / verificato
combat.tsx           = DEFERRED a v108_pre o pack revised
story.tsx            = DEFERRED a v108_pre o pack revised
```

Nessun validator è stato indebolito, modificato, eliminato o aggirato per realizzare questa decisione.

---

## 3. Validator che richiedono `combat_tsx_modified_v107D = false`

| Validator | Vincolo enforced |
|---|---|
| `validate_v107d_tsx_md5_supersede_review.py` | `combat_tsx.v107D_modified = false` (FAIL se true) |
| `validate_v107d_combat_parser_binding.py` | `combat_tsx_modified_v107d = false` + status `COMBAT_BINDING_DEFERRED_TO_v108_PRE_LEGACY_VALIDATORS_PROTECTED` |
| `validate_v107d_tsx_md5_supersede_review.py` | richiede ≥10 voci in `combat.validators_to_supersede_v108_pre` (lista esplicita degli MD5 baseline legacy da superare in v108_pre) |
| `validate_v107d_route_menu_exposure_safety.py` | `new_player_facing_routes_exposed_v107d = 0` (combat non viene esposto come nuovo entrypoint) |

## 4. Validator che richiedono `story_tsx_modified_v107D = false`

| Validator | Vincolo enforced |
|---|---|
| `validate_v107d_story_launch_path.py` | `story_tsx_modified_v107d = false` + status `STORY_TSX_UNCHANGED_LOBBY_BINDING_IS_LIVE_PROOF` |
| `validate_v107d_story_launch_path.py` | `story_battle_endpoint_modified_v107d = false` |
| `validate_v107d_route_menu_exposure_safety.py` | `new_player_facing_routes_exposed_v107d = 0` (nessun nuovo player path forzato in story) |

---

## 5. Conferme di non-modifica e di binding

### 5.1 `combat.tsx` NON è stato toccato in v107D
Verifica: nessun token v107D (`v107D`, `EXPO_PUBLIC_V107D_PREVIEW_LAUNCH_ENABLED`, `launchFromLobby`, `preBattleLobbyAdapter`) è presente nel file. Il binding tramite `combatLaunchParser.ts` (creato in v107A come helper non consumato) resta disponibile ma **non collegato** in attesa di v108_pre.

### 5.2 `story.tsx` NON è stato toccato in v107D
Verifica: nessun cambio al routing player-facing di `/story/*` né all'endpoint backend. La prova di flusso `Story → Lobby → /api/battle/launch` resta indiretta, garantita dal binding live nel lobby.

### 5.3 `pre-battle-lobby.tsx` contiene il binding v107D
File: `/app/frontend/app/pre-battle-lobby.tsx`. Token verificati presenti:

```
launchFromLobby
preBattleLobbyAdapter
EXPO_PUBLIC_V107D_PREVIEW_LAUNCH_ENABLED
v107D
```

Il binding è **gated OFF di default**: la chiamata `launchFromLobby` viene effettuata solo se `process.env.EXPO_PUBLIC_V107D_PREVIEW_LAUNCH_ENABLED === 'true'`. In produzione il comportamento runtime player-facing è **invariato**.

Status JSON associato: `data/design/battle_launch/v107d_pre_battle_lobby_real_binding_result_v1.json` → `REAL_BINDING_APPLIED_GATED_OFF_BY_DEFAULT`.

---

## 6. Forensic audit (perché v107C aveva richiesto il revert TSX)

File: `data/design/closed_alpha/v107d_failed_binding_forensic_audit_v1.json`
Validator: `validate_v107d_failed_binding_forensic_audit.py` → **PASS**.

Conclusione documentata:
- ≥10 validator MD5-baseline legacy si attivavano sull'edit di `combat.tsx` non superseduto, generando l'esplosione di Optional Fails > 30 osservata in v107C.
- Ipotesi v107D testata: limitare il binding reale al solo `pre-battle-lobby.tsx` (la cui catena di validator MD5 è stata formalmente supersedutata) **NON** modificando `combat.tsx`. Conclusione: ipotesi confermata, suite resta sana (`OPTIONAL FAIL = 23`).

---

## 7. MD5 supersede review

File: `data/design/closed_alpha/v107d_tsx_md5_supersede_review_v1.json`
Validator: `validate_v107d_tsx_md5_supersede_review.py` → **PASS**.

Riepilogo:
- `pre_battle_lobby_tsx.v107D_modified = true` → MD5 supersedutato formalmente per accomodare il binding `launchFromLobby` / `preBattleLobbyAdapter`.
- `combat_tsx.v107D_modified = false` → nessun supersede effettuato; la lista `combat.validators_to_supersede_v108_pre` (≥10 elementi) è preservata come historical reference per il pack successivo.
- `silent_validator_deletion = false`, `validator_weakening = false`, `fake_PASS = false`.

---

## 8. Backend loader server_id real acceptance

File: `data/design/server_scope/v107d_backend_loader_server_id_real_acceptance_result_v1.json`
Validator: `validate_v107d_backend_loader_server_id_real_acceptance.py` → **PASS**.

Stato:
- `feature_flag_default = false` (SERVER_SCOPED_RUNTIME_ENABLED resta OFF).
- `adoption_status = V107C_PROBE_ROUTER_LIVE_NO_NEW_LOADER_MODIFIED_v107D`.
- 5 probe endpoint live introdotti in v107C (`/api/v107c/loader-probe/*`), 0 loader esistenti modificati in v107D.
- `backend_isolation_live = false` (PENDING).
- Banner UI: `SERVER_DATA_ISOLATION_BACKEND_PENDING` (onesto, invariato).
- `db_writes_performed = 0`, `fake_isolation_live = false`.

---

## 9. E2E smoke (riuso v107C)

File: `data/design/battle_launch/v107d_e2e_smoke_result_v1.json`
Validator: `validate_v107d_e2e_smoke.py` → **PASS**.

- `reuses_v107c_smoke = true`
- `v107c_smoke_overall_pass = true`
- `v107c_smoke_cases_pass == v107c_smoke_cases_total`
- Safety: `no_db_writes = true`, `no_reward_grant = true`, `no_progress_write = true`, `no_currency_mutation = true`, `hiding_preview_state = false`.

---

## 10. Optional fail baseline guard

File: `data/design/closed_alpha/v107d_optional_fail_baseline_guard_v1.json`
Validator: `validate_v107d_optional_fail_baseline_guard.py` → **PASS**.

```
baseline_pre_v107d  = 23
baseline_post_v107d = 23
target_max          = 30
baseline_preserved  = true
hiding_optional_fails = false
silent_validator_deletion = false
validator_weakening = false
```

**Conferma: `OPTIONAL FAIL ≤ 30` rispettato (23/23).**

---

## 11. Route / menu exposure safety

File: `data/design/battle_launch/v107d_route_menu_exposure_safety_result_v1.json`
Validator: `validate_v107d_route_menu_exposure_safety.py` → **PASS**.

- `new_player_facing_routes_exposed_v107d = 0`
- `new_menu_items_exposed_v107d = 0`
- `new_backend_routers_added_v107d = 0`
- `hidden_intentional_routes_unchanged = true`
- `alpha_menu_preview_unchanged = true`
- `qa_routes_not_promoted = true`

---

## 12. Story launch path

File: `data/design/battle_launch/v107d_story_launch_path_result_v1.json`
Validator: `validate_v107d_story_launch_path.py` → **PASS**.

- `story_tsx_modified_v107d = false`
- `story_battle_endpoint_modified_v107d = false`
- `proof_of_launch_path` presente (il lobby gated binding è già live proof del path autoritativo).
- Status: `STORY_TSX_UNCHANGED_LOBBY_BINDING_IS_LIVE_PROOF`.

---

## 13. Suite master finale (post-modifiche)

Comando: `python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py`

```
pass         = 1115   (era 1105 → +10 = 10 validatori v107D registrati nel runner, tutti PASS)
fail         = 23     (OPTIONAL FAIL invariato, ≤ 30 target)
miss         = 0
required_fail= 0
exit_code    = 0
```

Outcome dei 10 validatori v107D nel runner master:

| Track | Validator | Esito |
|---|---|---|
| PROJECT-V107D-FAILED-BINDING-FORENSIC-AUDIT | validate_v107d_failed_binding_forensic_audit.py | PASS |
| PROJECT-V107D-TSX-MD5-SUPERSEDE-REVIEW | validate_v107d_tsx_md5_supersede_review.py | PASS |
| PROJECT-V107D-PRE-BATTLE-LOBBY-REAL-BINDING | validate_v107d_pre_battle_lobby_real_binding.py | PASS |
| PROJECT-V107D-COMBAT-PARSER-BINDING | validate_v107d_combat_parser_binding.py | PASS |
| PROJECT-V107D-STORY-LAUNCH-PATH | validate_v107d_story_launch_path.py | PASS |
| PROJECT-V107D-BACKEND-LOADER-SERVER-ID-REAL-ACCEPTANCE | validate_v107d_backend_loader_server_id_real_acceptance.py | PASS |
| PROJECT-V107D-E2E-SMOKE | validate_v107d_e2e_smoke.py | PASS |
| PROJECT-V107D-ROUTE-MENU-EXPOSURE-SAFETY | validate_v107d_route_menu_exposure_safety.py | PASS |
| PROJECT-V107D-OPTIONAL-FAIL-BASELINE-GUARD | validate_v107d_optional_fail_baseline_guard.py | PASS |
| MEGA-RELEASE-ACCELERATION-59-v107D-ROLLUP | validate_mega_release_acceleration_59_v107d_rollup.py | PASS |

---

## 14. Safety flags (riepilogo non negoziabile)

```
fake_PASS                       = false
validator_weakening             = false
silent_validator_deletion       = false
hiding_optional_fails           = false
hiding_preview_state            = false
new_player_facing_feature       = false
combat_tsx_changes              = false
story_tsx_changes               = false
reward_grant                    = false
progress_live_write             = false
currency_inventory_mutation     = false
gacha_shop_vip_bp_mutation      = false
battle_engine_formula_rewrite   = false
broad_combat_tsx_rewrite        = false
destructive_migration           = false
db_writes_performed             = 0
backend_isolation_live          = false   (banner: SERVER_DATA_ISOLATION_BACKEND_PENDING)
fake_isolation_live             = false
authoritative_battle_live_claim = false
commercial_release_claim        = false
```

---

## 15. File modificati / creati in v107D

**Modificato (binding TSX, già applicato nella sessione precedente, qui solo verificato):**
- `/app/frontend/app/pre-battle-lobby.tsx`

**Modificato (registrazione runner master, questo step):**
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` (aggiunti 10 nuovi tuple v107D dopo il rollup v107C)

**Design JSON v107D (già presenti, verificati):**
- `data/design/battle_launch/v107d_pre_battle_lobby_real_binding_result_v1.json`
- `data/design/battle_launch/v107d_combat_parser_binding_result_v1.json`
- `data/design/battle_launch/v107d_story_launch_path_result_v1.json`
- `data/design/battle_launch/v107d_e2e_smoke_result_v1.json`
- `data/design/battle_launch/v107d_route_menu_exposure_safety_result_v1.json`
- `data/design/server_scope/v107d_backend_loader_server_id_real_acceptance_result_v1.json`
- `data/design/closed_alpha/v107d_failed_binding_forensic_audit_v1.json`
- `data/design/closed_alpha/v107d_tsx_md5_supersede_review_v1.json`
- `data/design/closed_alpha/v107d_optional_fail_baseline_guard_v1.json`

**Validator Python v107D (già presenti, verificati):**
- 9 validator individuali in `/app/backend/scripts/validate_v107d_*.py`
- 1 rollup in `/app/backend/scripts/validate_mega_release_acceleration_59_v107d_rollup.py`

**Marker rollup generato:**
- `data/design/release_acceleration/mega_release_acceleration_59_v107d_rollup_marker_v1.json`

---

## 16. Cosa v107D NON ha fatto (gap dichiarati, onesti)

> v107D **non completa ancora** il flow Story → Lobby → Combat.
> v107D **completa solo** il binding lobby e documenta che combat/story restano deferred.

- ❌ `combat.tsx` non consuma ancora `/api/battle/launch` né `combatLaunchParser.ts`.
- ❌ `story.tsx` non è ancora stato modificato per redirigere player-facing al lobby.
- ❌ `/story/battle` non è ancora marcato come QA/deprecated.
- ❌ `SERVER_SCOPED_RUNTIME_ENABLED` resta a `false`. Banner UI: `SERVER_DATA_ISOLATION_BACKEND_PENDING`.
- ❌ Nessun apply live di `player_server_profiles`. Nessuna scrittura su DB.
- ❌ Nessun reward grant, progress live write, currency/inventory/gacha/shop/VIP/BP mutation.

---

## 17. Next recommended pack

```
v108_pre  (oppure v107E_revised)
TSX combat/story binding con validator e MD5 supersede progettati ESPLICITAMENTE per accettare la modifica.
```

Pack successivi (in coda, NON da eseguire finché v108_pre non è chiuso):
- **v108** — Authoritative Battle Engine + Mode Runtime Conversion (player-facing flow autoritativo).
- **v109** — Chat / Guild / Live Events server isolation.
- **v110** — Legacy data cleanup apply.
- Apply live `player_server_profiles` solo dietro autorizzazione esplicita con flag.

---

## 18. Commit hash di riferimento

```
HEAD pre-pack:  7a10d6aefee53e5f19a0ce89c771591434094cfb
```

(I file `.pyc` modificati sono cache di esecuzione, non vanno commitati.)

---

## 19. Verdict string finale

```
MEGA_RELEASE_ACCELERATION_59_TSX_MD5_SUPERSEDE_AND_REAL_BATTLE_LAUNCH_CONSUMER_BINDING_READY_WITH_PARTIAL_BINDING_GAPS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

`PUBLIC_SYNC_PENDING`: la sincronizzazione su repo pubblico non è parte di questo step (resta a discrezione utente tramite pulsante Publish di Emergent).
