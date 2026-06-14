# 128 — Pre-QA Stabilization 116C — Red Dot Notification Badge Foundation — FINAL REPORT

**Pack ID:** `PRE_QA_STABILIZATION_116C_RED_DOT_NOTIFICATION_BADGE_FOUNDATION`
**Data esecuzione:** 2026-06-14 (UTC)
**Esito sintetico:** ✅ **PASS — READY_FOR_GAME_MASTER_REAUDIT**

---

## 1. Scope e contratto

Il Pack 116C introduce **soltanto** la *foundation read-only / server-scoped* per il
sistema Red Dot / Notification Badge. NON attiva alcuna funzionalità reale di
claim, reward, mail/read-all, push, gacha, shop, combat o chat.

### Contratto rispettato
- ✅ Solo lettura (no DB writes)
- ✅ Server-scoped (server_id obbligatorio, no silent `s1` fallback)
- ✅ No claim activation / no read-all / no spend / no buy / no summon
- ✅ No push notification / no toast
- ✅ No combat / no battle_engine / no character bible rewrite
- ✅ No modifiche live a Chat/Bot (Pack 116B preservato)
- ✅ No modifiche a Battle Power (Pack 116A/EXT/FIX-A preservati)
- ✅ No bytecode (`.pyc` / `__pycache__`) tracciato in git
- ✅ Nessun `git add -A` / `git add .` usato

---

## 2. Deliverable creati

| File | Ruolo | Stato |
|------|-------|-------|
| `data/design/red_dot/red_dot_notification_badge_source_map_v1.json` | Source-of-truth (design-only) delle sorgenti red-dot. 14 sorgenti obbligatorie mappate; tutte con `mutation_forbidden=true`. | ✅ |
| `backend/utils/red_dot_summary.py` | Helper puro (no DB). Espone `build_red_dot_metadata()` + `build_summary()` con versione `red_dot_v1_preqa_read_only_foundation`. | ✅ |
| `backend/routes/red_dot.py` | Router `prefix="/api/red-dot"` con `GET /summary` (server_id required, 400 `SERVER_ID_REQUIRED` altrimenti) e `GET /metadata`. Solo `find_one` su PSP. | ✅ |
| `frontend/src/hooks/useRedDotSummary.ts` | Hook GET-only. Nessun `POST/PUT/DELETE`, nessun `/claim`, `/read-all`, `/spend`. Cancella stale request via `reqIdRef`. | ✅ |
| `frontend/components/ui/RedDotBadge.tsx` | Componente visuale puro. Nessun `apiCall`, `onPress` o `TouchableOpacity`. | ✅ |
| `frontend/app/(tabs)/home.tsx` | Importa `useRedDotSummary` + `RedDotBadge` (wiring visuale soltanto). | ✅ |
| `backend/scripts/validate_pre_qa_stabilization_116c_red_dot_notification_badge_foundation.py` | Validator dedicato 14-step. | ✅ |
| `backend/scripts/run_pre_qa_safety_validator_suite.py` | **Aggiornato**: registra validator 116C. | ✅ |

---

## 3. Verdetto validator

| Validator | Verdetto | Returncode |
|-----------|----------|------------|
| `validate_pre_qa_stabilization_116c_red_dot_notification_badge_foundation.py` | ✅ **PASS** | 0 |
| `validate_pre_qa_stabilization_116b_chat_bot_quality_and_legacy_chat_cleanup.py` | ✅ **PASS** | 0 |
| `validate_pre_qa_stabilization_116a_ext_fix_a_team_power_source_truth.py` | ✅ **PASS** | 0 |
| `validate_pre_qa_stabilization_115f_repo_hygiene_and_validator_truth.py` | ✅ **PASS** | 0 |
| `sweep_repo_hygiene.py` | ✅ **CLEAN** (5 `__pycache__` rimossi da FS; 0 tracciati git) | 0 |
| `run_pre_qa_safety_validator_suite.py` | ✅ **PRE_QA_SAFETY_SUITE_PASS** — 20/20 PASS, 0 FAIL, 0 SKIPPED, `backend_up=True` | 0 |

### 3.1 Riepilogo output validator 116C (step-by-step)
```
[1]  source map present + design_only_read_only OK
[2]  required source ids present (14 sources mapped) OK
[3]  backend helper exists + version constant OK
[4]  route /api/red-dot/summary + SERVER_ID_REQUIRED + no silent s1 OK
[5]  helper + route are READ-ONLY (no insert/update/delete/$set/$inc) OK
[6]  route does NOT call any claim/read-all/spend/push endpoint OK
[7]  metadata builder exposes read-only flags OK
[8]  frontend hook GET-only (no POST/PUT/DELETE/claim) OK
[9]  RedDotBadge visual-only (no apiCall, no onPress) OK
[10] Home wires Red Dot foundation imports (visual-only) OK
[11] no out-of-scope imports OK
[12] no .pyc / __pycache__ tracked OK
[13] pre-QA safety suite registers 116C OK
[14] runtime /api/red-dot/metadata OK
```

