# Divine Waifus — Pre-QA Repo Audit Pass 1 Findings

## Verdict provvisorio

`PRE_QA_NOT_READY_FIX_PACK_REQUIRED`

L'audit statico dello ZIP aggiornato ha già trovato blocker sufficienti per NON avviare la QA manuale su tester reali. Il codice compila lato Python (`python3 -m compileall backend` OK), ma la repo reale contiene ancora superfici legacy/live/player-facing che contraddicono i vincoli Pack 91–109.

Questo è un Pass 1: non è ancora la matrice finale completa di tutti i file e di tutte le 17 nuove feature, ma i blocker sotto sono già abbastanza gravi da richiedere un fix pack pre-QA.

---

## P0-01 — Gacha live, player-facing, account-wide e con spend di gems

**File:**
- `backend/server.py` lines 764–828
- `frontend/app/(tabs)/gacha.tsx` lines 83–130
- `frontend/app/(tabs)/_layout.tsx` lines 49–56

**Evidenza:**
- `POST /api/gacha/pull` e `POST /api/gacha/pull10` sono attivi.
- Spend: `db.users.update_one(... {"$inc": {"gems": -cost}})`.
- Grant roster: `db.user_heroes.insert_one(...)` senza `server_id`.
- Il tab Gacha è esposto come `Evoca` nella bottom navigation.
- La UI chiama direttamente `/api/gacha/pull` e `/api/gacha/pull10`.

**Perché è blocker:**
Contraddice `NO IAP/store/payment/gacha activation`, `NO premium/hard/gems grant/spend`, server-scope PSP e no account-wide roster mutation.

**Azione consigliata:**
Quarantinare o nascondere Gacha prima della QA manuale. Se deve restare visibile, mostrarlo locked/read-only con blocker `GACHA_LIVE_DISABLED_BY_ALPHA_GATE` e nessuna POST mutante.

---

## P0-02 — Team formation player-facing usa ancora endpoint legacy account-wide

**File:**
- `frontend/app/(tabs)/battle.tsx` lines 136–145, 248–267
- `backend/battle_engine.py` lines 1377–1427
- `backend/routes/v96_team_formation.py` lines 37–180

**Evidenza:**
- Battle tab carica `/api/team` senza `server_id`.
- Battle tab salva su `/api/team/update-formation` senza `server_id`.
- Backend salva in `db.teams` filtrando solo `user_id` + `is_active=True`.
- Esiste un endpoint strict read `/api/team/get-formation?server_id=...`, ma il frontend player-facing non lo usa.

**Perché è blocker:**
La formazione team è gameplay core e deve essere server-scoped. Questo path può mescolare S1/S2 e smentisce la promessa "no account-wide gameplay state".

**Azione consigliata:**
Aggiornare Battle tab a usare il loader strict con `server_id`. Se il save server-scoped non esiste, disabilitare/preview-only il salvataggio o creare endpoint strict PSP team save gated/tested.

---

## P0-03 — Mismatch `useServerScope`: hook espone `selected_server_id`, componenti leggono `serverId`

**File:**
- `frontend/src/hooks/useServerScope.ts` lines 16–24, 37–48
- `frontend/src/components/DailyHomeRewardSection.tsx` lines 58–63
- componenti coinvolti: `DailyLoginClaimButton`, `DailyQuestClaimButton`, `DailyTaskLoopOverview`, `TowerStrictConsumer`, `EconomyStrictConsumer`, `ControlledRewardsConsumer`

**Evidenza:**
- Il type `ServerScope` contiene `selected_server_id`, non `serverId`.
- Molti componenti fanno `scope?.serverId` o `const { serverId } = useServerScope()`.
- `DailyHomeRewardSection` ritorna `null` se `!scope?.serverId`.

**Perché è blocker:**
Le superfici safe/gated installate dai Pack 98–106 possono non renderizzare mai. È un drift tra report e codice reale.

**Azione consigliata:**
Unificare API hook: esporre sia `serverId` alias sia `selected_server_id`, aggiungere `isReady/refreshToken` se richiesto, e correggere componenti/validator TS.

---

## P0/P1-04 — Doppio sistema Auth/token rompe PSP ensure/starter dopo login default

**File:**
- `frontend/app/index.tsx` lines 12–19, 60–110
- `frontend/context/AuthContext.tsx` lines 62–94
- `frontend/src/auth/AuthContext.tsx` lines 21–23, 68–83
- `frontend/app/servers.tsx` lines 197–270

**Evidenza:**
- Login default usa `../context/AuthContext` e salva token in `AsyncStorage` key `token`.
- Login v96 usa `../src/auth/AuthContext` e salva token in SecureStore key `v96_auth_token`.
- Server select chiama `POST /api/psp/ensure` e `/api/psp/starter/claim` solo con `v96_auth_token`.
- Se l'utente entra dal login default, il server viene selezionato, ma ensure/starter claim può non partire.

**Perché è blocker:**
Onboarding/server fresh-start rischia di non creare PSP/starter reali per il flusso più visibile. QA manuale potrebbe partire in stato incoerente.

**Azione consigliata:**
Unificare auth o rendere `/servers` compatibile con entrambi i token. Idealmente usare un solo AuthContext player-facing.

---

## P0/P1-05 — Menu player espone modalità legacy/deferred/QA

**File:**
- `frontend/app/(tabs)/menu.tsx` lines 10–122+

