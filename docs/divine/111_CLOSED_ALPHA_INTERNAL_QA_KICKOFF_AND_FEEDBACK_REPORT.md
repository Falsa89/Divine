# Closed Alpha Internal QA Kickoff and Feedback Report

Autorizzazione: `AUTORIZZO_CLOSED_ALPHA_INTERNAL_QA_KICKOFF_NO_RUNTIME_ACTIVATION`.

Pack riferimento: **Closed Alpha Internal QA Kickoff and Feedback Intake Runbook**
(docs-only / read-only helpers, no runtime feature activation).

## 0. Stato di questo report

Questo documento contiene **due livelli**:

1. **Kickoff readiness** (compilato — verificato lato infrastruttura): conferma
   che gli artefatti del runbook QA sono pronti, il probe di safety invariants
   ritorna verde, e gli endpoint backend health sono coerenti col Pack 109
   `CLOSED_ALPHA_CONDITIONAL_READY`.
2. **Tester intake results** (placeholder — da popolare quando i tester reali
   completano le sessioni): tabelle `tester/device matrix`, `bug triage`,
   `screenshots/videos`, `sections A-O results`.

Nessun tester ha ancora completato sessioni reali al momento della
generazione di questo report (intake aperto). Le tabelle tester sono lasciate
come **template strutturati** pronti per essere compilati dal coordinatore QA
una volta ricevute le compilazioni `qa_tester_feedback_form.md`.

## 1. Verdict di kickoff (infrastruttura)

`CLOSED_ALPHA_INTERNAL_QA_KICKOFF_INFRASTRUCTURE_READY_WAITING_TESTER_INTAKE`

Sub-verdict:
- Backend health: **READY** (10/10 endpoint verdi, `reward_live_general=false`, `release_readiness_claimed=false`).
- Playable loop map: **READY** (S1 + S2 entrambi `surfaces=11`, `false_ready=[]`).
- Safety invariants probe: **`SAFE_INVARIANTS_OK`**.
- Mobile QA Checklist Pack 109: presente.
- Tester Runbook (italiano): presente.
- Feedback Form Template: presente.
- Bug Triage Matrix Template: presente.

## 2. Test window

- Apertura kickoff: **al momento di generazione di questo report** (commit di apertura: vedi sezione "Build / source commit").
- Durata pianificata raccolta feedback: **fino alla decisione di chiusura dell'utente** (NON viene definita una data automatica; il coordinatore QA decide quando consolidare la triage e chiudere il ciclo).
- Sessione tester individuale consigliata: **30\u201345 minuti**.

## 3. Build / source commit

- Backend/Frontend source commit baseline: cfr. `git log -1 --format=%H` post-auto-commit di Pack 109 (verdict `CLOSED_ALPHA_CONDITIONAL_READY`).
- Container locale: `LOCAL_CONTAINER_PUBLIC_SYNC_PENDING` (vedi Pack 109 verdict line).
- Build mobile: Expo Go bundle Metro via preview URL Pack 109. Development build NON richiesta per i flussi in scope.

## 4. Pack 109 gate reference