### 3.2 Riepilogo output validator 116B (chat/bot quality)
```
[1] /plaza screen-gated via PreQaScreenGate OK
[2] /dm screen-gated via PreQaScreenGate OK
[3] useChatChannel hook-level fail-close (load + send) OK
[4] useDM hook-level fail-close (5 paths) OK
[5] /plaza and /dm in preQaNavGuard blocked set OK
[6] bot chat quality contract v116b present + design_only_pre_qa_locked OK
[7] contract live_activation_flags all false OK
[8] contract forbidden_bot_behaviors all true (6 invariants) OK
[9] contract required_safety_invariants_before_live (4 invariants) OK
[10] v109 chat live_ready=false / pre_qa_locked preserved OK
[11] no out-of-scope imports across pack-116B files OK
[12] no .pyc / __pycache__ tracked OK
[13] pre-QA safety suite registers 116B validator OK
```

### 3.3 Riepilogo output validator 116A-EXT FIX-A (team power source truth)
```
[1] route exposes truth metadata (team_source/slot_count/valid/invalid/missing_reason) OK
[2] slot validity counting (valid/invalid + conditional active_team_power) OK
[3] no fake team (valid=0 → team_missing=True, power=0) OK
[4] owned heroes NOT summed when team missing OK
[5] no account-wide team fallback in battle_power route OK
[6] no DB writes in battle_power route OK
[7] formula version invariata (battle_power_v1_preqa_derived) OK
[8] battle.tsx: no /api/team account-wide + supporta slot_index OK
[9] home.tsx still uses useBattlePowerSummary (no regression) OK
[10] no out-of-scope imports OK
[11] pre-QA safety suite registers 116A-EXT FIX-A OK
[12] runtime summary truth metadata OK
```

### 3.4 Riepilogo output validator 115F (repo hygiene + validator truth)
```
[1] no __pycache__ tracked by git OK
[2] no .pyc tracked by git OK
[3] .gitignore bytecode coverage OK
[4] smoke 114 executes validator + bracket-matched check OK
[5] rollup 114 executes validator + smoke OK
[6] pre-QA safety suite references all required validators OK
[7] no out-of-scope runtime implementations in pack-115F scripts OK
```

### 3.5 Riepilogo output `sweep_repo_hygiene.py`
```json
{
  "tool": "sweep_repo_hygiene",
  "filesystem_sweep": {
    "pycache_dirs_removed": 5,
    "pyc_files_removed": 0,
    "pyo_files_removed": 0,
    "pycache_dirs_removed_sample": [
      "/app/backend/__pycache__",
      "/app/backend/utils/__pycache__",
      "/app/backend/data/__pycache__",
      "/app/backend/game_logic/__pycache__",
      "/app/backend/routes/__pycache__"
    ]
  },
  "git_index_audit": {
    "initial_tracked_pycache": 0,
    "initial_tracked_pyc_or_pyo": 0,
    "untracked_via_git_rm_cached": 0,
    "still_tracked_after_sweep": 0
  },
  "clean": true
}
```

### 3.6 Riepilogo `run_pre_qa_safety_validator_suite.py`
```
[✓] PASS  Validator 113 HomeOverflow
[✓] PASS  Smoke 113 HomeOverflow
[✓] PASS  Validator 114 Home Routes
[✓] PASS  Smoke 114 Home Routes
[✓] PASS  Rollup 114 Home Routes
[✓] PASS  Validator 114B Gacha/Combat/Lobby Guard
[✓] PASS  Validator 115A P0 Hard Gates
[✓] PASS  Smoke 115A P0 Hard Gates
[✓] PASS  Validator 115B Progression/Forge/Items
[✓] PASS  Smoke 115B Progression/Forge/Items
[✓] PASS  Validator 115C Auth/Server Scope
[✓] PASS  Validator 115D Screen-Entry/Deeplink Guard
[✓] PASS  Validator 115E Combat/Tower Legacy Hardening
[✓] PASS  Validator 115F Repo Hygiene & Validator Truth
[✓] PASS  Validator 115G Skill/Artifact Semantic Cleanup
[✓] PASS  Validator 116A Battle Power Foundation
[✓] PASS  Validator 116A-EXT Hero Card Power + Bible Source Map
[✓] PASS  Validator 116A-EXT FIX-A Team Power Source Truth
[✓] PASS  Validator 116B Chat/Bot Quality + Legacy Chat Cleanup
[✓] PASS  Validator 116C Red Dot Notification Badge Foundation

totali:  20  | PASS: 20  | FAIL: 0  | SKIPPED: 0
backend_up: True
verdict: PRE_QA_SAFETY_SUITE_PASS
```
File: `backend/reports/pre_qa_safety_validator_suite_20260614T151805Z.json`
+ pointer `backend/reports/pre_qa_safety_validator_suite_latest.json`.

---

## 4. Runtime curl evidence (backend UP)

