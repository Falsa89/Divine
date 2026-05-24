# 144D — STATUS SECOND SLICE — DEV-LIVE EXTENDED LOAD

## Track D — `PROJECT_V_TRACK_D`

**Verdict:** `TRACK_D_SECOND_SLICE_DEV_LIVE_EXTENDED_LOAD_READY`

## 1. Obiettivo

Validare che il resolver second-slice mantenga latenze sub-target sotto un carico esteso (1000 chiamate miste su 3 modalità) con flag ON.

## 2. Carico applicato

| Metrica | Valore |
|---|---|
| Chiamate totali | 1000 |
| Errori | 0 |
| Durata totale | 0.01 s |
| Throughput | ~100 000 calls/s |
| Spend / Gacha / DB write / Destructive | tutto `false` |

## 3. Latenze (µs)

| Percentile | Valore | Target | Esito |
|---|---|---|---|
| p50 | 4.8 µs | n/a | ✅ |
| p95 | 4.9 µs | 100 ms | **dentro** ✅ |
| p99 | 7.1 µs | n/a | ✅ |
| max | 20.5 µs | n/a | ✅ |

## 4. Modalità mixed

- `campaign`
- `pvp`
- `boss`

## 5. Validator

`validate_project_v_second_slice_dev_live_extended_load_v1.py` → **PASS**.
