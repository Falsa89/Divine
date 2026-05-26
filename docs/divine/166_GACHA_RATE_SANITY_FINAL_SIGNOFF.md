# 166 — PROJECT GACHA RATE SANITY FINAL SIGNOFF

**Verdict:** `PROJECT_GACHA_RATE_SANITY_FINAL_SIGNOFF_COMPLETE`

## Sommario

Pack P0 che chiude il signoff finale delle rate gacha. Le rate dev-like
(8–30% combinato 5★+6★) sono state sostituite con le rate canoniche launch
V1 (1.5–5.0% combinato 5★+6★). Le guarantee weights hardcoded
`[0.65, 0.25, 0.10]` / `[0.70, 0.30]` sono state sostituite da
`guarantee_weights` normalizzate dalle rate finali per ogni banner,
eliminando la regressione QA "4 mitici + 3 leggendari in x10".

## Track Verdicts

| Track | Verdict |
|---|---|
| A — Audit | `TRACK_A_GACHA_SURFACE_AND_BACKEND_AUDIT_READY` |
| B — Final rate table | `TRACK_B_FINAL_RATE_TABLE_SIGNOFF_READY` |
| C — Frontend display | `TRACK_C_FRONTEND_RATE_DISPLAY_UPDATED_SAFE` |
| D — Backend alignment | `TRACK_D_BACKEND_RATE_ALIGNMENT_READY_SAFE` |
| E — Sanity tests | `TRACK_E_GACHA_RESULT_SANITY_TESTS_READY` |
| F — Pity contract | `TRACK_F_PITY_AND_DISCLOSURE_CONTRACT_READY` |
| G — Beta harness | `TRACK_G_BETA_HARNESS_AND_STATIC_AUDIT_INTEGRATION_READY` |
| H — Public repo sync | `TRACK_H_PUBLIC_REPO_SYNC_VERIFICATION_READY` |
| I — Completion | `TRACK_I_GACHA_RATE_SANITY_COMPLETION_READY` |

## Final Rate Table (Canonical Launch V1)

| Banner | 1★ | 2★ | 3★ | 4★ | 5★ | 6★ | 5★+6★ | Status |
|---|---|---|---|---|---|---|---|---|
| Standard  | 39.00 | 32.00 | 20.00 | 7.50  | 1.35 | 0.15 | 1.50% | LIVE |
| Elementale| 34.50 | 31.00 | 23.00 | 9.00  | 2.20 | 0.30 | 2.50% | LIVE |
| Selettivo | 32.00 | 30.00 | 24.00 | 10.50 | 3.00 | 0.50 | 3.50% | LIVE |
| Premium   | 28.00 | 29.00 | 25.00 | 13.00 | 4.25 | 0.75 | 5.00% | LOCKED (IAP signoff) |
| Mirato    | 28.00 | 29.00 | 25.00 | 13.00 | 4.25 | 0.75 | 5.00% | LOCKED (featured signoff) |

## Before/After

| Banner | 5★+6★ before | 5★+6★ after | delta |
|---|---|---|---|
| Standard  | 8% | 1.50% | −6.50pp |
| Elementale| 14% | 2.50% | −11.50pp |
| Selettivo | 18% | 3.50% | −14.50pp |
| Premium   | 30% | 5.00% | −25.00pp |
| Mirato    | 30% | 5.00% | −25.00pp |

## Simulation Result (seed = 20260601, 10000 x10 per banner)

Worst observed `5★+6★` in singolo x10:
- Standard: 4 (rare cluster)
- Elementale: 4
- Selettivo: 4
- Premium: 5 (di cui 4 dalla x9 e 1 dalla guarantee)
- Mirato: 5

Tutti **sotto** la soglia anti-regressione `< 7` ("4 mythic + 3 legendary").

## Invarianti

- `backend/battle_engine.py` MD5 `151ca35ad3bc35f0a6209cb3744ed440` ✅
- `backend/.env` MD5 `ff60bbb79efa329b71aa8ed351ea89b3` ✅
- Soul Forge: 0 Modal/KeyboardAvoidingView/confirmOpen ✅
- Artefatti / Costellazioni: HIDDEN (nessuna attivazione) ✅
- Premium / Mirato: LOCKED in UI (pulsanti disabilitati) ✅
- Nessuna IAP introdotta ✅
- Nessun DB write da script ✅
- Nessuna mutazione user/heroes/Character Bible ✅

## Suite

`python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --parallel`
→ **697 PASS / 0 FAIL / 0 MISS**

## Prossimo Pack consigliato

- Primary: `PROJECT_ARTIFACT_BIBLE_CANONICAL_DESIGN_PACK`
- Alternative: `PROJECT_IAP_DESIGN_PACK`
