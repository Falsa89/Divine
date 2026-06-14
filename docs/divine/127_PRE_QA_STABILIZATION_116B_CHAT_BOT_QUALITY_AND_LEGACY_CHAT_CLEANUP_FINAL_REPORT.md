# 127_PRE_QA_STABILIZATION_116B_CHAT_BOT_QUALITY_AND_LEGACY_CHAT_CLEANUP_FINAL_REPORT

## Verdict
`PRE_QA_STABILIZATION_116B_CHAT_BOT_QUALITY_AND_LEGACY_CHAT_CLEANUP_READY_FOR_GAME_MASTER_REAUDIT`

## Commit SHAs
- Baseline (pre-116B): `b8d81a2e2d16e30896b9c7f01ddf0c0f3a92cde7`
- Pack 116B commit:    `948aa95ea8429ccbdcd08279455254acfd90861e`
- Report/self-ref:     `6e95045beddccb4ef4e60c8c3fa1978637ddab9c`

> **Commit policy** (preservata): MAI `git add -A` / `git add .`. Tutti i file con `git add -- <path>` esplicito.

## Chat / DM surfaces — current state

| Surface | Tipo | Stato pre-116B | Stato post-116B | Note |
|---|---|---|---|---|
| `/plaza` (`frontend/app/plaza.tsx`) | Screen | Gated via `PreQaScreenGate` (early-return prima degli hook) | **PRESERVED gated** | Render mostra `<PreQaScreenGate routeKey="/plaza" />` quando bloccato |
| `/dm` (`frontend/app/dm.tsx`) | Screen | Gated via `PreQaScreenGate` | **PRESERVED gated** | Idem |
| `useChatChannel` (`frontend/hooks/useChatChannel.ts`) | Hook | Solo screen-gate (potenziale esposizione se invocato da non-gated host) | **HOOK-LEVEL FAIL-CLOSE aggiunto** (`isRouteAllowedInPreQa('/plaza')`) | Defense-in-depth: copre `load(channel)` + `send(msg)` |
| `useDM` (`frontend/hooks/useDM.ts`) | Hook | Solo screen-gate | **HOOK-LEVEL FAIL-CLOSE aggiunto** (`isRouteAllowedInPreQa('/dm')`) | Copre 5 path: `refreshThreads`, `refreshMessages`, `openWithUser`, `sendMessage`, `markRead` |
| `preQaNavGuard` blocked set | Utils | `/plaza`, `/dm` gia' presenti | invariato | confermato |
| Backend `/api/plaza/*` | Route | esiste (auth required) | **invariato** (richiede auth, hook non chiama mai in pre-QA) | Pack 116B preferisce non aggiungere lock backend, perche' i hook gia' fail-close lato client (defense-in-depth = sufficient per pre-QA; auth + future server-scope check resta per pack futuri) |
| Backend `/api/dm/*` | Route | esiste (auth required) | invariato | idem |

### Truth on hook fail-close
**Prima** del Pack 116B i hook erano protetti SOLO dal screen-gate (early-return in plaza.tsx / dm.tsx). Se un altro host surface (non testato, ma teoricamente possibile) avesse invocato `useChatChannel` o `useDM` senza wrappare il pre-QA gate, le chiamate `/api/plaza/chat` o `/api/dm/*` sarebbero partite. Pack 116B aggiunge `_chatPreQaBlocked()` e `_dmPreQaBlocked()` come **defense-in-depth hook-level**: anche se l'host non gattea, il hook stesso rifiuta di fare la rete call quando le route canoniche risultano gated.

## Scope / files changed

**Created**:
- `data/design/server_actors/v116b_bot_chat_quality_contract_v1.json` — Bot chat quality contract design-only (pre-QA locked).
- `backend/scripts/validate_pre_qa_stabilization_116b_chat_bot_quality_and_legacy_chat_cleanup.py` — Validator 116B (13 check statici).
- `docs/divine/127_PRE_QA_STABILIZATION_116B_CHAT_BOT_QUALITY_AND_LEGACY_CHAT_CLEANUP_FINAL_REPORT.md` — questo file.

**Modified**:
- `frontend/hooks/useChatChannel.ts` — Hook-level fail-close (`_chatPreQaBlocked` su `load` + `send`).
- `frontend/hooks/useDM.ts` — Hook-level fail-close (`_dmPreQaBlocked` su `refreshThreads` + `refreshMessages` + `openWithUser` + `sendMessage` + `markRead`).
- `backend/scripts/run_pre_qa_safety_validator_suite.py` — registrato 116B come 19ª voce.

