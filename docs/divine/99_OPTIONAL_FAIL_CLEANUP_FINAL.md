# 99 — OPTIONAL FAIL CLEANUP FINAL — v99

> Lingua: Italiano. Politica: NO validator weakening, NO fake PASS, NO hiding optional fail, NO validator removal solo per abbassare il numero.

## Stato finale

| Metrica | Pre-v99 | Post-v99 |
| --- | --- | --- |
| Pass | 999 | 1007 (+8 validator v99) |
| OPTIONAL FAIL | 134 | **134** (invariati) |
| REQUIRED FAIL | 0 | 0 |
| MISS | 0 | 0 |
| Target ≤30 | NOT_REACHED | **NOT_REACHED** |

## Audit forense dei 134 OPTIONAL FAIL

| Categoria | Count | Azione | Note |
| --- | --- | --- | --- |
| Stale MD5 `backend/battle_engine.py` post-v95 RC patch | **88** | deferred v100 (MD5 audit formale) | Il patch v95 era autorizzato e tracciato. Regenerazione massiva = validator weakening de-facto. |
| Environmental (Expo ENOSPC, Redis, Playwright limit) | 12 | acceptable for Closed Alpha | container Emergent caveats noti |
| Canary slice legacy (M/U/V/W/SP/PLAYER/FULL-REPO/BATCH1-V2) | 18 | deferred v100 (formal supersede review) | superseded da slice gating v90+ |
| Historical rollups pre-v90 | 8 | deferred v100 | MEGA-RELEASE-ACCELERATION-{1..21}-ROLLUP + MEGA-ECONOMY-SAFETY-ACCELERATION-{1..14}-ROLLUP |
| Design-only legacy bibles (Artifact/IAP/VIP/BP) | 8 | deferred v100 | design-only, no runtime |
| **true blocker per Closed Alpha** | **0** | nessuna azione | nessun fail blocca il runtime gioco |

## Validator rimossi / deprecati

NESSUNO. **No validator removal**.

## Proof rigenerate

NESSUNA in v99. La regenerazione MD5 baseline su 88 validator legacy richiede un audit MD5 formale per-validator con doc trail (processo v100), non eseguibile automaticamente senza weakening.

## Impact su Closed Alpha

- **Nessun blocker runtime gioco**.
- I 134 fail sono **tutti audit/MD5/legacy caveats**, **non bloccano** il gameplay.
- Verdetto: gate ≤30 **NOT_REACHED**, ma documentato onestamente come blocker tecnico.
- Closed Alpha può procedere come **CONDITIONAL** (non `READY`).

## Piano v100

1. `classify_optional_failures_v100.py` — classificatore con MD5 audit trail.
2. Regenerazione baseline `backend/battle_engine.py` storico post-v95 RC autorizzata formalmente.
3. Supersede review formale per 18 canary slice track.
4. Deprecation review per 8 design-only bibles legacy.
5. Target post-v100: `optional_fail <= 30`.

## Safety

```
validator_weakening = false
fake_PASS = false
validator_removed_to_lower_count = false
hidden_optional_fail = false
required_fail_introduced = false
```
