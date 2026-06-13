# Closed Alpha Manual QA — Bug Intake Log

> **Stato:** Manual QA INTERNA CONTROLLATA — AVVIATA
> **Autorizzazione:** Game Master, `FINAL_DEEP_REAUDIT_PASS_4_RETRY = GREEN`
> **HEAD autorizzato:** `40571ad5738b2180cd741cfff7b0b0b0ab695c2b`
> **Linguaggio:** Italiano

---

## Vincoli di QA (estratti dal verdetto Game Master)

Durante la Manual QA NON è ammesso:

| Vincolo | Stato |
|---|---|
| Gacha live | 🚫 OFF (resta `GACHA_LIVE_DISABLED_PRE_QA`) |
| IAP / payment / store live | 🚫 OFF |
| Reward live | 🚫 OFF (`reward_live_general=false`) |
| Mutation `users.gold/gems/experience` | 🚫 vietata |
| Battle reward/progress live non autorizzato | 🚫 vietato |
| Nuova feature implementation | 🚫 vietata |
| Runtime activation | 🚫 vietata |
| Public launch claim | 🚫 vietata |
| Closed Alpha pubblica / store claim | 🚫 vietata |

Ogni bug trovato deve essere riportato e classificato in questo log.
Ogni fix successivo deve essere **targeted** e **approvato** dal Game Master prima dell'implementazione.

---

## Bug intake template

Per ciascun bug ricevuto, compilare:

```
## BUG-<YYYYMMDD>-<NN> — <titolo breve>

- **Reporter:** Game Master / QA tester #N
- **Severity:** P0 / P1 / P2 / P3
  - P0 = crash / leak account-wide / mutazione vietata / blocker QA
  - P1 = funzionalità rotta sul main flow autorizzato
  - P2 = UX/contenuto/navigazione su flow secondario autorizzato
  - P3 = cosmetic / minor
- **Area:** backend / frontend / nav-guard / server-scope / auth / other
- **Repro steps:** ...
- **Expected:** ...
- **Observed:** ...
- **Logs / payload (se applicabile):** ...
- **Files candidati:** ...
- **Vincoli toccati (se applicabile):** ...
- **Status:** OPEN / IN_REVIEW / FIX_PROPOSED / APPROVED_BY_GAMEMASTER / FIXED / VERIFIED / WONT_FIX
- **Pack di fix proposto:** PRE_QA_STABILIZATION_<N>_<short_name>
- **Verifica fix:** validator / smoke / suite x?
- **Approvato dal Game Master:** SI / NO / IN_ATTESA
```

---

## Workflow fix bug durante Manual QA

1. **Bug ricevuto** dal Game Master / tester interno → aperto in questo log con severity provvisoria.
2. **Triage** da parte dell'agente: classificazione severity, area, files candidati, conferma vincoli non violati.
3. **Proposta di fix targeted** (NO refactor, NO nuove feature, scope minimo): l'agente prepara la proposta come Pack candidate (es. `PRE_QA_STABILIZATION_115_<short_name>`) ma **NON committa nulla** prima dell'approvazione.
4. **Approvazione esplicita Game Master** richiesta prima di toccare codice.
5. **Implementazione**: solo i file autorizzati. `git add -- <path>` esplicito (mai `git add -A`).
6. **Validazione**:
   - validator dedicato al pack (se previsto);
   - smoke runtime (se applicabile);
   - Master Validation Suite x1 (o x3 se flakiness Redis ricompare);
   - hygiene: `git restore data/design/` se la suite produce artifacts;
   - verifica `git diff --name-only <pre> HEAD` mostri SOLO i file dichiarati.
7. **Report onesto**: nuovo `docs/divine/<N>_<pack>_FINAL_REPORT.md` con SHA, diff, validator/smoke/suite result, safety invariants, verifica negativa forbidden.
8. **Verdetto Game Master**.

---

## Test sandbox raccomandata

- **Auth bootstrap test:** `POST /api/auth/guest` con `alias_hint` random (sandbox `GUEST_QA_ONLY`, gated, no email/password persistente).
- **Backend base URL:** `http://localhost:8001`
- **Health check:** `GET /api/health` o `GET /openapi.json`
- **Gacha guard verify:** `POST /api/gacha/pull` → atteso `423` + `GACHA_LIVE_DISABLED_PRE_QA`.
- **Server scope check:** rispetto chiave AsyncStorage `v101_selected_server_id`.

---

## Log bug aperti

> Nessun bug ricevuto al momento. In attesa del primo intake dal Game Master.

---

## Log bug chiusi

> (vuoto)

---

*Log inizializzato all'apertura della Manual QA interna controllata, su autorizzazione del Game Master del 2026-06.*
