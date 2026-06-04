# 91 — Battle Engine Status/DoT/Targeting Audit (v91 FIXED)

## Pack

`MEGA_RELEASE_ACCELERATION_40_PRE_BATTLE_LOBBY_ENGINE_STATUS_DOT_AND_CANONICAL_ENCOUNTER_SOURCE_PACK_v91_FIXED`

## Scope

Audit **read-only** del battle engine attuale (`backend/battle_engine.py`, MD5-lockato a `151ca35ad3bc35f0a6209cb3744ed440`).

**v91 NON modifica l'engine.** Questo documento e' solo audit/diagnostica per pianificare un futuro pack v92+ che fixa i problemi engine.

## Status / Buff / Debuff catalog (osservato)

| Effetto | Tipo | Categoria | Stato observed |
|---------|------|-----------|----------------|
| Burn | DoT | elemental-fire | Presente; tick per turno; duration variabile |
| Poison | DoT | bio | Presente; tick per turno; stack potenzialmente non gestito |
| Bleed | DoT | physical | Presente; tick per turno; cleanse non chiaro |
| Shock | status | elemental-thunder | Presente; stun probability; duration variabile |
| Frostbite | status | elemental-ice | Presente; speed slow + DoT misto; coerenza tick incerta |
| Curse | status | shadow | Presente; debuff stat + tick possibile |
| Taunt | control | tank | Presente; redirect target dps |
| Cleanse | utility | support | Presente; rimuove status; selettivita' parziale |
| Immunity | passive | various | Presente; flag su unit; pre-check effect application |

## Aree problematiche identificate (read-only)

### 1. DoT tick timing

- Il battle_engine attuale calcola DoT alla fine del turno del bersaglio. Se piu' DoT con stesso source applicano lo stesso turno, l'ordine non e' deterministico.
- Stack: il codice esistente sembra **sovrascrivere** invece che stack. Burn applicato 2 volte in fila puo' resettare la duration invece di sommare i tick.
- Cleanse selettivita': non e' chiaro se cleanse rimuove **TUTTI** i DoT o solo l'ultimo applicato.

### 2. Targeting AoE vs Taunt

- AoE attack ignora Taunt come single-target (corretto). Pero' alcune skill marcate `aoe_partial` (es. cleave 2 target) possono saltare il Taunt e colpire il dps direttamente. Bug noto pre-v91.
- Boss skill marcate `phase_2_aoe` non rispettano Taunt in alcuni casi.

### 3. Immunity vs status

- Immunity flag e' checked PRIMA dell'applicazione, ma alcuni effetti (es. Frostbite parziale come slow + DoT) bypassano il check sulla componente slow.

### 4. Battle report fields

- `total_damage_done` corretto.
- `total_healing_done` SEMPRE 0 sui dataset attuali (vedi findings v16.30 in `test_result.md`): nessun eroe del roster ha `passives.effect.heal_per_turn`.
- `dot_damage_done` non aggregato in report.
- `status_applied_count` non aggregato in report.

## Files coinvolti (read-only)

- `backend/battle_engine.py` (1100+ righe, MD5-lockato)
- `backend/skill_kit_runtime_adapter.py` (se presente; risolve skill effects)
- `frontend/app/combat.tsx` (MD5-lockato; consumer del battle engine via /api/battle/simulate)

## Raccomandazioni v92+ (non eseguite in v91)

1. Introdurre `dot_stack_policy: 'sum_ticks' | 'reset_duration' | 'overwrite'` esplicito per ogni status.
2. Aggiungere `cleanse_policy: 'all' | 'top' | 'by_category'` esplicito.
3. Patch targeting per `aoe_partial` con Taunt awareness.
4. Aggiungere `dot_damage_done` e `status_applied_count` al battle report.
5. Aggiungere passive heal_per_turn ad almeno un eroe support (data-only, no engine change).

## Vincoli rispettati

- File MD5-lockati toccati: 0/8
- db_writes: 0
- reward_live: false
- endpoint_live: false
- battle_engine_authoritative: false (no new logic in v91)

## Verdict v91 FIXED audit

AUDIT_COMPLETE_NO_ENGINE_PATCH_IN_v91_FIXED.
