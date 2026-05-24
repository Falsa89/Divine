# 136C — CANARY FLAG ON BEHAVIOR SMOKE

**Pack**: `PROJECT_N` — Track C
**Verdict**: `TRACK_C_CANARY_FLAG_ON_BEHAVIOR_SMOKE_READY`
**Marker JSON**: `/app/data/design/status_effects/project_n_canary_flag_on_behavior_smoke_v1.json`

## 7 check B1–B7

| ID | Input/Check | Atteso | Osservato |
|----|-------------|--------|-----------|
| B1 | buff_offensive atk_pct 0.10 | `atk_pct=0.10` | ✅ |
| B2 | buff_offensive crit_pct 0.05 | `crit_pct=0.05` | ✅ |
| B3 | buff_defensive def_pct 0.10 | `def_pct=0.10` | ✅ |
| B4 | buff_defensive hp_pct 0.15 | `hp_pct=0.15` | ✅ |
| B5 | out-of-slice (debuff) | zero envelope | ✅ |
| B6 | cap clamp (0.99 → 0.30) | clamp respected | ✅ |
| B7 | seam source no DoT/tick/heal | 0 forbidden keywords | ✅ |

Deterministic 3v3 con flag ON in-process: SHA256 = `d951767a72…` (byte-identical al baseline).
