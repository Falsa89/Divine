# 118B — Web QA Access Harness Runbook

**Pack:** `PRE_QA_STABILIZATION_118B_WEB_QA_ACCESS_HARNESS_PACK`
**Audience:** Game Master + QA tester (web preview / dev build) — affianca il device runbook 118.
**Stato:** Harness QA-only, read-only, deeplink-only, dev/QA-gated.

---

## 0. Cos'è

La pagina `/qa-manual-118` (`frontend/app/qa-manual-118.tsx`) è una **superficie
QA web**, non player-facing. Permette al Game Master di verificare in modo
diretto e veloce gli 8 endpoint read-only autorizzati (Battle Power, Red Dot,
Hero Upgrade, User Heroes) senza dover usare obbligatoriamente l'app wrapper
Expo sul telefono.

**NON è una superficie player.** Non viene linkata da home/menu/tab. Accesso
esclusivo per **deeplink** + **flag dev/QA** (`EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE=true`).

---

## 1. Quando usarla

- Validazione veloce Pack 116A/EXT/FIX-A/116B/116C/117A/117B/118 dal browser.
- Affiancamento durante Manual QA su device reale (Pack 118).
- Spot-check rapidi delle invarianti pre-QA prima di un re-audit Game Master.
- Verifica regressioni dopo polish/fix (Pack 119) preparatori.

Non usare per:
- Test live di sistemi player non ancora sbloccati.
- Test di endpoint mutation (mai presenti in questa pagina).
- Demo a stakeholder esterni (è una pagina interna).

---

## 2. Pre-requisiti

1. Build web preview Expo attiva (oppure dev build).
2. Backend in esecuzione su `8001` (controllo: `GET /api/battle-power/metadata` HTTP 200).
3. Flag environment frontend `EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE=true` impostato nella sessione QA.
4. (Opzionale) Account utente registrato con `bearer_token` valido per endpoint server-scoped.
5. `server_id` di test noto (default consigliato: `s1`).

---

## 3. Setup sessione

```text
STEP 0.1 — verifica EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE=true (frontend env QA)
STEP 0.2 — apri il web preview o build dev/QA
STEP 0.3 — naviga al deeplink /qa-manual-118 (no link in tabs/menu)
STEP 0.4 — verifica banner ROSSO "QA-only·read-only·no mutations·no live systems"
STEP 0.5 — inserisci server_id (default s1)
STEP 0.6 — (opzionale) incolla un bearer_token QA
STEP 0.7 — premi "Run all read-only probes"
```

Se la pagina mostra il banner "QA-only · gated" senza controlli, il flag
`EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE` non è attivo. Sblocca per la sessione e
ricarica.

---

## 4. Endpoint coperti

Vedi `118_WEB_QA_ACCESS_HARNESS_SNAPSHOT.json` per la lista completa (8 GET
autorizzati):

| # | Endpoint | Auth | server_id | Invariant chiave |
|---|----------|------|-----------|------------------|
| 1 | `GET /api/battle-power/metadata` | no | no | `formula_version=battle_power_v1_preqa_derived` |
| 2 | `GET /api/battle-power/summary?server_id=...` | yes | yes | server-scoped find_one PSP |
| 3 | `GET /api/battle-power/breakdown` | no | no | `breakdown_version=battle_power_breakdown_v1_preqa_metadata_only` · `metadata_only_COMPLETE` |
| 4 | `GET /api/red-dot/metadata` | no | no | `red_dot_summary_version=red_dot_v1_preqa_read_only_foundation` |
| 5 | `GET /api/red-dot/summary?server_id=...` | yes | yes | actionable_now=false su sources non-warning safe |
| 6 | `GET /api/hero-upgrade/metadata` | no | no | `source_version=hero_upgrade_readiness_v1_preqa_read_only` |
| 7 | `GET /api/hero-upgrade/readiness?server_id=...` | yes | yes | `any_red_dot_candidate=false` · `can_upgrade_now=false` |
| 8 | `GET /api/user/heroes?server_id=...` | yes | yes | read-only roster server-scoped |

Nessun altro endpoint può essere chiamato dalla pagina. Nessun bottone esegue
mutazioni. Nessun bottone abilita claim/upgrade/spend/buy.

---

## 5. Comportamento atteso per endpoint

Vedi `118_WEB_QA_ACCESS_HARNESS_SNAPSHOT.json` → `expected_keys` e `invariant`.

**Casi negativi (utili da verificare):**
- `GET /api/hero-upgrade/readiness` senza `server_id` → HTTP 400 `SERVER_ID_REQUIRED`.
- Endpoint server-scoped senza bearer → HTTP 401 `Token mancante`.
- `GET /api/red-dot/summary?server_id=s1` neo-utente → HTTP 200 con source `server_profile_required` (warning safe 116C).

---

## 6. Regole d'oro

- **MAI** premere qualcosa che non sia un "Probe" o "Run all read-only probes".
- **MAI** modificare manualmente la URL per aggiungere endpoint non in lista.
- **MAI** copiare `bearer_token` di account reali in screenshot.
- Se un endpoint risponde con campi indicanti mutation/db_write/push attiva: STOP, FAIL critico (bucket B9).
- Se una probe scrive nel DB (visibile da metriche backend): STOP, FAIL critico (B9).
- Se appare un bottone claim/upgrade/spend nella pagina: STOP, regressione 118B.

---

## 7. Output evidence

Per ogni endpoint, riporta in `docs/divine/qa/118_MANUAL_QA_EVIDENCE_TEMPLATE.md`
(blocco "endpoint probes"):

```yaml
qa_id: 118b_web_probe_<endpoint_id>
endpoint: <path>
http_status: <200|400|401|...>
latency_ms: <int>
invariant_match: yes|no
response_excerpt: |
  <prime 500 char>
notes: <eventuali anomalie>
```

---

## 8. Stop conditions

Interrompi la sessione harness se:
- Probe inattesa scrive su DB (regressione P0).
- Push notification arriva durante test (regressione B9).
- Endpoint non in lista risulta chiamato dalla pagina (regressione 118B).
- Pagina mostra widget/bottone non-Probe non-Run (regressione 118B).
- Backend down: dichiarare `SKIPPED_BACKEND_DOWN`, NON marcare PASS.

---

## 9. Fine sessione

- Esporta evidence (screenshot della pagina + JSON output per ogni endpoint).
- Aggiorna `118_MANUAL_QA_EVIDENCE_TEMPLATE.md` (sezione "web harness probes").
- Disabilita `EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE` dopo la sessione QA.
- Notifica Game Master con evidence allegata.

---

## 10. Note di sicurezza

- La pagina **non** registra alcun listener push.
- La pagina **non** apre WebSocket.
- La pagina **non** usa `localStorage` per storing token oltre l'input controllato.
- La pagina **non** è elencata in nessuna route player; il file vive in `frontend/app/qa-manual-118.tsx` accessibile solo via deeplink.
- Il banner rosso è permanente in alto e segnala QA-ONLY / READ-ONLY / NO MUTATIONS / NO LIVE SYSTEMS.
