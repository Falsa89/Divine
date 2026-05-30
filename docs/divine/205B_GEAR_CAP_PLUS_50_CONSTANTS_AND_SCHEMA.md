# 205B — GEAR_CAP CONSTANTS AND SCHEMA

**Track**: B | **Verdict**: `TRACK_B_GEAR_CAP_CONSTANTS_AND_SCHEMA_READY`

## Cap canonici

- `GEAR_CAP_CANONICAL = 50`
- `GEAR_CAP_LEGACY_TO_REPLACE = 20` (debt marker; mai cancellato in questo pack)
- `GEAR_CAP_MIN = 0`

## Stage canonici

| stage_id | label_it    | min | max | unlock_via                                                                  |
|----------|-------------|-----|-----|-----------------------------------------------------------------------------|
| early    | Avvio       | 0   | 10  | hero_level_or_ascension_low                                                 |
| mid      | Intermedio  | 11  | 20  | hero_level_mid + ascension_unlock                                           |
| late     | Avanzato    | 21  | 35  | forge_enhance + materials_late                                              |
| endgame  | Endgame     | 36  | 50  | forge_reforge + endgame_materials + costellazione_gate_optional             |

## Slot canonici

`weapon`, `armor`, `helm`, `boots`, `gloves`, `accessory`.

## Frontend exports

`GEAR_CAP_CANONICAL`, `GEAR_CAP_LEGACY_TO_REPLACE`, `GEAR_STAGED_CAPS`,
`GEAR_SLOTS`, `resolveGearStage(level)`.
