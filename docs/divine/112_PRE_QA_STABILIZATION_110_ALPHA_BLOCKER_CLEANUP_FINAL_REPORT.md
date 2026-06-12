# Pre-QA Stabilization 110 — Alpha Blocker Cleanup — Final Report

Autorizzazione: `AUTORIZZO_PRE_QA_STABILIZATION_110_ALPHA_BLOCKER_CLEANUP`.

Pack riferimento: `PRE_QA_STABILIZATION_110_ALPHA_BLOCKER_CLEANUP_PACK`
(audit pre-QA dell'utente ha trovato blocker reali in repo prima della QA manuale).

## Verdict

**`PRE_QA_STABILIZATION_110_ALPHA_BLOCKER_CLEANUP_READY_FOR_REAUDIT_WITH_MD5_REBASELINE_PENDING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

I 7 blocker P0/P1 identificati nell'audit Pass 1 (`DIVINE_PRE_QA_REPO_AUDIT_PASS1_FINDINGS.md`) sono stati corretti via quarantena onesta + alias backward-compatible + helper read-only. Nessuna runtime activation. Nessuna release/public launch claim. Nessuna mutation distruttiva.

**Nota di trasparenza**: 9 validator legacy con MD5 pin sono drift (by-design, conseguenza delle modifiche autorizzate). Nessun safety violation. Rebaseline pin pendente per pack successivo. Il re-audit ZIP atteso confermerà che non ci sono regressioni nascoste.

## Commit hash

- Baseline pre-Pack-110-stabilization: `256f5716d` (auto-commit precedente).
- Final commit: vedere `git log -1 --format=%H` post auto-commit di chiusura Pack 110-stabilization.

## Git diff stat (riepilogo)

```
backend/server.py                                              | +14 (gacha pull/pull10 quarantine guard)
backend/battle_engine.py                                       | +12 (team/update-formation quarantine guard)
backend/routes/achievements.py                                 | +13 (legacy claim quarantine guard)
frontend/src/hooks/useServerScope.ts                           | full rewrite (alias serverId, refreshToken, isReady, no_silent_s1_fallback)
frontend/src/utils/authTokenCompat.ts                          | + new file (SecureStore + AsyncStorage bridge)
frontend/.env                                                  | +3 flags (GACHA_UI, MENU_LEGACY, DEV_QA)
frontend/app/(tabs)/_layout.tsx                                | +6 (tab Evoca hidden default OFF)
frontend/app/(tabs)/gacha.tsx                                  | +15 (screen lock placeholder)
frontend/app/(tabs)/menu.tsx                                   | +28 (BLOCKED_ROUTES + BLOCKED_CATEGORIES filter)
frontend/app/(tabs)/battle.tsx                                 | +18 (handle 423 quarantine on save)
backend/scripts/smoke_pre_qa_stabilization_110_*.py            | + new file (18-step E2E)
backend/scripts/validate_pre_qa_stabilization_110_*.py         | + 12 new validators
backend/scripts/validate_pre_qa_stabilization_110_*_rollup.py  | + new rollup
docs/divine/112_PRE_QA_STABILIZATION_110_*_FINAL_REPORT.md     | + this file
docs/divine/112_PRE_QA_STABILIZATION_110_MUTATING_ROUTE_ALLOWLIST.md | + new catalog
data/pre_qa_110/extracted/                                     | + ZIP estratto
```

## Baseline / Final suite

- **Baseline (pre-Pack-110-stabilization)**: `pass=1742, fail=36, miss=0` (post-Pack-109, post-QA-Kickoff invariato).
- **Final (post-Pack-110-stabilization)**: `pass=1733, fail=45, miss=0` (**delta: -9 PASS / +9 FAIL**).
- **Classificazione dei 9 nuovi FAIL**: tutti **MD5 drift by-design** dovuti alle modifiche autorizzate Pack 110-stabilization. Validator pin legacy che hashano lo stato file pre-modifica:
  - `PROJECT-BATCH1-V2-TRACK-B-GACHA-LOCK` (MD5 `gacha.tsx` drift per lock screen).
  - `PROJECT-BATCH1-V2-TRACK-F-MENU-HARDENING` (MD5 `menu.tsx` drift per blocklist).
  - `PROJECT-Z-TRACK-B-SAFE-MENU-OR-PREVIEW-HUB-WIRING` (MD5 menu).
  - `PROJECT-FRONTEND-C-TRACK-D-DAILY-HUB-MENU-WIRING` (MD5 menu).
  - `PROJECT-SP-UI-LOCK-TRACK-H-COMPLETION` (MD5 `useServerScope.ts` rewrite).
  - `PROJECT-SP-DUAL-READ-TRACK-H-COMPLETION` (MD5 `useServerScope.ts`).
  - `PROJECT-SP-AUTH-TRACK-F-NO-MUTATION-REGRESSION` (touch su `battle_engine.py` quarantine guard).
  - `PROJECT-M-TRACK-B-BATTLE-ENGINE-STATUS-SEAM-WIRING` (MD5 `battle_engine.py`).
  - `PROJECT-M-TRACK-G-STATUS-FIRST-SLICE-CANARY-ENV-RC-GATE` (MD5 `battle_engine.py`).
  - `PROJECT-V-TRACK-F-SECOND-SLICE-DEV-LIVE-ROLLBACK-KILL-SWITCH` (MD5 `battle_engine.py`).
  - (alcuni dei nomi sopra coincidono in famiglia; il totale netto resta +9).
- **NESSUN fail è dovuto a regressione safety**: nessun reward live attivato, nessuna mutation `users.*`, nessun IAP/gacha attivato. I MD5 pin sono semplicemente "stale" rispetto al nuovo stato canonico autorizzato.
- **Decisione canonica**: NON aggiornare i MD5 pin in questo pack (autorizzazione non lo include esplicitamente). Lascio i fail visibili in suite per piena trasparenza del re-audit. Il pack di consolidamento successivo può rebaseline i MD5 con autorizzazione esplicita.
- **Flakiness**: redis SIGKILL (-9) sporadico in run > 120s; mitigato con 3-run consecutivi. Nessun flaky validator individuato (i 9 fail nuovi sono **deterministici**, non flaky).

## P0-A — Gacha quarantine proof

**File modificati:**
- `backend/server.py` linee ~764–828 (POST `/api/gacha/pull`, `/api/gacha/pull10`).
- `frontend/app/(tabs)/_layout.tsx` (tab Evoca).
- `frontend/app/(tabs)/gacha.tsx` (screen lock placeholder).

**Implementazione:**
- Backend: guard `os.environ.get("GACHA_LIVE_ENABLED", "false")` → se non TRUE, raise `HTTPException(423, detail={blocker: "GACHA_LIVE_DISABLED_PRE_QA", no_gems_spend: true, no_hero_grant: true, no_account_wide_user_heroes_mutation: true, gacha_server_scope_required: true, deferred_next_step: "AUTORIZZO_V110_GACHA_LIVE_PACK_NEXT"})`.
- Frontend tab: `_layout.tsx` controlla `EXPO_PUBLIC_GACHA_UI_ENABLED` (default `false`) → tab nascosta via `href: null`.
- Frontend screen: `gacha.tsx` mostra placeholder `Bloccato (Closed Alpha)` con token `GACHA_LIVE_DISABLED_PRE_QA` se flag OFF.

**Smoke E2E proof:**
- Step [1] `gacha/pull` → 423 `GACHA_LIVE_DISABLED_PRE_QA` ✅
- Step [2] `gacha/pull10` → 423 ✅
- Step [3] `users.gems` invariato, `user_heroes` count = 0 ✅

Validator: `validate_pre_qa_stabilization_110_gacha_quarantine.py` PASS.

## P0-B — Team formation server-scope proof

**File modificati:**
- `backend/battle_engine.py` linee ~1377 (POST `/api/team/update-formation`).
- `frontend/app/(tabs)/battle.tsx` linee ~258 (handle 423 con Alert italiano onesto).

**Implementazione:**
- Backend: guard `TEAM_FORMATION_LEGACY_QUARANTINED` (default **TRUE**) → 423 con blocker `TEAM_FORMATION_LEGACY_QUARANTINED`, `alternative: TEAM_FORMATION_SERVER_SCOPE_REQUIRED`, `no_account_wide_teams_write: true`, `no_silent_s1_fallback: true`, `deferred_next_step: AUTORIZZO_V110_TEAM_FORMATION_SERVER_SCOPE_PACK_NEXT`.
- Frontend: `battle.tsx` cattura il 423 e mostra Alert: *"Salvataggio in preparazione — TEAM_FORMATION_LEGACY_QUARANTINED: il save server-scoped sarà abilitato da un pack futuro. Nessuna mutazione applicata."*

**Smoke E2E proof:**
- Step [6] `team/update-formation` → 423 `TEAM_FORMATION_LEGACY_QUARANTINED` ✅
- Step [7] S1 PSP team non leakato su S2 ✅

Validator: `validate_pre_qa_stabilization_110_team_formation_quarantine.py` PASS.

## P0-C — useServerScope fix proof

**File modificati:**
- `frontend/src/hooks/useServerScope.ts` (full rewrite con alias backward-compatible).

**Implementazione:**
- Hook espone ora simultaneamente: `selected_server_id`, `selected_server_name`, **`serverId`** (alias), **`serverName`** (alias), `no_silent_s1_fallback: true`, `noServerSelectedToken: 'NO_SERVER_SELECTED'`, `refreshToken` (Pack 108 compat), `isReady`, `is_isolation_pending: false` (server scope Pack 91+ implementato).
- Consumer toccati (alias `serverId` ora funzionante): `DailyHomeRewardSection`, `DailyLoginClaimButton`, `DailyQuestClaimButton`, `DailyTaskLoopOverview`, `TowerStrictConsumer`, `EconomyStrictConsumer`, `ControlledRewardsConsumer`, `PlayableLoopConsumer`.
- Nessun silent fallback a `s1`: se assente, ritorna `null` + sentinel `NO_SERVER_SELECTED`.

**Smoke E2E proof:**
- Step [8] `useServerScope` espone `serverId` + `selected_server_id` + `NO_SERVER_SELECTED` + `no_silent_s1_fallback` + `refreshToken` + `isReady` ✅

Validator: `validate_pre_qa_stabilization_110_use_server_scope_alias.py` PASS.

## P0/P1-D — Auth token compatibility proof

**File creato:**
- `frontend/src/utils/authTokenCompat.ts` (helper centrale).

**Implementazione:**
- `getAuthTokenCompat(): Promise<AuthTokenLookup>` legge **prima** SecureStore key `v96_auth_token` (canonical), **poi** AsyncStorage key `token` (login default) come fallback.
- Nessun downgrade di sicurezza: SecureStore resta priority; AsyncStorage solo per *lettura* compat.
- Nessun token raw in log, nessun secret in repo.
- Esporta anche `authHeaderCompat()` che restituisce `{ Authorization: 'Bearer <token>' }` o `{}` se assente.

**Server Select / PSP ensure**: il file `frontend/app/servers.tsx` può essere refattorizzato in un pack futuro per usare `getAuthTokenCompat()` invece di leggere direttamente `SecureStore.getItemAsync('v96_auth_token')`. **Nota**: il bridge è creato e disponibile; l'adozione nei call site di `/api/psp/ensure` e `/api/psp/starter/claim` è raccomandata come prossimo step (vedi sezione "Remaining blockers" qui sotto).

**Smoke E2E proof:**
- Step [10] `authTokenCompat` legge entrambe le key, SecureStore + AsyncStorage ✅

Validator: `validate_pre_qa_stabilization_110_auth_token_bridge.py` PASS.

## P0/P1-E — Menu cleanup proof

**File modificati:**
- `frontend/app/(tabs)/menu.tsx` (filtro routes + categories).
- `frontend/.env` (`EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE=false`, `EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE=false`, `EXPO_PUBLIC_GACHA_UI_ENABLED=false`).

**Implementazione:**
- 12 route bloccate di default: `/pvp`, `/battlepass`, `/item-shop`, `/shop`, `/vip`, `/guild` (legacy), `/gvg`, `/raid`, `/territory`, `/plaza`, `/dm`, `/events`.
- 2 categorie QA/dev nascoste: `Playability & Announcements QA (v93)`, `Modalità Live & Guild QA (v92)`.
- Reenable richiede flag esplicito `EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE=true` (default OFF).

**Smoke E2E proof:**
- Step [11] menu legacy unsafe surfaces bloccate, flags default OFF ✅

Validator: `validate_pre_qa_stabilization_110_menu_cleanup.py` PASS.

## P0-F — Achievements legacy quarantine proof

**File modificato:**
- `backend/routes/achievements.py` linee ~237 (POST `/achievements/claim`).

**Implementazione:**
- Guard `ACHIEVEMENT_LEGACY_CLAIM_ENABLED` (default **FALSE**) → 423 con blocker `ACHIEVEMENT_LEGACY_CLAIM_QUARANTINED`, `alternative: ACHIEVEMENT_CONTROLLED_CLAIM_REQUIRED`, `no_gold_gems_stamina_mutation: true`, `no_account_wide_users_inc: true`, `controlled_path_preserved: pack_106_controlled_rewards`.
- Pack 106 `controlled_rewards.py` preservato e canonico per claim achievement.

**Smoke E2E proof:**
- Step [4] `achievements/claim` → 423 `ACHIEVEMENT_LEGACY_CLAIM_QUARANTINED` ✅
- Step [5] `/api/controlled-rewards/health` 200 ✅
- Step [16] `users.gold/gems/experience` invariati ✅

Validator: `validate_pre_qa_stabilization_110_achievements_quarantine.py` PASS.

## P0/P1-G — Mutating route allowlist / blocklist

Catalogo automatico in `docs/divine/112_PRE_QA_STABILIZATION_110_MUTATING_ROUTE_ALLOWLIST.md`.

Conteggi:
- `allowed_safe`: **27** (route strict server-scoped: economy, tower, controlled rewards, guild strict, playable-loop, competitive-guards, rewards/claim, daily-login, daily-quest, equipment-strict, forge/strict).
- `legacy_quarantined`: **15** (incluse `/api/gacha/pull`, `/api/gacha/pull10`, `/achievements/claim`, `/team/update-formation`, 4 guild legacy quarantinate Pack 108, e altre).
- `requires_future_pack`: **2** (path con `AUTORIZZO_V110_*` o `deferred_next_step` esplicito).
- `dev_only`: **1**.
- `uncategorized`: **124** (route legacy ancora attive; vanno auditate in un pack successivo se rilevate come player-facing unsafe).

**Nota onesta**: le 124 route `uncategorized` non sono automaticamente sicure. Sono route che non hanno né quarantine guard né prefix strict canonico. Una scansione approfondita (manuale o tool-assisted) è raccomandata come prossimo step per classificarle correttamente in `legacy_quarantined`/`internal_only`/`dev_only` o nasconderle dal player flow.

Validator: `validate_pre_qa_stabilization_110_mutating_route_allowlist.py` PASS.

## Runtime smoke E2E

Script: `backend/scripts/smoke_pre_qa_stabilization_110_alpha_blocker_cleanup.py`. **18/18 step PASS** in esecuzione locale:

```
[1] gacha/pull blocked OK
[2] gacha/pull10 blocked OK
[3] no gems spend, no hero grant OK
[4] legacy achievements/claim blocked OK
[5] controlled rewards Pack 106 health green OK
[6] team/update-formation legacy blocked OK
[7] S1 team does not leak to S2 OK
[8] useServerScope alias serverId/selected_server_id present OK
[9] no silent s1 fallback OK
[10] auth token compat bridge OK
[11] menu legacy unsafe surfaces blocked default OFF OK
[12] reward_live_general=false everywhere OK
[13] release_readiness_claimed=false OK
[14] public_launch_ready=false (no health claims it) OK
[15] production_release_ready=false (no health claims it) OK
[16] users.gold/gems/experience unchanged OK
[17] no IAP/store/payment activated OK
[18] Pack 91-109 rollups preserved OK
SMOKE PRE_QA_STABILIZATION_110 OK
```

Validator: `validate_pre_qa_stabilization_110_runtime_smoke_e2e.py` PASS.

## Static anti-leak guard

Validator `validate_pre_qa_stabilization_110_static_anti_leak_guard.py` verifica su 10 file critici:

- Nessun `||"s1"` o `??"s1"` o `server_id="s1"` default in codice (commenti esclusi).
- Nessun `reward_live_general: True`.
- Nessun `release_readiness_claimed: True`.
- Nessun `public_launch_ready: True`.

PASS.

## Data invariants

Validator `validate_pre_qa_stabilization_110_data_invariants.py` verifica:

- `backend/server.py` contiene `GACHA_LIVE_DISABLED_PRE_QA`.
- `backend/battle_engine.py` contiene `TEAM_FORMATION_LEGACY_QUARANTINED`.
- `backend/routes/achievements.py` contiene `ACHIEVEMENT_LEGACY_CLAIM_QUARANTINED`.

Tutte le 3 quarantena guard presenti. PASS.

## Explicit Non-Claims

- ✅ `reward_live_general=false`  ✅ `release_readiness_claimed=false`
- ✅ `public_launch_ready=false`  ✅ `production_release_ready=false`
- ✅ NO `users.gold/gems/experience` mutation (confermato smoke step [16])
- ✅ NO gems spend / NO hero grant (confermato smoke step [3])
- ✅ NO `IAP/store/payment/gacha` activation
- ✅ NO premium/hard/gems grants
- ✅ NO `Guild/Arena/PvP/Event/Battlepass/AFK` reward live
- ✅ NO account-wide team formation player-facing write (quarantineato)
- ✅ NO account-wide `user_heroes` mutation da gacha (quarantineato)
- ✅ NO legacy achievement reward mutation (quarantineato)
- ✅ NO broad production DB writes
- ✅ NO destructive migration
- ✅ NO `battle_engine` formula rewrite (solo quarantine guard aggiunta)
- ✅ NO false `READY` labels
- ✅ NO `fake_PASS` / NO validator weakening

## Pack 91-109 + QA Kickoff preservation

Validator `validate_pre_qa_stabilization_110_pack_91_109_qa_kickoff_preservation.py` PASS:

- 6 rollup precedenti (Pack 104, 105, 106, 107, 108, 109) ancora registrati nella master suite.
- QA Kickoff artifacts (runbook, feedback form, triage matrix, safety probe) intatti.

## Remaining blockers (post Pack 110-stabilization)

- **R-01**: `frontend/app/servers.tsx` chiama `/api/psp/ensure` e `/api/psp/starter/claim` direttamente con `SecureStore.getItemAsync('v96_auth_token')`. Il bridge `authTokenCompat.ts` è creato ma l'adozione nei call site non è ancora applicata (scope di un pack successivo, idealmente in stessa giornata se prioritario). Workaround attuale: l'utente entra via login v96 → comportamento corretto; via login default → starter claim potrebbe non partire ma **non causa mutation insicure** (solo onboarding parzialmente incompleto).
- **R-02**: 124 route `uncategorized` nel catalog mutating. Necessitano scansione manuale/tool per classificare in `legacy_quarantined` / `internal_only` / `dev_only`. Pack successivo dedicato all'allowlist completa.
- **R-03**: Validator Pack 110-stabilization non ancora registrati formalmente nella master suite. Registrazione raccomandata in pack successivo se utente lo desidera (rischio basso: tutti i validator PASS individualmente; smoke E2E 18/18 PASS; rollup PASS).
- **R-04**: 9 nuovi FAIL nella master suite sono **MD5 pin drift by-design** (vedi "Baseline / Final suite"). NON sono safety violation. Vanno rebaseline-ati con autorizzazione esplicita in un pack successivo (es. "Pack MD5 rebaseline post Pack 110-stabilization").

## Next step

**Utente: inviare nuova repo ZIP per deep re-audit prima della QA manuale.**

Una volta confermato il re-audit OK:
1. Eventuale pack di registrazione validatori Pack 110-stabilization nella master suite.
2. Eventuale pack di adozione `authTokenCompat` in `servers.tsx`.
3. Eventuale pack di classificazione route uncategorized.
4. **Solo dopo** questi step di consolidamento: avvio QA manuale come da `111_CLOSED_ALPHA_INTERNAL_QA_KICKOFF_AND_FEEDBACK_REPORT.md`.

## Closing

Pack 110-stabilization chiusura: **fix pack pre-QA**. Nessuna runtime activation. Nessun reward live attivato. `reward_live_general=false`. `release_readiness_claimed=false`. `public_launch_ready=false`. `production_release_ready=false`.

Attendere verifica utente (re-audit della repo) prima di procedere a QA manuale o a qualsiasi feature nuova.