**Untouched** (vincoli rispettati):
- Backend chat/dm route handlers: non modificati.
- `data/design/v109_server_isolation/v109_chat_guild_gvg_rankings_isolation_v1.json`: invariato (live_ready=false preservato).
- Bot startup (`backend/bot_system.py`, `backend/server.py:1497-1530`): invariato — kill switch `BOTS_DISABLED=true` gia' attivo da Pack v108_POSTQA_A.
- `battle_engine.py`, combat/tower runtime, gacha, reward, Character Bible, skill catalog: **untouched**.
- Battle Power 116A/EXT/FIX-A: invariati.

## Bot chat quality contract (`v116b_bot_chat_quality_contract_v1.json`)

### Header
- `_meta.scope = "design_only_pre_qa_locked"`
- `_meta.is_runtime = false`
- `_meta.do_not_use_for_runtime_activation = true`
- `runtime_state = "design_only_pre_qa_locked"`
- Supersede parziale di v97/v98 (estende invarianti, non sostituisce)

### `live_activation_flags` (4 flag, **tutti false**)
- `bot_chat_live`
- `dm_bot_live`
- `plaza_chat_live`
- `fake_users_presented_as_real`

### `forbidden_bot_behaviors` (13 invarianti, tutte true)
- `manual_ultimate_advice_forbidden`
- `real_iap_recommendation_forbidden`
- `real_pii_forbidden`
- `toxicity_forbidden`
- `competing_game_ads_forbidden`
- `out_of_context_response_forbidden`
- `invented_kit_or_banner_or_event_claim_forbidden`
- `pressure_to_spend_forbidden`
- `pii_collection_forbidden`
- `personal_political_religious_topics_forbidden`
- `moderation_bypass_forbidden`
- `impersonation_of_real_player_forbidden`
- `pretending_to_be_admin_or_dev_forbidden`

### `forbidden_topics_examples` (12 esempi concreti in italiano)
Include: "ti consiglio di usare l'ultimate ora", "compra il pacchetto premium ora", "dimmi il tuo numero di telefono", "<competitor game> e' meglio", "rate boostato segreto", etc.

### `required_safety_invariants_before_live` (10 invarianti, tutte true)
- `server_scope_required`
- `moderation_required_before_live`
- `rate_limits_required_before_live`
- `admin_kill_switch_required`
- `audit_log_required_before_live`
- `bot_isolation_required_before_live`
- `fake_users_must_be_distinguishable_from_real_players`
- `intent_classifier_must_be_versioned`
- `fixture_dryrun_must_pass_quality_gates`
- `min_human_review_pass_count: 1`

### `fixture_dryrun_quality_gates` (10 gates)
Include: `max_response_length_chars: 280`, `must_use_italian_when_user_uses_italian: true`, `must_indicate_bot_nature_in_admin_inspector: true`.

### `ui_truth_requirements` (5 invarianti + 4 esempi copy preferiti + 3 esempi copy vietati)
Copy preferiti: "Chat in preparazione", "Messaggi privati in preparazione", "Richiede server scope e moderazione", "Non disponibile in Pre-QA".

### `preserved_pre_qa_locks` (6 lock confermati)
- `plaza_screen_gated_via_preqascreengate: true`
- `dm_screen_gated_via_preqascreengate: true`
- `chat_hook_must_fail_close_when_plaza_gated: true`
- `dm_hook_must_fail_close_when_dm_gated: true`
- `bot_startup_disabled_via_env_BOTS_DISABLED: true`
- `no_account_wide_chat_endpoint_introduced: true`

## Validator results

### `python3 backend/scripts/validate_pre_qa_stabilization_116b_chat_bot_quality_and_legacy_chat_cleanup.py`
**PASS — 13/13**:
1. `[1] /plaza screen-gated via PreQaScreenGate (early-return before hooks) OK`
2. `[2] /dm screen-gated via PreQaScreenGate OK`
3. `[3] useChatChannel hook-level fail-close (load + send) OK`
4. `[4] useDM hook-level fail-close (5 paths) OK`
5. `[5] /plaza and /dm in preQaNavGuard blocked set OK`
6. `[6] bot chat quality contract v116b present + design_only_pre_qa_locked OK`
7. `[7] contract live_activation_flags all false OK`
8. `[8] contract forbidden_bot_behaviors all true (6 invariants) OK`
9. `[9] contract required_safety_invariants_before_live (4 invariants) OK`
10. `[10] v109 chat live_ready=false / pre_qa_locked preserved OK`
11. `[11] no out-of-scope imports across pack-116B files OK`
12. `[12] no .pyc / __pycache__ tracked OK`
13. `[13] pre-QA safety suite registers 116B validator OK`