**Evidenza:**
Menu espone, tra gli altri:
- `Arena PvP`
- `Battle Pass`
- `Negozio Oggetti`, `Negozio`, `VIP`
- `Gilda & Fazioni`, `Guerra tra Gilde`, `Raid Cooperativi`, `Conquista Territori`
- `Piazza Comunitaria`, `Messaggi`
- `Eventi Giornalieri`
- sezioni QA: `Playability & Announcements QA (v93)`, `Modalità Live & Guild QA (v92)`

**Perché è blocker:**
Pack 108/109 dichiarano no false-ready e sistemi deferred/gated. Il menu reale mostra molte superfici non pronte o legacy come se fossero player-facing.

**Azione consigliata:**
Nascondere QA/dev menu e route unsafe dietro flag default OFF; per sistemi deferred usare card locked/deferred non cliccabili o safe preview.

---

## P0-06 — Legacy achievements claim bypassa Pack 106 controlled rewards

**File:**
- `backend/routes/achievements.py` lines 237–258

**Evidenza:**
- `POST /achievements/claim` è attivo.
- Usa reward legacy con `gold`, `gems`, `stamina`.
- Mutazione: `db.users.update_one(... {"$inc": user_inc})`.
- Non usa Pack 106 `achievement_claim_controlled`, completion-proof, ledger/idempotency safe, o server_id.

**Perché è blocker:**
Bypassa il sistema controllato Pack 106 e reintroduce gems/gold rewards account-wide.

**Azione consigliata:**
Quarantinare legacy `/achievements/claim` o redirigere a controlled rewards. Achievements live vero resta deferred/controlled.

---

## P0/P1-07 — Molte route legacy mutanti risultano ancora registrate

**File principali:**
- `backend/game_systems.py`
- `backend/routes/economy.py`
- `backend/routes/items.py`
- `backend/routes/forge.py`
- `backend/routes/raids.py`
- `backend/routes/cosmetics.py`
- `backend/routes/gvg.py`
- `backend/routes/social.py`
- `backend/routes/unique_items.py`
- `backend/routes/level_sharing.py`

**Evidenza:**
`game_systems.py` registra sia route strict nuove sia molti moduli legacy. La scansione ha trovato mutating endpoints non tutti chiaramente gated.

**Perché è blocker:**
Anche se alcuni non sono linkati, una QA build non dovrebbe esporre endpoint mutanti legacy non allowlisted, specialmente se toccano economy/reward/progress.

**Azione consigliata:**
Creare allowlist router alpha, static validator di mutating endpoints, e quarantena per route legacy non incluse nel playable loop.

---

## P1-08 — Commento/hook `useServerScope` ancora dichiara backend isolation pending

**File:**
- `frontend/src/hooks/useServerScope.ts` lines 1–7, 43–46

**Evidenza:**
Il commento dice che backend per-server isolation non è implementata e i dati runtime restano account-wide.

**Perché conta:**
È stale rispetto ai Pack 91–109 e può confondere implementazioni future; inoltre il hook non è stato riallineato ai componenti attuali.

**Azione consigliata:**
Aggiornare hook, commenti e contract frontend-server.

---

# Stato preliminare delle 17 funzioni extra

| ID | Funzione | Stato preliminare repo | Priorità |
|---|---|---|---|
| 1 | Multi-team multi-phase battle | Non trovata come runtime best-of-3 player-vs-player; solo riferimenti design multi-team raid boss. | B |
| 2 | Server Factory / nuovi server | PSP onboarding esiste, ma server blueprint/factory e calendar non risultano completi. | A/B |
| 3 | Login reward popup / new server calendar | Daily/controlled rewards esistono; popup/calendar completi non confermati. | A/B |
| 4 | Offerte triggerate | Non trovate come sistema runtime; da design-only. | C |
| 5 | Rating/commenti/team suggestions eroi | Non trovati runtime completi. | B/C |
| 6 | Radar stat chart | Non trovato runtime evidente. | B |
| 7 | i18n lingue principali | Non trovato framework i18n completo; molte stringhe hardcoded. | B |
| 8 | Descrizioni accurate | Presenti molti cataloghi/testi, ma qualità/coerenza da auditare; possibili placeholder/legacy. | A/B |
| 9 | Annunci live | Esistono QA preview, non broadcast runtime live confermato. | B |
| 10 | Floating damage/heal numbers | Da approfondire; non confermato overlay target-combat completo. | B |
| 11 | Font dedicato | Non confermato; occhio licenze. | C/B |
| 12 | BP delta | Esiste design/future references; runtime delta overlay dichiarato deferred in docs. | B |
| 13 | Welcome/new server/welcome back/event popup | Non confermato completo. | A/B |
| 14 | Spedizione eroi | Non trovata. | B |
| 15 | Daily quest stile Bleach | Daily tracker/claim esiste; barra/milestone/x2 non confermati. | A/B |
| 16 | Endless/survival mode | Non trovata runtime completa. | B |
| 17 | Ask/suggest | Attiva come regola audit/design. | — |

---

## Raccomandazione immediata

Non avviare QA manuale. Preparare prima un fix pack pre-QA:

`PRE_QA_STABILIZATION_110_ALPHA_BLOCKER_CLEANUP`

Scope minimo:
1. Quarantina/hide Gacha live e tab Evoca.
2. Quarantina legacy Achievements claim o redirect a controlled path.
3. Fix `useServerScope` API e componenti serverId.
4. Allinea Battle Team Formation a server-scoped loader/save o disabilita save legacy.
5. Unifica auth/token o rende Server Select compatibile col login default.
6. Rimuovi/nascondi menu QA/dev/deferred unsafe da player menu.
7. Add static validator mutating endpoints allowlist.
8. Final smoke: no gacha live, no account-wide team save, no legacy rewards, selected server required, no false-ready.

