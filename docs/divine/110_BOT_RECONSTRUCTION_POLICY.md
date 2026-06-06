# v110 PSP PREP — Bot Reconstruction Policy

**Pack**: `MEGA_RELEASE_ACCELERATION_70_v110_PSP_APPLY_AND_LEGACY_CLEANUP_PREP_GATED_NOT_APPLIED`
**Track**: G
**Public sync tag**: `PUBLIC_SYNC_TAG_v110_PSP_APPLY_AND_LEGACY_CLEANUP_PREP_GATED_NOT_APPLIED`

## Regole fondamentali

- `bots_default_disabled`: **true** — bot non si avviano automaticamente.
- `bots_server_scoped`: **true** — bot esistono solo nel contesto di un `server_id`.
- `empty_roster_after_reset_forbidden`: **true** — un bot resettato non può mai presentare roster vuoto in runtime; deve ricevere uno dei due path di ricostruzione.
- `legacy_heroes_in_bot_roster_forbidden`: **true** — niente unit legacy/Day1 LV100 trickle nei roster bot.
- `premium_currency_grant_to_bots_forbidden`: **true** — nessun grant di valuta premium.

## Opzioni di ricostruzione su reset

### Opzione 1 — `starter_roster_seed`
Il bot riceve un roster starter deterministico (5 eroi 3–4 stelle, niente legacy). `premium_grant=false`. `day1_lv100_forbidden=true`.

### Opzione 2 — `controlled_summon_access`
Il bot ottiene ticket summon controllati per ricostruire il roster con catalogo non-legacy. `premium_grant=false`. `day1_lv100_forbidden=true`.

## Bot lifecycle

- `requires_server_id`: true
- `requires_active_bot_profile`: true
- `can_start_only_if_disabled_default_overridden_explicitly`: true

## Invariante preservata

`PROJECT-V108-POSTQA-INVARIANT-NO-BOT-DEFAULT-STARTUP` resta attiva. Il pack v110 **non** applica nulla.

## Riferimento JSON

`/app/data/design/v110_psp_migration/v110_bot_reconstruction_policy_v1.json`
