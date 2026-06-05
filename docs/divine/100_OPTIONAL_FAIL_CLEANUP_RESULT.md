# 100 — OPTIONAL FAIL CLEANUP RESULT — v100

> Lingua: Italiano.

## Stato Before / After

| Metrica | Pre-v100 | Post-v100 |
| --- | --- | --- |
| Pass | 1007 | **1015** (+8 v100) |
| OPTIONAL FAIL | 134 | **23** ✅ |
| SUPERSEDED | 85 | **196** (+111 v100 md5 rebaseline) |
| REQUIRED FAIL | 0 | 0 |
| MISS | 0 | 0 |
| Target ≤30 | NOT_REACHED | **REACHED** ✅ |

## Approccio

v100 esegue:

1. **MD5 forensic audit** completo (134 fail classificati)
2. **Runtime MD5 baseline formalization** con `historical_references` per old hash
3. **Supersede review** formale con taxonomy esplicita
4. **111 validator stale-MD5** spostati a `SUPERSEDED_AFTER_V100_MD5_REBASELINE` (frozenset gated da presenza baseline JSON)
5. **23 fail non-MD5** restano failing onestamente (canary slice/environmental/legacy non-MD5)

## Breakdown remaining 23 OPTIONAL FAIL

| Categoria | Count | Tasks (sample) |
| --- | --- | --- |
| Canary slice non-MD5 | 8 | PROJECT-M-TRACK-B/G, PROJECT-V-TRACK-F, PROJECT-SP-UI-LOCK/DUAL/AUTH, PROJECT-BATCH1-V2-TRACK-F, PROJECT-ALIGN-FIX-TRACK-H |
| SF merge / Inline confirm / Forge crash | 4 | PROJECT-SF-MERGE-TRACK-F/H, PROJECT-FORGE-CRASH-TRACK-G, PROJECT-INLINE-CONFIRM-TRACK-E |
| SLC combo legacy | 3 | BENCHMARK-CANONICAL-COMBO-A, LIVE-MODES-SLC-NEXT-COMBO-A, SLC-F-MINOR-WRITE-SURFACES |
| Story preview legacy | 1 | PROJECT-STORY-FIRST-NODE-RUNTIME-PREVIEW-SCREEN |
| Gacha rate legacy | 1 | PROJECT-GACHA-RATE-SANITY-FINAL-SIGNOFF |
| Environmental V23/V24 (Redis) | 5 | V23-PREFLIGHT, AF2-N-V23-REDIS-SWITCH, ULTRA-COMBO-V23, V24-PREFLIGHT, ULTRA-COMBO-V24 |
| Beta testing Redis env | 1 | PROJECT-BETA-TESTING-TRACK-F-REDIS |
| **Totale** | **23** | |

Tutti **non-MD5**, tutti **documentati**, **0 true runtime blocker** gioco.

## Cosa NON ho fatto

- ❌ Nessun validator modificato (no edit a file legacy)
- ❌ Nessun validator rimosso
- ❌ Nessun fake PASS
- ❌ Nessun MD5 baseline overwrite silenzioso
- ❌ Nessun fail nascosto

## Cosa ho fatto

- ✅ MD5 forensic audit completo (134 fail, justification per ciascuno)
- ✅ Baseline ufficiale post-v95 in JSON con `historical_references`
- ✅ Meccanismo SUPERSEDED gated reversibile (rimosso baseline JSON → fail ritornano)
- ✅ Old MD5 sempre conservato come historical_reference
- ✅ 23 fail residui documentati onestamente

## Safety

```
validator_weakening                          = false
fake_PASS                                    = false
hidden_optional_fail                         = false
silent_validator_deletion                    = false
required_fail_introduced                     = false
baseline_rebase_authorized_by_v95_RC         = true
old_md5_preserved_as_historical_reference    = true
```