`MEGA_RELEASE_ACCELERATION_109_CLOSED_ALPHA_RC_SWEEP_CONDITIONAL_READY_WITH_DEFERRED_BLOCKERS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Gate canonico: `CLOSED_ALPHA_CONDITIONAL_READY`.

Report sorgente: `docs/divine/110_CLOSED_ALPHA_RC_SWEEP_RELEASE_GATE_FINAL_REPORT.md`.

## 5. Tester / device matrix (placeholder)

> Il coordinatore QA deve compilare questa tabella ricevendo i feedback form.

| Tester ID | Ruolo | Device | OS / version | Server testato | Account | Sessione (min) | Feedback ricevuto |
|-----------|-------|--------|--------------|----------------|---------|----------------|--------------------|
| T-001     |       |        |              |                | fresh   |                | \u23f3                |
| T-002     |       |        |              |                | fresh   |                | \u23f3                |
| T-003     |       |        |              | S1\u2192S2\u2192S1     | returning|               | \u23f3                |
| T-004     |       |        |              |                |         |                | \u23f3                |
| T-005     |       |        |              |                |         |                | \u23f3                |

Target minimo: **5 tester totali**, di cui **\u22652 Android**, **\u22652 iOS** (se
disponibili, altrimenti documentare *iOS unavailable*), **\u22651 device
medio-basso**, **\u22651 fresh**, **\u22651 returning**, **\u22651 server switch
S1\u2192S2\u2192S1**.

## 6. Sezioni A\u2013O \u2014 risultati

> Stato corrente: i risultati infrastrutturali (probe + smoke automatico Pack 109)
> sono `OK`. I risultati tester reali sono in attesa di intake.

### A \u2014 Install / startup
- Infrastruttura: bundle Metro disponibile via preview Pack 109; nessun crash riscontrato in automazione.
- Tester reali: `\u23f3 in attesa`.

### B \u2014 Auth / logout
- Infrastruttura: `AuthContext.tsx` espone `login`/`logout`; nessun fallback silenzioso a server di default.
- Tester reali: `\u23f3 in attesa`.

### C \u2014 Server selection / server switch
- Infrastruttura: `useServerSwitchRefreshGuard` invalida cache su switch; `buildPlayableLoopCacheKey(null)` ritorna `NO_SERVER_SELECTED`; probe conferma server map distinta S1 vs S2.
- Tester reali: `\u23f3 in attesa`.

### D \u2014 Home / Lobby / navigation
- Infrastruttura: 11 surface playable loop su S1 e S2 con `false_ready=[]`; copy italiana canonica.
- Tester reali: `\u23f3 in attesa`.

### E \u2014 Story / battle preview / staging
- Infrastruttura: nessuna route Pack 104\u2013108 importa `battle_engine` o chiama `/api/battle/simulate` live (validator dedicato PASS).
- Tester reali: `\u23f3 in attesa`.

### F \u2014 Tower strict loop
- Infrastruttura: `/api/tower/strict/health` 200; `TOWER_STRICT_PREFLIGHT_ENABLED=OFF`.
- Tester reali: `\u23f3 in attesa`.

### G \u2014 Daily login / Daily quest
- Infrastruttura: `/api/daily-login/claim/health`, `/api/daily-quest/claim/health`, `/api/daily-quest/tracker/health` tutti 200; kill switch `DAILY_LOGIN_CLAIM_ENABLED=OFF` di default.
- Tester reali: `\u23f3 in attesa`.

### H \u2014 Controlled rewards
- Infrastruttura: `/api/controlled-rewards/health` 200; `reward_live_general=false`.
- Tester reali: `\u23f3 in attesa`.

### I \u2014 Economy strict (shop / soul / equipment / forge / fusion)
- Infrastruttura: `/api/economy/strict/health` 200; nessun `$inc` su `users.gold/gems/experience`.
- Tester reali: `\u23f3 in attesa`.

### J \u2014 Inventory / Equipment / Material scope
- Infrastruttura: `player_server_profiles` chiave composita `(user_id, server_id)`; Pack 105 PSP material ledger PRESERVED.
- Tester reali: `\u23f3 in attesa`.

### K \u2014 Guild strict / legacy quarantine
- Infrastruttura: 5 endpoint strict server-scoped; 4 route legacy mutanti quarantineate (HTTP 423 `GUILD_LEGACY_QUARANTINED`).
- Tester reali: `\u23f3 in attesa`.

### L \u2014 Arena / PvP / Event \u2014 locked/deferred state
- Infrastruttura: tutti i preflight `READY_GATED_REWARDS_DEFERRED`; blocker canonici esposti.
- Tester reali: `\u23f3 in attesa`.

### M \u2014 Performance / loading / crash / memory
- Infrastruttura: backend stabile, supervisor `RUNNING`; bundle Metro responsive.
- Tester reali: `\u23f3 in attesa`.

### N \u2014 UI / UX mobile readability
- Infrastruttura: copy italiana canonica in `playableLoopFlags.ts` (`PLAYABLE_LOOP_STATUS_COPY`); helper `isFalseReadyClaim` presente.
- Tester reali: `\u23f3 in attesa`.

### O \u2014 Safety invariants
- Infrastruttura: probe `qa_safety_invariants_probe.py` ritorna `SAFE_INVARIANTS_OK`.
- Backend env: `REWARD_LIVE_GENERAL`, `GUILD_REWARD_LIVE_ENABLED`, `ARENA_REWARD_LIVE_ENABLED`, `PVP_REWARD_LIVE_ENABLED`, `EVENT_REWARD_LIVE_ENABLED`, `BATTLEPASS_REWARD_LIVE_ENABLED`, `AFK_REWARD_LIVE_ENABLED`, `DAILY_LOGIN_CLAIM_ENABLED` \u2192 tutti **absent (=default OFF)**.
- Tester reali: `\u23f3 in attesa`.

## 7. P0 / P1 / P2 / P3 issue table

> Coordinatore QA: popola dalle compilazioni `qa_tester_feedback_form.md`.
> Stato attuale: **0 bug segnalati** (intake aperto).

| ID     | Severity | Sezione | Area | Title | Tester | Device | OS | Repro steps | Expected | Actual | Owner | Status | Pack target |
|--------|----------|---------|------|-------|--------|--------|-----|-------------|----------|--------|-------|--------|-------------|
| \u2014      | \u2014        | \u2014       | \u2014    | \u2014     | \u2014      | \u2014      | \u2014   | \u2014           | \u2014        | \u2014      | \u2014     | \u2014      | \u2014           |

## 8. Screenshots / videos requested list

I tester sono pregati di allegare screenshot/video per **ogni bug** segnalato.
Lista minima screenshot richiesti:

- [ ] Schermata Login (post-splash).
- [ ] Selezione server (S1/S2 visible).
- [ ] Home dopo selezione server.
- [ ] Playable loop map (se UI flag attivo via tester-only build).
- [ ] Tentativo legacy `POST /api/guild/create` (errore 423 atteso).
- [ ] Lobby + qualsiasi surface `Bloccato (Closed Alpha)` o `In preparazione (deferred)`.
- [ ] Eventuali crash (log Expo Go o devtools).
- [ ] Eventuale popup IAP/gacha/payment (NON dovrebbe apparire \u2192 P0 se appare).

## 9. Safety invariant confirmation (kickoff)

Risultato `qa_safety_invariants_probe.py` (eseguito all'apertura kickoff):

```
=== Closed Alpha QA Safety Invariants Probe (READ-ONLY) ===

