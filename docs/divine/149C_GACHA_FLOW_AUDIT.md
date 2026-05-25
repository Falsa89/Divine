# 149C — SUMMON & GACHA FLOW AUDIT

## Track C — `PROJECT_FRONTEND_B_TRACK_C`

**Verdict:** `TRACK_C_SUMMON_AND_GACHA_FLOW_AUDIT_READY`

## Route auditata

- `/(tabs)/gacha` (457 LOC)

## Flow steps (6)

1. Tab Evoca → lista banner (`GET /api/gacha/banners`)
2. Selezione banner → pity counter, raretà
3. Pull singolo / Pull 10x (`POST /api/gacha/pull[10]`)
4. Animazione evocazione
5. Reveal raretà
6. Goto hero-detail

## Gap identificati (4)

| Gap | Severity |
|---|---|
| History pull permanente assente | medium |
| Pity counter senza spiegazione testuale | low |
| Skip animazione layout migliorabile | low |
| Banner duplicate preview mock vs live | low |

## Vincoli

**`do_not_touch`:** gacha mutation logic, banner rates, economy hooks.

## Validator

`validate_project_frontend_b_gacha_flow_audit_v1.py` → **PASS**.
