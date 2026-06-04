# 92 — Avatar Placeholder Dev Registry (v92)

## Pack

`MEGA_RELEASE_ACCELERATION_41_LIVE_EVENTS_GUILD_MODE_TESTABILITY_AND_AVATAR_PLACEHOLDER_PACK_v92`

## Scopo

Registrare avatar **placeholder/dev only** per testare modalita' che richiedono avatar specifici non ancora finali. Servono per:
- posizione
- layout
- movement
- selection
- lobby
- combat / world map presence
- guild / live UI

## Avatar registrati (7)

| Avatar ID | Label | Categoria | Usage |
|-----------|-------|-----------|-------|
| `player_avatar_hd_base_dev` | Player HD Avatar (base dev) | player_hd | home/profile/sanctuary test |
| `player_war_avatar_mini_base_dev` | Player War Mini Avatar | player_war_mini | territory + war avatar mode |
| `guild_war_avatar_base_dev` | Guild War Avatar | guild_war | gvg lobby test |
| `event_avatar_base_dev` | Event Avatar | event | event avatar mode test |
| `hero_room_chibi_avatar_base_dev` | Hero Room Chibi Avatar | hero_room_chibi | sanctuary chibi test |
| `raid_boss_avatar_placeholder_dev` | Raid Boss Avatar | raid_boss | raid lobby/visual test |
| `faction_boss_avatar_placeholder_dev` | Faction Boss Avatar | faction_boss | faction boss lobby/visual test |

## Regole assolute

| Flag | Valore |
|------|--------|
| `placeholder_dev_only` | true |
| `final_asset_ready` | false |
| `production_asset` | false |
| `do_not_treat_as_canonical` | true |
| `no_monetization` | true |
| `no_cosmetic_unlock` | true |
| `no_inventory_grant` | true |

## Cosa non sono

- NON sono asset finali.
- NON sono direzione artistica autoritativa.
- NON sono unlock cosmetici.
- NON vengono trattati come Character Bible.
- NON sono prodotti per la pubblicazione.

## Cosa sono

Segnaposti **dev-only** per:
- testare il flow delle modalita' che richiedono avatar prima che gli asset definitivi arrivino
- validare layout/posizionamento UI
- validare la pipeline avatar (selection -> lobby -> combat)
- non bloccare il testing in attesa del team art

## Vincoli rispettati

- `db_writes`: 0
- `reward_live`: false
- `ranking_live`: false
- `final_asset_import`: false
- `production_exposure`: false