Health endpoint safety statements (10/10 OK):
  /tower/strict/health          status=200 rlg=False rrc=False \u2192 OK
  /economy/strict/health        status=200 rlg=False rrc=False \u2192 OK
  /controlled-rewards/health    status=200 rlg=False rrc=False \u2192 OK
  /guild/strict/health          status=200 rlg=False rrc=False \u2192 OK
  /playable-loop/health         status=200 rlg=False rrc=False \u2192 OK
  /competitive-guards/health    status=200 rlg=False rrc=False \u2192 OK
  /rewards/claim/health         status=200 rlg=False rrc=False \u2192 OK
  /daily-login/claim/health     status=200 rlg=False rrc=False \u2192 OK
  /daily-quest/claim/health     status=200 rlg=False rrc=False \u2192 OK
  /daily-quest/tracker/health   status=200 rlg=False rrc=False \u2192 OK

Playable loop map (server_id=s1, server_id=s2):
  server_id=s1: surfaces=11 false_ready=[] rrc=False
  server_id=s2: surfaces=11 false_ready=[] rrc=False

backend/.env reward live flags (all absent = default OFF):
  REWARD_LIVE_GENERAL, GUILD_REWARD_LIVE_ENABLED, ARENA_REWARD_LIVE_ENABLED,
  PVP_REWARD_LIVE_ENABLED, EVENT_REWARD_LIVE_ENABLED, BATTLEPASS_REWARD_LIVE_ENABLED,
  AFK_REWARD_LIVE_ENABLED, DAILY_LOGIN_CLAIM_ENABLED

