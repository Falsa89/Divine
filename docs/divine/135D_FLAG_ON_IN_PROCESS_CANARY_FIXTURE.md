# 135D — FLAG ON IN-PROCESS CANARY FIXTURE

**Pack**: `PROJECT_M` — Track D
**Verdict**: `TRACK_D_FLAG_ON_IN_PROCESS_CANARY_FIXTURE_READY`
**Marker JSON**: `/app/data/design/status_effects/project_m_flag_on_in_process_canary_fixture_v1.json`
**Validator**: `/app/backend/scripts/validate_project_m_flag_on_in_process_canary_fixture_v1.py`

## Esecuzione

Il flag `STATUS_RUNTIME_BUFF_SLICE_ENABLED` è valorizzato a `'true'` **solo dentro il processo di test** tramite `os.environ`, ripristinato in `finally`. Nessun env backend toccato; nessuna chiamata a `simulate_battle` durante il test.

## Fixtures (6/6 PASS)

| ID | Input | Atteso | Osservato |
|----|-------|--------|-----------|
| C1 | `buff_offensive atk_pct 0.10` | `atk_pct=0.10` | ✅ |
| C2 | `buff_offensive crit_pct 0.05` | `crit_pct=0.05` | ✅ |
| C3 | `buff_defensive def_pct 0.10` | `def_pct=0.10` | ✅ |
| C4 | `buff_defensive hp_pct 0.15` | `hp_pct=0.15` | ✅ |
| C5 | `debuff atk_pct 0.50` (out-of-slice) | zero envelope | ✅ |
| C6 | `buff_offensive atk_pct 0.99` (oltre cap) | `atk_pct=0.30` (clamp master cap) | ✅ |

## Conformità ai guardrail

- ✅ Nessun backend env toggle.
- ✅ Nessuna live battle mutation.
- ✅ Nessun DB write.
- ✅ Env ripristinata al termine.