### 4.1 `GET /api/red-dot/metadata` (no auth) — **HTTP 200**
```json
{
  "status": "ok",
  "red_dot_summary_version": "red_dot_v1_preqa_read_only_foundation",
  "source_map_path": "data/design/red_dot/red_dot_notification_badge_source_map_v1.json",
  "no_db_writes": true,
  "no_claim_activation": true,
  "no_read_all": true,
  "no_push_notification": true,
  "no_toast": true,
  "server_scoped": true,
  "max_count_display_cap": 99
}
```

### 4.2 `GET /api/red-dot/summary` SENZA `server_id` (auth) — **HTTP 400**
```json
{
  "detail": {
    "code": "SERVER_ID_REQUIRED",
    "message": "Red Dot summary e' server-scoped. Fornire server_id esplicito; nessun silent s1 fallback.",
    "no_silent_s1_fallback": true,
    "red_dot_summary_version": "red_dot_v1_preqa_read_only_foundation",
    "source_map_path": "data/design/red_dot/red_dot_notification_badge_source_map_v1.json",
    "no_db_writes": true,
    "no_claim_activation": true,
    "no_read_all": true,
    "no_push_notification": true,
    "no_toast": true,
    "server_scoped": true,
    "max_count_display_cap": 99
  }
}
```

### 4.3 `GET /api/red-dot/summary?server_id=s1` (auth) — **HTTP 200**
```json
{
  "status": "ok",
  "server_id": "s1",
  "red_dot_summary_version": "red_dot_v1_preqa_read_only_foundation",
  "no_db_writes": true,
  "no_claim_activation": true,
  "no_read_all": true,
  "no_push_notification": true,
  "no_toast": true,
  "server_scoped": true,
  "max_count_display_cap": 99,
  "psp_present_for_server": false,
  "sources": [
    {
      "source_id": "server_profile_required",
      "has_dot": true,
      "count": 0,
      "severity": "warning",
      "reason": "PLAYER_SERVER_PROFILE_REQUIRED",
      "route": "/home",
      "locked_by_pre_qa": false,
      "actionable_now": false
    }
  ],
  "by_screen": {
    "/home": {
      "has_dot": true,
      "count": 0,
      "severity": "warning",
      "reason": "PLAYER_SERVER_PROFILE_REQUIRED",
      "route": "/home",
      "locked_by_pre_qa": false,
      "actionable_now": false
    }
  },
  "home_total": {
    "has_dot": true,
    "count": 0,
    "severity": "warning",
    "reason": null,
    "route": "/home",
    "locked_by_pre_qa": false,
    "actionable_now": false
  },
  "active_sources_count": 1
}
```

> Per un utente neo-registrato (no PSP) il summary mostra un **dot di warning**
> di tipo `server_profile_required` aggregato al nodo `/home`. Nessuna azione
> automatica. Il dot è puramente informativo.

---

## 5. Mappatura sorgenti red-dot (14 obbligatorie + extra design)

### Attive in 116C (read-only safe)
| source_id | route | severity | Logica |
|-----------|-------|----------|--------|
| `server_profile_required` | `/home` | warning | PSP mancante per (uid, server_id) |
| `team_missing_warning` | `/battle` | info | Derivato da `/api/battle-power/summary` (team_missing=true) |

### Deferred (resolver futuro richiesto)
`mail_unread`, `daily_login_claimable`, `daily_quest_claimable`, `achievements_claimable`,
`battle_pass_claimable`, `events_active_claimable`, `shop_free_claim`, `gacha_free_summon_or_ticket`,
`hero_upgrade_available`, `gear_rune_artifact_divine_alert`

### Locked by Pack 116B (chat/dm)
`chat_pre_qa_locked`, `dm_pre_qa_locked` — mai dot actionable mentre locked.

### Future
`guild_messages_or_war`

### Unknown — pending Game Master / Character Bible
`vip_or_subscription_alert`

---

## 6. Igiene git (commit policy rispettata)

- Pre-commit: `python3 backend/scripts/sweep_repo_hygiene.py` → `clean=true`, 0 file bytecode tracciati.
- `git add` esplicito per ciascun file (mai `git add -A` / `git add .`).
- Lista esatta dei file aggiunti documentata nel commit message.

---

## 7. Verdetto finale

# `PRE_QA_STABILIZATION_116C_RED_DOT_NOTIFICATION_BADGE_FOUNDATION_READY_FOR_GAME_MASTER_REAUDIT`

- ✅ Foundation read-only/server-scoped completata
- ✅ 14 sorgenti red-dot mappate (2 attive safe + deferred + locked + future + unknown)
- ✅ Backend route GET-only con `SERVER_ID_REQUIRED` enforcement
- ✅ Frontend hook GET-only + componente puramente visuale
- ✅ 20/20 validator suite **PASS** (0 FAIL, 0 SKIPPED, backend_up=True)
- ✅ Pack 116A/EXT/FIX-A e Pack 116B preservati senza regressioni
- ✅ Repo hygiene: nessun bytecode tracciato

**Stop. In attesa di re-audit Game Master prima di procedere a 117+.**
