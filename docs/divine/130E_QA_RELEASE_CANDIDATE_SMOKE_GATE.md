# 130E — QA Release Candidate Smoke Gate (Track E)

**Verdict:** `TRACK_E_QA_RELEASE_CANDIDATE_SMOKE_GATE_READY`

## Safe automated subset (9 check)
| # | Check | Target | Atteso |
|---|---|---|---|
| S1 | API health | GET /api/heroes | 200 |
| S2 | Heroes catalog count | GET /api/heroes | 100 |
| S3 | Borea inert | GET /api/heroes/borea | 200 |
| S4 | Primordial Gaia absent | GET /api/heroes/primordial_gaia | 404 |
| S5 | server_profiles preview disabled | GET+POST /api/server-profiles/select | 503 |
| S6 | Housing preview disabled | GET /api/housing/preview | 503 |
| S7 | AF2-N approval gates PENDING | static check marker | 5/5 PENDING |
| S8 | Gacha safe non-spend | validator-only | zero spend |
| S9 | Artifact/Housing no live leak | env audit | live envs unset |

## Manual_required (post-RC)
- Real battle smoke (manual operator).
- Live login dryrun (richiede credenziali seedate `QA_TEST_*`).

## Vincoli rispettati
- NO account creation, NO real gacha spend, NO currency mutation,
  NO destructive action, NO secret logging, NO frontend.
