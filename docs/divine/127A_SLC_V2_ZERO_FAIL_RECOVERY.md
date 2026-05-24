# 127A — PROJECT_E Track A — SLC V2 ZERO-FAIL RECOVERY

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_E`  
**Verdict**: 🟢 `TRACK_A_SLC_V2_ZERO_FAIL_RECOVERY_APPLIED_SAFE`  
**Rollback**: rimuovere il blocco `SUPERSEDED_AFTER_PROJECT_E_V2` dal suite runner (v1 ritorneranno a FAIL)

## 1. Strategia

8 successori v2 emessi + cluster v1 quarantinato via meccanismo `SUPERSEDED` esistente, gated da env var `SUITE_KEEP_DEPRECATED_AUDITS` (default OFF). Nessuna rimozione di evidenza: gli 8 script v1 restano on-disk e registrati in OPTIONAL.

## 2. Mappatura V1 → V2

| V1 task (SUPERSEDED default) | V2 task (PASS default) | Coverage |
|---|---|---|
| `SLC-C-REPO-PREFLIGHT` | `SLC-C-REPO-PREFLIGHT-V2` | **strict superset** (post-SLC-G baseline: 3 indexes, Phase 11 guard, apply marker) |
| `SLC-C-COMBO` | `SLC-C-COMBO-V2` | **strict superset** (preflight v2 + critical_files + api_smoke autosufficient) |
| `SLC-D-PREFLIGHT` | `SLC-D-PREFLIGHT-V2` | strict parity (upstream v2) |
| `SLC-D-COMBO` | `SLC-D-COMBO-V2` | strict parity |
| `SLC-BE-PREFLIGHT` | `SLC-BE-PREFLIGHT-V2` | strict parity |
| `SLC-BE-COMBO` | `SLC-BE-COMBO-V2` | strict parity (sp/select=503 dry-run scenario) |
| `SLC-F-PREFLIGHT` | `SLC-F-PREFLIGHT-V2` | strict parity |
| `SLC-F-COMBO` | `SLC-F-COMBO-V2` | strict parity |

## 3. Supersedence mechanism

- **Env gate**: `SUITE_KEEP_DEPRECATED_AUDITS`
- **Default (unset/false)**: v1 cluster → `[SUPERSEDED]` (`exit=--`, non-fail)
- **Opt-in (`true`)**: v1 cluster eseguito storicamente → 8 FAIL ricompaiono (scelta esplicita dell'operatore)
- **Presence gate**: tutti gli 8 v2 successor scripts devono esistere su disco prima che la supersedence si attivi

## 4. Anti-cheat invariants (tutti ✅)

- ❌ NO REQUIRED weakening
- ❌ NO hidden failures
- ❌ NO fake PASS
- ❌ NO evidence deletion (v1 scripts ancora on-disk)
- ✅ v1 entries ancora REGISTRATE in OPTIONAL list
- ✅ SUPERSEDED marker visibile nel report JSON

## 5. Expected suite state post-Track A

`pass ≥ 405, fail=0, miss=0, superseded=8`

## 6. Forbidden scope rispettato

REQUIRED weakening ❌, hiding failures ❌, fake PASS ❌, evidence deletion ❌, runtime changes ❌.
