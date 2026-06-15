# 118 — Manual QA Device Runbook (Pre-QA Stabilization Pack 118)

**Pack:** `PRE_QA_STABILIZATION_118_MANUAL_QA_DEVICE_UNLOCK_PASS`
**Audience:** QA tester(s) on real device(s) (iOS + Android).
**Stato:** controlled targeted device QA — solo le superfici autorizzate in `pre_qa_118_manual_qa_allowed_surface_matrix_v1.json`.

---

## 0. Premessa di sicurezza

Questo runbook NON autorizza:
- claim/reward/spend/buy/summon/gacha,
- mark-read/read-all su mail,
- daily/achievement/battle-pass claim,
- push notification,
- chat/DM/bot live activation,
- hero upgrade mutation, material consume, equip/fuse/forge,
- combat authoritative play (no `battle_engine.py`),
- modifica formula Battle Power,
- modifica Red Dot oltre safe warnings 116C,
- modifica gacha rates,
- modifica Character Bible.

Il QA è **read-only / verify-locked-stays-locked**. Se durante il test un
endpoint inattesamente scrive su DB o un dot actionable appare per source
deferred, **STOP IMMEDIATO** e logga issue come `B9_safety_violation_blocker`
(vedi `pre_qa_119_post_qa_triage_buckets_v1.json`).

---

## 1. Pre-requisiti tester

1. Device fisico: 1 iPhone (iOS 17+) + 1 Android (Android 13+).
2. App installata via build Emergent (Publish + iOS/Android build).
3. Account dedicato di test (registrare nuovo account a inizio sessione).
4. Connessione rete stabile.
5. Logging device disponibile (Xcode console / `adb logcat`) opzionale.
6. Copia di `pre_qa_118_manual_qa_allowed_surface_matrix_v1.json` per checklist.

---

## 2. Setup sessione

```text
STEP 0.1 — install app version <build_id>
STEP 0.2 — open app
STEP 0.3 — register new account email=qa118_<timestamp>@test.com
STEP 0.4 — annota access_token (se la UI lo espone in dev) o procedi via UI
STEP 0.5 — verifica che app entri in /home senza crash
STEP 0.6 — apri Evidence Template e copia headers (vedi 118_MANUAL_QA_EVIDENCE_TEMPLATE.md)
```

---

## 3. Ordine d'esecuzione consigliato (26 superfici)

### Fase A — Stati negativi e endpoint metadata (curl / dev tools)
1. `118_qa_011` Hero Upgrade Readiness senza server_id → 400 SERVER_ID_REQUIRED.
2. `118_qa_007` Battle Power metadata.
3. `118_qa_008` Battle Power breakdown.
4. `118_qa_009` Red Dot metadata.
5. `118_qa_010` Hero Upgrade metadata + readiness (server_id=s1).
6. `118_qa_022` Negative no server_id (duplicato esplicito).
7. `118_qa_023` Negative no PSP.
8. `118_qa_026` Negative deferred source (Quality Frame in breakdown).

### Fase B — UI player-visible su device
9.  `118_qa_001` /home Battle Power.
10. `118_qa_002` /home Red Dot.
11. `118_qa_003` /menu Red Dot.
12. `118_qa_004` /heroes card power badge.
13. `118_qa_005` /hero-detail power + upgrade hint.
14. `118_qa_006` /battle formation slot_index.
15. `118_qa_020` Server profile required warning.
16. `118_qa_021` Team missing warning.

### Fase C — Verifica locked routes (deve restare gated)
17. `118_qa_012` /plaza gated.
18. `118_qa_013` /dm gated.
19. `118_qa_014` /gacha gated.
20. `118_qa_015` /shop deferred.
21. `118_qa_016` /battlepass deferred.
22. `118_qa_017` /mail deferred.
23. `118_qa_018` /daily-hub deferred.
24. `118_qa_019` /events not_ready.
25. `118_qa_024` Negative no team (PSP, team vuoto).
26. `118_qa_025` Negative source unsafe (global_blocker readiness).

---

## 4. Procedura per ogni riga QA

Per ciascuna riga della matrix:

```text
1. Leggi `qa_id`, `surface`, `route_or_endpoint`, `status`.
2. Esegui `verifier_actions` nell'ordine indicato.
3. Confronta osservato vs `expected_behavior` + `pre_qa_invariants`.
4. Cattura screenshot (player-visible) o curl output (endpoint).
5. Compila row in 118_MANUAL_QA_EVIDENCE_TEMPLATE.md.
6. Se PASS → next row.
7. Se FAIL → annota severity, screenshot, log, bucket triage (B1..B9).
```

---

## 5. Regole d'oro durante il test

- **Mai** premere bottoni di claim/spend/upgrade/buy/summon anche se appaiono.
  Se appaiono e sono attivi → bug `B9_safety_violation_blocker`.
- **Mai** abilitare permission push/notification durante test (non richiesto).
- **Mai** modificare credenziali admin / config server.
- **Mai** condividere screenshot con token / PII reale.
- Se un endpoint risponde con `mutation` o `db write`, FAIL critico (`B9`).
- Se il device manda push notification → FAIL critico (`B9`).
- Se l'app crasha → cattura crashlog completo + ultimo screen.

---

## 6. Triage buckets disponibili per ogni FAIL

Vedi `data/design/release_readiness/pre_qa_119_post_qa_triage_buckets_v1.json`:

| Bucket | Sicuro in 119? | Descrizione |
|--------|----------------|-------------|
| B1 UI copy/label | ✅ | Copy fix frontend-only. |
| B2 UI layout / safe area | ✅ | StyleSheet only. |
| B3 Read-only endpoint polish | ✅ | Additive only. |
| B4 Locked route copy | ✅ | Frontend-only. |
| B5 Red Dot aggregation polish | ✅ | Anti-fakedot. |
| B6 Observability / log polish | ✅ | Log cleanup. |
| B7 Security/auth minor | ✅ | Auth Depends additive. |
| B8 Live unlock | ❌ | Attendere Pack 120+. |
| B9 Safety violation | ✅ P0 | Revert + harden + new validator step. |

---

## 7. Fine sessione QA

```text
- Compila Evidence Template completo.
- Conta PASS / FAIL per fase.
- Classifica ogni FAIL in bucket B1..B9.
- Allega evidence (screenshot, log, curl output).
- Notifica Game Master con file evidence.
- NON aprire Pack 119 senza GM approval.
```

---

## 8. Stop conditions

Interrompere immediatamente la sessione QA se:
- Crash ripetuto su screen safe (P0).
- Endpoint inattesamente fa DB write (B9).
- Push notification arriva (B9).
- Chat/DM live attivo (regressione 116B, B9).
- Hero upgrade button attivo e cliccabile (regressione 117B, B9).
- Gacha summon possibile (regressione 115A, B9).

Log l'incidente immediatamente, allega evidence, ferma il test.
