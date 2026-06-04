# 95 — Battle Engine Runtime Apply

## Pack

`MEGA_RELEASE_ACCELERATION_44_v95`

## Scope

Applicazione runtime delle policy validate in v94 (precedentemente design-only):

- DoT core: Burn, Poison, Bleed, Shock, Frostbite, Curse;
- Stack policy: `sum_ticks`, `reset_duration`, `overwrite`, `cap_stacks`;
- Cleanse policy: `all`, `top`, `by_category`, `by_priority`, `one_stack`, `remove_status`;
- Immunity: blocca nuove applicazioni, non rimuove esistenti;
- Taunt + fix `aoe_partial` (intercetta) vs aoe pieno (bypass);
- Boss hard-control conversion (Freeze → Speed Down, Stun/Silence → Weaken, Sleep → Slow lieve, Petrify → Defense Break);
- Battle report extension: `dot_damage_done`, `status_applied_count`, `healing_done`, `cleanse_count`, `status_prevented_by_immunity_count`, `taunt_redirect_count`.

## MD5

- **Old MD5** `backend/battle_engine.py`: `5c7e8941bf9469a1c878ecc4aae8db12`
- **New MD5** `backend/battle_engine.py`: `56b6e5261c3b35c421db3202f750d1a6`

MD5 break autorizzato esplicitamente dal pack v95 (`specs/v95_scope_guardrails.json` → `allowed_md5_unlocks.backend/battle_engine.py`).

## Diff summary

1. `process_status_effects(char, v95_counters=None)` — accetta counters opzionali e gestisce DoT su `burn`, `poison`, `bleed`, `frostbite`, `curse`. `frostbite` applica anche un piccolo speed-down una sola volta. `shock` non fa DoT tick (gestito on_action_attempt).
2. `apply_taunt_override` — distingue `aoe_partial` (rispetta Taunt) da aoe pieno (bypass). Aggiorna counter `taunt_redirect_count` quando il target viene cambiato.
3. `execute_skill` — branch status effect estesa per:
   - cleanse (mode `all|top|by_category|by_priority|one_stack|remove_status`);
   - DoT con stack policy + immunity check;
   - hard control (stun/freeze/silence/sleep/petrify) con immunity check e conversione boss;
   - counters aggiornati via `simulate_battle._v95_counters`.
4. `simulate_battle` — inizializza `v95_counters` e li include nel result come `result['v95_battle_report']`, oltre a `total_damage_done`, `total_damage_taken`. Mantiene intatti `team_a_final`, `team_b_final`, `mvp`, `victory`, `turns`, `battle_log`.
5. `_v95_apply_dot_with_stack_policy`, `_v95_apply_cleanse`, `_v95_has_immunity`, `_v95_is_boss`, `_v95_maybe_convert_boss_hardcontrol` — helper additivi.
6. `V95_ENGINE_STATUS_DOT_METADATA['applied_runtime']` = `runtime_apply_active` (era `metadata_only_no_behavior_change`).

## Rollback note

Rollback rapido: ripristinare `backend/battle_engine.py` al MD5 `5c7e8941bf9469a1c878ecc4aae8db12` (v94). `simulate_battle` torna a non emettere `v95_battle_report` ma il resto del payload resta legacy-compatibile.

## Validator coverage

- `backend/scripts/validate_v95_battle_engine_runtime_apply.py`
- `backend/scripts/validate_v95_engine_runtime_regression_tests.py`
- `backend/scripts/test_v95_battle_engine_runtime_status_dot.py` (21 regression test, 21/21 PASS)

## Safety

- `db_writes` = 0
- `reward_live` = false
- nessuna modifica a balance numerico (damage_per_turn e duration sono determinati dai dati delle skill esistenti)
- nessuna mutazione del Character Bible o del roster
