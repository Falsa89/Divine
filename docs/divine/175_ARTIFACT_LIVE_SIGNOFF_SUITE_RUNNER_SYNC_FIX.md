# 175 — PROJECT ARTIFACT LIVE SIGNOFF SUITE RUNNER SYNC FIX

## Verdetto locale
**`PROJECT_ARTIFACT_LIVE_SIGNOFF_SUITE_RUNNER_SYNC_FIX_READY`**

> Diventerà `_COMPLETE_PUBLIC_REPO_VERIFIED` solo dopo Save to GitHub → branch `main` → PUSH e verifica della repo pubblica.

---

## Obiettivo
Chiudere il mismatch del solo `backend/scripts/run_hero_skill_kit_validator_suite.py` sul branch pubblico `main`, dopo che il pack 174 ha sincronizzato correttamente JSON/doc/proof marker ma non il blob del suite runner.

## Scope (estremamente ristretto)
- ✅ 2 sole modifiche **a soli commenti** sul suite runner
- ✅ La tupla di registrazione Stage 7 NON viene duplicata (singola, count = 1)
- ✅ La sentinella v3 esistente è preservata
- ✅ Aggiunti: sentinella header v4 + sentinella inline RESYNC_v4
- ❌ Nessuna modifica a runtime, DB, frontend, gacha, IAP, battle_engine, `.env`
- ❌ Nessun live marker iniettato in `.env`
- ❌ Stage 8 non invocato

## Patch effettiva (2 hunk di soli commenti)

**Hunk 1** — header riga 2-3:
```python
 #!/usr/bin/env python3
 # PUBLIC_SYNC_TAG: suite_runner_live_signoff_v3_force_resnapshot_2026_05_27
+# PUBLIC_SYNC_TAG_RESYNC_v4: suite_runner_live_signoff_v4_force_resnapshot_after_stale_push_175
 # Stage 6 GATED-IMPORT and Stage 7 LIVE-ACTIVATION-SIGNOFF OPTIONAL validators
```

**Hunk 2** — vicino alla registrazione Stage 7 (righe ~1115-1117):
```python
     # STAGE_7_LIVE_ACTIVATION_SIGNOFF_REGISTRATION_SENTINEL (do not remove; required for public sync verification):
+    # STAGE_7_LIVE_ACTIVATION_SIGNOFF_REGISTRATION_RESYNC_v4 (sync fix 175; do not remove):
     ('PROJECT-ARTIFACT-INVENTORY-LIVE-ACTIVATION-SIGNOFF', 'validate_project_artifact_inventory_live_activation_signoff_v1.py'),
```

> La tupla di registrazione Stage 7 era già presente in HEAD locale dal pack 174 — è solo il push pubblico ad averla saltata.

## Aggiunte minori (oltre al fix del suite runner)
- 3 JSON di tracking in `data/design/artifacts/live_signoff_sync_fix/` (audit, patch, validation)
- 1 validator `backend/scripts/validate_project_artifact_live_signoff_suite_runner_sync_fix_v1.py`
- Registrazione OPTIONAL nel suite (`PROJECT-ARTIFACT-LIVE-SIGNOFF-SUITE-RUNNER-SYNC-FIX`) per attestare il fix nelle suite run future

## 🔒 Invarianti rispettati
```
151ca35ad3bc35f0a6209cb3744ed440  backend/battle_engine.py            ✅
ff60bbb79efa329b71aa8ed351ea89b3  backend/.env                        ✅  (zero marker live)
893f244d85fd45cbe825996463995293  backend/routes/artifacts.py         ✅
0e75c94e00899af773dbc9faf7326a15  frontend/app/artifacts-preview.tsx  ✅
8849e21c44207fc1d0074cae2cdc6879  frontend/app/artifacts.tsx          ✅
f68b9239cec04ea54879f0be381e772a  frontend/app/(tabs)/gacha.tsx       ✅
```

## 🎯 Suite custom Python
```
Overall: PASS  (pass=706, fail=0, miss=0)
```

## Stato locale del suite runner (post-patch)
| Verifica | Esito |
|---|:---:|
| `PUBLIC_SYNC_TAG: ...v3...` presente | ✅ riga 2 |
| `PUBLIC_SYNC_TAG_RESYNC_v4: ...v4...` presente | ✅ riga 3 |
| `STAGE_7_LIVE_ACTIVATION_SIGNOFF_REGISTRATION_SENTINEL` | ✅ riga 1115 |
| `STAGE_7_LIVE_ACTIVATION_SIGNOFF_REGISTRATION_RESYNC_v4` | ✅ riga 1116 |
| Tupla `('PROJECT-ARTIFACT-INVENTORY-LIVE-ACTIVATION-SIGNOFF', ...)` | ✅ riga 1117 (count = 1) |
| AST parse OK | ✅ |
| Nuovo MD5 | `92892b9d64b9919548c1b2a1a2380dc7` |

## 🔜 Prossimo pack
Nessuno automatico. Attendo l'utente per Stage 8 (con tutti i live marker + canary allowlist) o per shift di priorità su IAP/BP/Shop modernization.