=== VERDICT: SAFE_INVARIANTS_OK ===
```

Explicit non-claim:

- `reward_live_general=false` \u2705
- `release_readiness_claimed=false` \u2705
- `public_launch_ready=false` \u2705
- `production_release_ready=false` \u2705
- Nessun grant `users.gold/gems/experience`. \u2705
- Nessun grant `premium/hard/gems`. \u2705
- Nessuna attivazione `IAP/store/payment/gacha`. \u2705
- Nessun reward live `Guild/Arena/PvP/Event/Battlepass/AFK`. \u2705

## 10. Recommended Pack 110 (post-tester-intake)

La raccomandazione finale deve essere riformulata **dopo aver ricevuto i
feedback tester reali** e popolato la tabella P0/P1/P2/P3 in sezione 7.

Logica decisionale canonica (da PROMPT_MAIN):

```
if P0 exists:
    Pack 110 = P0 bugfix pack.
elif P1 exists:
    Pack 110 = P1 alpha-blocker cleanup pack.
elif P0 == 0 and P1 == 0 and user wants more gameplay:
    Pack 110 candidate \u2208 {
      Daily Login claim live controlled rollout,
      Achievements authoritative completion,
      Soul Forge live controlled rollout,
      Guild live runtime pack,
      Story / Tower UX polish pack
    }
```

**Raccomandazione preliminare (in assenza di feedback tester reali)**:

- Stato corrente safe-by-construction: tutti gli invariant OK.
- Pack 110 candidato pi\u00f9 sicuro (no risk reward live, no IAP, no gacha): **Story / Tower UX polish pack**.
- Pack 110 candidato a basso rischio: **Achievements authoritative completion** (richiede review economy/reward invariant; in caso di dubbio, defer).
- Pack 110 candidato a rischio medio (richiedono pack di autorizzazione esplicita prima): Daily Login claim live, Soul Forge live, Guild live runtime.

**NON viene raccomandato** nessun pack di tipo "reward live activation"
fino a quando i tester reali non avranno confermato che NESSUN bug economy/
reward \u00e8 stato osservato.

## 11. Decision (kickoff)

- **Continue alpha**: il framework kickoff \u00e8 pronto; aspettare intake tester.
- **Fix P0 first**: non applicabile (0 bug segnalati al momento del kickoff).
- **Fix P1 first**: non applicabile (0 bug segnalati al momento del kickoff).
- **Expand testers**: applicabile (target minimo 5 tester, attualmente 0 sessioni completate).

**Decisione di kickoff**: `CONTINUE_ALPHA_WAITING_TESTER_INTAKE_AND_EXPAND_TESTERS_TO_AT_LEAST_5`.

## 12. Artifacts Index

Artefatti creati / riferiti da questo kickoff:

- `docs/divine/111_CLOSED_ALPHA_INTERNAL_QA_TESTER_RUNBOOK.md` \u2014 runbook tester (italiano).
- `docs/divine/111_CLOSED_ALPHA_INTERNAL_QA_KICKOFF_AND_FEEDBACK_REPORT.md` \u2014 questo file.
- `docs/divine/templates/qa_tester_feedback_form.md` \u2014 form compilabile per tester.
- `docs/divine/templates/qa_bug_triage_matrix.md` \u2014 matrice triage iniziale.
- `docs/divine/110_CLOSED_ALPHA_MOBILE_QA_CHECKLIST.md` \u2014 checklist breve mobile (creata in Pack 109).
- `docs/divine/110_CLOSED_ALPHA_RC_SWEEP_RELEASE_GATE_FINAL_REPORT.md` \u2014 Pack 109 final report.
- `backend/scripts/qa_safety_invariants_probe.py` \u2014 helper read-only, lanciabile in qualunque momento.
- `backend/scripts/validate_qa_kickoff_artifacts.py` \u2014 validator docs-only degli artefatti.
- `data/qa_runbook/extracted/PROMPT_MAIN.md` \u2014 prompt sorgente del kickoff runbook.

## 13. Closing

Pack QA Kickoff chiusura: **docs-only/read-only**. Nessuna attivazione runtime.
`reward_live_general=false`. `release_readiness_claimed=false`.
`public_launch_ready=false`. `production_release_ready=false`.

Attendo:

1. Distribuzione del runbook ai tester (a cura dell'utente / coordinatore).
2. Ricezione di almeno 5 compilazioni `qa_tester_feedback_form.md`.
3. Popolamento delle tabelle in sezione 5 (tester matrix) e sezione 7 (bug triage) di questo report.
4. Decisione finale dell'utente sul Pack 110 sulla base dei dati raccolti.
