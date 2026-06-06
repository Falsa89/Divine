# v109 SERVER ISOLATION — Core Loader server_id Filter Promotion

**Pack**: `MEGA_RELEASE_ACCELERATION_69_v109_SERVER_ISOLATION_AND_SERVER_ID_FILTER_PROMOTION`
**Track**: C
**Public sync tag**: `PUBLIC_SYNC_TAG_v109_SERVER_ISOLATION_AND_SERVER_ID_FILTER_PROMOTION`

## Esito complessivo

**Nessun loader promosso runtime**. `any_loader_promoted=false`, `filter_applied_anywhere_true=false`.

Motivazione onesta: la promozione runtime di `server_id` come filtro di query richiede prima il pack `v110_PSP_apply` per produrre dati realmente server-scoped (Player Server Profile). Senza PSP, qualsiasi claim `filter_applied=true` sarebbe falso, perché i dati restano account-wide.

## Tabella loader audited

| Loader | File | parses_server_id | filters_server_id | filter_applied_claim | Stato |
|---|---|---|---|---|---|
| user_heroes | `backend/routes/hero_progression.py` | false | false | **false** | account-wide; PSP non applicato (v110) |
| team_formation | `backend/routes/teams.py` / lobby | false | false | **false** | account-wide; PSP non applicato (v110) |
| inventory | `backend/routes/equipment.py` | false | false | **false** | account-wide; PSP non applicato (v110) |
| currencies_wallet | `backend/routes/economy.py` | false | false | **false** | account-wide; PSP non applicato (v110) |
| story_progress | `backend/routes/combat.py` | false | false | **false** | account-wide; PSP non applicato (v110) |
| battle_instance_preview | `backend/routes/v108_authoritative_pre_instance.py` | **true** | false | **false** | echo only; missing server_id → `BATTLE_INSTANCE_SERVER_REQUIRED` |
| battle_instance_resolve | `backend/routes/v108_authoritative_runtime_resolve.py` | **true** | false | **false** | echo only; missing server_id → `BATTLE_RESULT_INSTANCE_REQUIRED` |

## Cosa è stato evitato

- nessuna duplicazione random di dati;
- nessuna migrazione distruttiva;
- nessuna applicazione PSP;
- nessuna pretesa di server isolation tramite solo frontend AsyncStorage;
- nessun `filter_applied=true` falso.

## Safety flags

- `false_server_id_filter_claim`: false
- `fake_PASS`: false
- `release_readiness_claimed`: false

## Riferimento JSON

`/app/data/design/v109_server_isolation/v109_core_loader_filter_promotion_v1.json`