### Catena completa richiesta dal pack
| Script | Risultato |
|---|---|
| `validate_pre_qa_stabilization_116b_chat_bot_quality_and_legacy_chat_cleanup.py` | **13/13 PASS** |
| `validate_pre_qa_stabilization_116a_ext_fix_a_team_power_source_truth.py` | 12/12 PASS |
| `validate_pre_qa_stabilization_116a_ext_hero_card_power_and_bonus_source_map.py` | 11/11 PASS |
| `validate_pre_qa_stabilization_115f_repo_hygiene_and_validator_truth.py` | 7/7 PASS |
| `sweep_repo_hygiene.py` | `clean=true` |
| `run_pre_qa_safety_validator_suite.py` | **19/19 PASS, 0 FAIL, 0 SKIP** |

## Curl evidence (backend up)
```
GET  /api/plaza/chat                                      -> HTTP 401 (auth required)
GET  /api/plaza/chat?channel=global&server_id=s1          -> HTTP 401 (auth required)
GET  /api/dm/threads                                      -> HTTP 401 (auth required)
GET  /api/plaza/channels                                  -> HTTP 401 (auth required)
```

→ Tutti gli endpoint chat/DM richiedono auth Bearer token. I hook fail-close pre-QA evitano ogni chiamata da pre-QA UI; solo un client con token valido potrebbe raggiungerli (e nessun client in pre-QA dovrebbe averne motivo). Pack 116B sceglie esplicitamente di NON aggiungere lock backend 423 per evitare regressione su test esistenti — i hook fail-close + screen gate sono sufficienti per pre-QA stabilization.

## Bot startup status (audit only, NO mutation)
- `backend/bot_system.py`: contiene `initialize_bots("default")` e `run_bot_cycle("default")` LEGACY (account-wide).
- `backend/server.py:1503`: hard kill switch `BOTS_DISABLED=true` o `BOT_KILL_SWITCH=true` salta `initialize_bots`/`run_bot_cycle`. **Preservato invariato** (Pack v108_POSTQA_A).
- Pack 116B **NON crea bot account**, **NON muta bot state**, **NON attiva bot chat**.
- Refactor del `("default")` server-scoping legacy e' **deferred** (broad refactor vietato dal pack).

## Safety invariants (preservate)
- DB writes: **0**.
- Chat live: **false**. DM live: **false**. Bot chat live: **false**. DM bot live: **false**.
- Bot account creation: **0**. Bot state mutation: **0**.
- Moderation bypass: **NESSUNO** (contract richiede moderazione esplicita pre-live).
- gacha/summon unlock: **0**. Reward/progress/EXP/gold/gems mutation: **0**.
- Combat authoritative: **false**. `battle_engine.py`: **untouched**.
- Battle Power 116A/EXT/FIX-A: invariati (validator 116A 11/11 + 116A-EXT 11/11 + FIX-A 12/12 confermano).
- Red Dot: **NON implementato**. Artifact/Divine Weapon/Cosmetics live: **false** (invariato 115G/116A-EXT).
- Character Bible: **untouched** (v109 chat letto, NON modificato).
- gacha rates: **untouched**.
- `data/design/**` modificate: 0 (solo NUOVO file `v116b_bot_chat_quality_contract_v1.json` in cartella esistente `server_actors/`).
- Tracked `.pyc` / `__pycache__`: **0** (hygiene 115F preservata).

## UI copy truth
Le surface `/plaza` e `/dm` rendono `<PreQaScreenGate routeKey="/plaza|/dm" />` quando bloccate. Il componente PreQaScreenGate gia' mostra una copy onesta ("In preparazione" / "Non disponibile in Pre-QA" — definita nel componente). Le altre superfici della app NON contengono inviti a "parlare in chat" o "aprire DM con il giocatore X" — verificato grep su frontend per stringhe accese ("apri chat", "parla con bot", "globale sempre"). Nessuna stringa misleading trovata.

> Nota: il contract 116B include `ui_truth_requirements.preferred_copy_examples_it` e `forbidden_copy_examples_it` come riferimento canonico per ogni futura modifica copy.

## Deferred (post-116B roadmap)
- **116C — Red Dot notification badge foundation**: badge UI, NON push notification.
- **117+ — Bot chat live activation roadmap**: richiede *prima* moderation + rate-limits + admin kill-switch + bot isolation + intent classifier versionato + fixture dryrun pass + 1+ human review (vedi contract).
- **117+ — Plaza/DM endpoint server-scope hardening**: introduzione `server_id` required + envelope locked 423 (analogo Pack 115G artifacts) quando sara' il momento.
- **117+ — Refactor di `initialize_bots("default") → server-scoped**: broad refactor vietato in 116B.

## Stop condition
Manual QA rimane in pausa fino al re-audit del Game Master.
**Non procedere a 116C** prima del re-audit esplicito.
