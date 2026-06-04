# 92 — Live/Guild/Special Mode Testability Audit (v92)

## Pack

`MEGA_RELEASE_ACCELERATION_41_LIVE_EVENTS_GUILD_MODE_TESTABILITY_AND_AVATAR_PLACEHOLDER_PACK_v92`

## Obiettivo

Rendere testabili in QA/preview tutte le modalita' live/guild/time-gated/avatar-based, non solo le 5 core (Storia/Torre/Arena/Training/Raid).

## Modalita' auditate (15)

### Core (5) — TESTABILI DIRETTAMENTE

| Mode | Status | QA path |
|------|--------|---------|
| Storia | TESTABLE | `/pre-battle-lobby?mode=story` |
| Torre degli Inferi | TESTABLE | `/pre-battle-lobby?mode=tower` |
| Arena PvP | TESTABLE | `/pre-battle-lobby?mode=arena` |
| Addestramento Eroico | TESTABLE | `/pre-battle-lobby?mode=training` |
| Raid Cooperativi | TESTABLE | `/pre-battle-lobby?mode=boss` |

### Live / Eventi (3)

| Mode | Time gate | Blocker | Soluzione v92 |
|------|-----------|---------|---------------|
| Eventi Live (generico) | per-event scheduled | finestra non aperta | QA Hub + simulate window open |
| Crepuscolo dei Titani | lun/mer/ven 20:30-21:30 | finestra non aperta + non wired | QA Hub + simulate + pre-entry lobby |
| Assalto del Ragnarok | daily 11-12 + 19-20 | finestra non aperta + non wired | QA Hub + simulate + pre-entry lobby |

### Guild / Live Cooperativa (3)

| Mode | Requirements | Blocker | Soluzione v92 |
|------|-------------|---------|---------------|
| Guerra tra Gilde | gilda + scheduled + avatar gw | gilda live + finestra + avatar non finale | QA Hub + simulate + avatar placeholder + pre-entry |
| Raid di Gilda | gilda + scheduled | non wired + gilda required | QA Hub + simulate + pre-entry |
| Boss del Server | weekly reset | non wired + scheduled | QA Hub + simulate + pre-entry |

### Faction / Territory (2)

| Mode | Requirements | Blocker | Soluzione v92 |
|------|-------------|---------|---------------|
| Boss di Fazione | scheduled + faction | wire pending + finestra | QA Hub + simulate + avatar boss placeholder |
| Conquista Territori | guild + war avatar + scheduled wave | avatar war non finale + guild + scheduled | QA Hub + simulate + war avatar placeholder |

### Avatar Modes (2)

| Mode | Asset blocker | Soluzione v92 |
|------|---------------|---------------|
| Modalita' War Avatar | war avatar asset non finale | war avatar placeholder dev (`player_war_avatar_mini_base_dev`) |
| Modalita' Event Avatar | event avatar asset non finale + scheduled | event avatar placeholder dev (`event_avatar_base_dev`) |

## Schema classificazione

Ogni modalita' nell'inventory ha questi campi:

- `exists_in_ui`, `exists_in_route`
- `time_gated`, `guild_required`, `avatar_required`
- `battle_required`, `pre_battle_required`
- `encounter_source_type`
- `currently_testable`, `blocker_reason`
- `qa_preview_path_needed`, `qa_preview_path`

## Conteggio finale

- Total modes: **15**
- Currently testable direttamente: **5**
- Bloccate da time-gate / asset / wiring: **10**
- Risolte da v92 (testabili via QA hub): **10**

## Vincoli rispettati

- `db_writes`: 0
- `reward_live`: false
- `ranking_live`: false
- `event_currency_live`: false
- `guild_score_mutation`: 0
- Production time-gate override: NO (solo QA)
- Production UI exposure: NO
- Random opponents: NO (policy v91 esteso a live/guild)
