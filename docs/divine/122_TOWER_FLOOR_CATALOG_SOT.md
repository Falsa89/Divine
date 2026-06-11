# 122 — Tower Floor Catalog SOT (Pack 102)

Documento SOT del catalogo Tower a 100 piani launch, introdotto dal `MEGA_RELEASE_ACCELERATION_102_TOWER_100_FLOOR_CATALOG_DETERMINISTIC_ENEMY_TEAMS`.

## Decisione canonica utente

- **Torre launch base = 100 piani.**
- Espansione future patch = **+20 o +30 piani per patch**.
- Il **contenuto del floor è identico** per tutti i player e tutti i server.
- La **progressione resta server-scoped**: S1 separato da S2.
- Enemy team **deterministici**, non random.
- Tutti gli enemy team devono usare **solo hero_id ufficiali, validi, evocabili/player-facing**.
- **NO boss mostri singoli** o boss raid.
- Le boss floor sono **team boss**: team 6v6 con leader boss e difficoltà più alta.
- Piano 5/15/25/.../95 = **mini-spike**.
- Piano 10/20/.../90 = **boss team**.
- Piano 50 e 100 = **major boss team**.

## Catalog version

- `CATALOG_VERSION = "tower_v1_100_launch"`.
- Modulo statico: `backend/data/tower_floor_catalog_v1.py`.
- Import-safe (no DB writes, no side effects).

## Hero ID source

- Sorgente canonica: `backend/data/character_bible.py` (RM1.12 Phase 1).
- Universo utilizzato: **`LAUNCH_BASE_HERO_IDS`** (100 launch heroes ufficiali).
- **Borea / `EXTRA_PREMIUM_HERO_IDS` NON utilizzato** (premium/restricted al lancio, non eligible come enemy team).
- Validazione hero_ids: presence in `CHARACTER_BIBLE_BY_ID` + `release_group == "launch_base"`.

## Distribuzione (snapshot launch)

Esiti del `get_catalog_summary()`:

| Floor type | Count | Floors |
|---|---|---|
| `normal` | 80 | rimanenti |
| `mini_spike` | 10 | 5, 15, 25, 35, 45, 55, 65, 75, 85, 95 |
| `boss_team` | 8 | 10, 20, 30, 40, 60, 70, 80, 90 |
| `major_boss_team` | 2 | 50, 100 |

Floor 50 e 100 sono i due punti chiave: 50 = mid major, 100 = strongest launch (leader rarity 6).

## Enemy team rules

- **TEAM_SIZE = 6**.
- **Nessun hero_id duplicato** nello stesso team.
- Composizione deterministica via `(floor, slot_index)` indexing.
- Slot 0 è sempre il `boss_leader_slot` per i floor `boss_team` e `major_boss_team`.
- Ogni slot ha un `role` canonico assegnato (vedi `SLOT_ROLE_ORDER` / `_BOSS` / `_MINI`).
- Rarity tier scala con floor secondo `_compute_tier(floor)` (curva 1→6).

## Endpoint catalog

- `GET /api/tower/strict/catalog` — summary (auth-free, read-only).
- `GET /api/tower/strict/catalog/floor/{floor}` — detail per floor (1..100), 404 fuori range.

## Wiring preview

L'endpoint `POST /api/tower/strict/battle/preview` (Pack 101) ora include `catalog_floor` letto dal modulo statico. NESSUN reward grant, NESSUNA mutation. Floor 101+ → 404 `FLOOR_OUT_OF_CATALOG_RANGE`.

## Expansion policy

- Pack futuro può aggiungere **+20 o +30 piani per patch**.
- L'espansione richiederà un nuovo modulo `tower_floor_catalog_v2.py` con `CATALOG_VERSION = "tower_v2_120_launch"` o `"tower_v2_130_launch"`, lasciando `v1` immutato per audit storico.
- Migrazione versione: il loader pubblico dovrà esporre la versione corrente con health endpoint e ogni client potrà invalidare cache.
- NESSUNA espansione applicata in Pack 102.

## S1/S2 isolation

- Il **contenuto** del floor è identico cross-server (è contenuto statico).
- La **progression** del player (floor corrente, highest_floor, rewards_claimed) resta server-scoped su `PSP.tower_progress`.
- Smoke E2E verifica: preflight S1 NON crea `PSP.tower_progress` su S2.

## Vincoli (non negoziabili)

- NO invalid/legacy/hidden hero IDs.
- NO true boss monsters in base Tower.
- NO random enemy teams.
- NO tower battle execute live.
- NO tower reward live grant.
- NO `users.gold/users.gems/users.experience` mutation da Tower.
- NO release readiness claim.
- NO `/api/battle/simulate` call dal preview.
