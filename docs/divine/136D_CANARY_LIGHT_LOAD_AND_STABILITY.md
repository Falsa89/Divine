# 136D — CANARY LIGHT LOAD AND STABILITY

**Pack**: `PROJECT_N` — Track D
**Verdict**: `TRACK_D_CANARY_LIGHT_LOAD_AND_STABILITY_READY`

## Profilo load

- 150 richieste (50 loop × 3 endpoint: `/api/heroes`, `/api/heroes/borea`, `/api/heroes/greek_borea`)
- Durata: 2.86 s → ~52 RPS
- Non-destructive: no spend, no gacha, no DB mutation

## Risultati

| Metrica | Valore |
|---------|--------|
| 2xx | 150 |
| 4xx | 0 |
| 5xx | 0 |
| Errori | 0 |
| Latenza p50 | 1.98 ms |
| Latenza p95 | 55.14 ms |
| Latenza p99 | 68.87 ms |
| Latenza max | 80.23 ms |

Nessuna regressione vs flag OFF baseline.
