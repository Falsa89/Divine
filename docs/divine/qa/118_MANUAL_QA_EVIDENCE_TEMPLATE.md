# 118 — Manual QA Evidence Template

**Pack:** `PRE_QA_STABILIZATION_118_MANUAL_QA_DEVICE_UNLOCK_PASS`
**Sessione QA:** _<compila>_
**Tester:** _<nome>_
**Build ID:** _<id>_
**Device(s):** _<iPhone XX iOS XX> + <Android XX>_
**Account di test:** _<email/timestamp>_
**Inizio sessione (UTC):** _<YYYY-MM-DDTHH:MM:SSZ>_
**Fine sessione (UTC):** _<YYYY-MM-DDTHH:MM:SSZ>_

---

## Sommario

- Totale superfici testate: __ / 26
- PASS: __
- FAIL: __
- BLOCKED: __
- Bucket triage rilevati: __ (B1=?, B2=?, ...)

## Regression check rapida

- [ ] Battle Power formula version invariata (`battle_power_v1_preqa_derived`)
- [ ] Red Dot summary version invariata (`red_dot_v1_preqa_read_only_foundation`)
- [ ] Hero Upgrade source version invariata (`hero_upgrade_readiness_v1_preqa_read_only`)
- [ ] Plaza/DM gated (no chat live, no DM live)
- [ ] Gacha gated (no summon)
- [ ] Mail/Daily/BattlePass deferred (no claim attivo)
- [ ] Hero upgrade button inattivo (no upgrade mutation)
- [ ] Nessuna push notification ricevuta
- [ ] Nessun crash su screen safe

---

## Righe QA (compilare una per qa_id)

Template riga (copia per ogni qa_id):

```yaml
qa_id: 118_qa_XXX
surface: <nome surface>
status: <allowed_targeted_device_qa | allowed_read_only_endpoint_check | locked_verify_stays_locked | deferred_do_not_test_as_live | blocked_until_future_pack>
run_at_utc: <YYYY-MM-DDTHH:MM:SSZ>
device: <iPhone | Android>
observed_outcome: PASS | FAIL | BLOCKED
observed_details: |
  <descrizione di cosa hai visto/letto>
expected_behavior_match: yes | no
pre_qa_invariants_match: yes | no
evidence:
  - screenshot: <path o note>
  - curl_output: |
      <eventuale output curl>
  - log_excerpt: |
      <eventuale log>
bucket_triage_if_failed: <B1..B9 | N/A>
severity_if_failed: <P0 | P1 | NA>
notes_for_pack_119:
  - <eventuali raccomandazioni>
```

---

## Issue summary (compilare a fine sessione)

### P0 (must fix in Pack 119)

- [ ] _<qa_id>_ — _<descrizione>_ — bucket _<B?>_

### P1 (should fix in Pack 119)

- [ ] _<qa_id>_ — _<descrizione>_ — bucket _<B?>_

### Safety violations (B9, immediate stop)

- [ ] _<qa_id>_ — _<descrizione>_

---

## Verdetto finale tester

```text
[ ] PASS — Pack 118 Manual QA superato. Pronto per Pack 119 POST-QA Fix and Polish (se necessario).
[ ] FAIL — Issue rilevati. Lista issue allegata. Pack 119 richiesto.
[ ] BLOCKED — Safety violation rilevata. STOP. Notifica Game Master immediato.
```

Firma tester: _________________________   Data: _________________________

---

## Allegati

- [ ] Screenshot folder: `<path/to/screenshots/>`
- [ ] Curl output folder: `<path/to/curl/>`
- [ ] Crash logs (se presenti): `<path/to/logs/>`
- [ ] Evidence ZIP per Game Master: `<118_qa_evidence_<sessione>.zip>`
