# 144C — STATUS SECOND SLICE — DEV-LIVE BEHAVIOR REGRESSION

## Track C — `PROJECT_V_TRACK_C`

**Verdict:** `TRACK_C_SECOND_SLICE_DEV_LIVE_BEHAVIOR_REGRESSION_READY`

## 1. Obiettivo

Verificare in regression test che il comportamento del resolver second-slice con flag ON sia **identico** alla baseline funzionale stabilita nel Pack S/T, su tutte le famiglie, caps e modalità di gioco.

## 2. Casi coperti

| Metrica | Valore |
|---|---|
| Casi totali | 14 |
| Casi PASS | 14 |
| Casi FAIL | 0 |

## 3. Famiglie coperte

- `debuff_offensive`
- `debuff_defensive`
- `speed_up`
- `speed_down`

## 4. Caps coperti

- `per_status_max`
- `aggregate_offensive`
- `aggregate_defensive`
- `aggregate_speed`

## 5. Modalità coperte

- `campaign`
- `pvp`
- `boss`

## 6. Edge cases verificati

- Cancel di coppie opposte (`speed_up` ↔ `speed_down`) ✅
- Ignore di status out-of-scope ✅
- Misto valid + invalid ✅
- Nessun DOT / tick loop touched ✅

## 7. Validator

`validate_project_v_second_slice_dev_live_behavior_regression_v1.py` → **PASS**.
