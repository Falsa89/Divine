# 86 · Raid Boss Playable / Placeholder Schema

Schema **design-only** per raid boss giocabili (`raid_boss_playable_schema_v1.json`) e relativo catalogo placeholder (`raid_boss_placeholder_catalog_v1.json`).

## Vincoli
- `design_only = true`
- `runtime_attached = false`
- `reward_grant_attached = false`
- `obtainable = false`
- `show_in_summon = false`
- Frammenti `grant_allowed=false`, `show_in_inventory=false`
- Nessun real boss fragments grant, nessun real playable boss unlock, nessun final_numbers
- Nessun DB write, nessun endpoint live

## Catalogo placeholder iniziale
- `raid_boss_placeholder_001` (Demon/Fire/SSR)
- `raid_boss_placeholder_002` (Dragon/Water/UR)

Entrambi includono forma giocabile placeholder con skill placeholder e modello frammenti bloccato.
