# 163H — Soul Forge Forge Crash + API Contract + Shop Nav: Completion

## Verdict globale
`PROJECT_SOUL_FORGE_FORGE_CRASH_API_CONTRACT_AND_SHOP_NAV_FIX_COMPLETE`

## Track verdicts
| # | Track | Verdetto | Stato |
|---|-------|----------|:---:|
| A | Crash Root Cause Audit | `TRACK_A_SOUL_FORGE_FORGE_CRASH_ROOT_CAUSE_IDENTIFIED` | ✅ |
| B | Frontend Crash Proofing + Normalization | `TRACK_B_FRONTEND_FORGE_CRASH_PROOFING_FIXED_SAFE` | ✅ |
| C | Backend Contract Alignment | `TRACK_C_BACKEND_FORGE_ENDPOINT_CONTRACT_ALIGNED_OR_VERIFIED` | ✅ |
| D | Mobile Modal + Post-Success | `TRACK_D_MOBILE_CONFIRM_MODAL_AND_POST_SUCCESS_STATE_SAFE` | ✅ |
| E | Soul Shop Navigation Buttons | `TRACK_E_SOUL_SHOP_NAVIGATION_BUTTONS_READY_SAFE` | ✅ |
| F | Economy/Exclusive Recheck | `TRACK_F_ECONOMY_EXCLUSIVE_NAVIGATION_RECHECK_READY` | ✅ |
| G | Redis + Test Credentials Hygiene | `TRACK_G_REDIS_SUITE_NOISE_AND_TEST_CREDENTIALS_HYGIENE_READY` | ✅ |
| H | Completion | `TRACK_H_SOUL_FORGE_FORGE_CRASH_API_CONTRACT_SHOP_NAV_COMPLETION_READY` | ✅ |

## File modificati
| File | MD5 pre | MD5 post |
|------|---------|----------|
| `frontend/app/soul-forge.tsx` | `ba8f802d10cc774e65e8c552a1482099` | `88a39590454ecc1c5f16e34e09d90b63` |
| `memory/test_credentials.md` | (placeholder hygiene) | `d2c867673c75f703f6580174a2cef091` |

## File NON toccati (invarianti)
- `backend/routes/soul_forge.py` (contract già corretto)
- `backend/battle_engine.py` (MD5 invariant `151ca35a…`)
- `backend/.env` (MD5 invariant `ff60bbb7…`)
- `frontend/app/economy.tsx` (già locked redirect)
- `frontend/app/exclusive.tsx` (già locked notice)

## Backend / DB
- Backend changes: **0**
- DB writes: **0**
- Reward formula changes: **0**
- Endpoint changes: **0**

## API Contract Snapshot
```
POST /api/soul/forge   (auth-protected)
Body:     { "hero_ids": [<uhid>...] }
Response: { "gained_essence": <int>, "new_balance": <int> }
Verified empirically: curl -> {"gained_essence":10,"new_balance":10}
```

Il frontend ora normalizza anche risposte alternative (alias `gained|essence_gained|soul_essence_gained`, `balance|soul_essence|new_soul_essence`).

## Suite validator (parallel)
- **674 PASS / 5 FAIL / 0 MISS**
- I 5 FAIL sono **TUTTI Redis V23/V24 ambientali** (pre-esistenti, infra-scope, documentati onestamente in Track G).
- **0 fake PASS, 0 validator weakening, 0 REQUIRED weakening**.
- 8 nuovi validator `validate_forge_crash_track_*_v1.py` aggiunti alla suite OPTIONAL: tutti PASS.
- Pin MD5 di 11 JSON aggiornati per il nuovo MD5 di `soul-forge.tsx`.

## Vincoli rispettati
- ✅ Zero reward formula changes
- ✅ Zero backend route changes
- ✅ Zero DB writes da script
- ✅ Zero hero deletion da script
- ✅ Zero gacha/shop/IAP/battle_engine changes
- ✅ Zero MD5 drift su `battle_engine.py` e `backend/.env`
- ✅ Zero validator weakening
- ✅ Zero fake PASS / hidden failures
- ✅ Zero plaintext password committato

## Mobile QA Checklist (da verificare a vista dall'utente)
- [ ] Soul Forge si apre senza crash
- [ ] Hero card / filtri / scroll OK
- [ ] Selezione di un eroe 1-3★ funziona
- [ ] Press `FORGE SOUL` apre il modal
- [ ] Press `CONFERMA` esegue la chiamata senza crash
- [ ] Su success: appare il pannello "+N Soul Essence" e bilancio aggiornato
- [ ] Su API failure: banner rosso "Forge non riuscita" visibile, eroi restano selezionati
- [ ] L'app MAI crasha (prima, durante, dopo)
- [ ] Bottone `Apri Tesoreria` nel Negozio Anime preview funziona
- [ ] Bottone `Vai al Negozio` (locked) nel Negozio Anime preview funziona
- [ ] Bottone `Apri Negozio Oggetti` (locked) nel Negozio Polvere preview funziona
- [ ] Bottone `In Preparazione` disabilitato non porta a fake nav
- [ ] `/economy` ancora redirect-only, no retire/buy
- [ ] `/exclusive` ancora locked notice, no craft
- [ ] `memory/test_credentials.md` non contiene password plaintext

## Redis Validator Status (honesty report)
- 5 validator V23/V24 falliscono per **redis-cli non installato** nel container e binding supervisor `redis-server` rotto.
- Issue ambientale pre-esistente dell'handoff iniziale.
- **Nessun tentativo di fake PASS**.
- **Nessun validator indebolito**.
- Documentato in `data/design/soul_forge/forge_crash_track_g_hygiene_v1.json` come known infra-pack scope.

## Remaining blockers
Nessuno per questo pack.

## Next pack recommendation
🔴 **P0**: `PROJECT_GACHA_RATE_SANITY_FINAL_SIGNOFF_PACK` (dal Master Batch Plan precedente)

Opzionale a sequenza:
- `PROJECT_REDIS_INFRA_STABILIZATION_PACK` (per chiudere i 5 fail ambientali)
- `PROJECT_IAP_DESIGN_PACK`
- `PROJECT_SHOP_IAP_INTEGRATION_PACK`
