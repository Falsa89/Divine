# 209I — SMOKE AND QA

**Track**: I | **Verdict**: `TRACK_I_SMOKE_AND_QA_READY`

## Smoke tests

| Test | Method | Path | Atteso |
|---|---|---|---|
| flag-off default | GET | `/api/material-raid/config` | 503 `disabled` |
| flag-on config | GET | `/api/material-raid/config` | 200, tracks+families+stage_model |
| flag-on stages | GET | `/api/material-raid/stages` | 200, stages I-V + power |
| reward open | POST | `/api/material-raid/reward-preview` | 200, `preview_ok` |
| reward locked | POST | `/api/material-raid/reward-preview` | 200, `locked_deferred` |
| reward invalid track | POST | `/api/material-raid/reward-preview` | 200, `invalid_track` |
| clear ok | POST | `/api/material-raid/clear-preview` | 200, `preview_ok` |
| clear underpowered | POST | `/api/material-raid/clear-preview` | 200, `team_underpowered_preview` |

## QA observations

- Tutti gli endpoint read-only/preview-only. Zero scrittura DB possibile.
- Reward preview blocca i 3 track locked con `locked_deferred`.
- `clear-preview` ritorna solo eligibility booleano + delta vs recommended.
- Zero stamina, zero tickets, zero paid currency.
