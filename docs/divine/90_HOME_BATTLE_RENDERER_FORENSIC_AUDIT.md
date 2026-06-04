# 90 — Forensic Audit Home Battle Renderer (v90)

## Pack

`MEGA_RELEASE_ACCELERATION_39_RESTORE_HOME_BATTLE_RENDERER_AND_REAL_MODE_ROUTING_PACK_v90`

## Esito audit

**OLD RENDERER TROVATO NEL REPO CORRENTE** — Non era stato perso. Era gia' presente, gia' MD5-lockato, gia' wired al backend.

## Renderer Home battle reale

| Campo | Valore |
|-------|--------|
| File | `frontend/app/combat.tsx` |
| Componente | `CombatScreen` (default export) |
| Righe | 1848 |
| MD5 lock | `fc792a05b2ada6e677d80400732ae5c3` |
| Stato | Presente, intatto |

## Architettura interna riusata

| Aspetto | Componente / file |
|---------|-------------------|
| Sprite eroi/nemici | `frontend/components/BattleSprite.tsx` (889 righe) |
| Background battlefield | `frontend/components/ui/battleBackgrounds.ts` -> `pickBattleBackground` / `preloadBattleAsset` / `BattleBgResult` |
| Layout posizioni | `frontend/components/battle/motionSystem.ts` -> `buildBattleLayout` / `getHomePosition` |
| Animazioni | `frontend/components/battle/heroBattleAnimations.ts` (398 righe) |
| Debug overlay | `frontend/components/battle/BattleDebugOverlay.tsx` |
| Loading screen | `frontend/components/battle/BattleLoadingScreen.tsx` |
| Post-battle summary | `frontend/components/battle/PostBattleSummary.tsx` + `buildPostBattleSummary.ts` |
| Asset eroi greci | `frontend/components/ui/hopliteAssets.ts` + `hopliteAssetManifest.ts` |

## Caricamento dati reale

- `teamA` (player team) — caricato in `startBattle()` (riga 314) via `apiCall('/api/battle/simulate', { method: 'POST' })`, campo `team_a_final`.
- `teamB` (enemy team) — stesso endpoint, campo `team_b_final`.
- `battleBg` (background) — risolto da `pickBattleBackground` deterministico.
- `bfRect` (battlefield anchor) — misurato via `onLayout`.

L'endpoint `/api/battle/simulate` esiste gia' in `backend/battle_engine.py` riga 1030 (MD5-lockato).
**v90 NON crea nuovi endpoint, NON modifica l'engine, NON tocca i file lockati.**

## Routing Home originale

| Trigger | Route | Stato |
|---------|-------|-------|
| PlayShield Home (storico) | `/combat` | Indirezionato in v28 a `/story` con commento esplicito che vieta ripristino diretto senza pack dedicato |
| Direct deeplink dev/QA | `/combat` | Attivo |
| Menu modalita' (v88) | `/playable-mode-battle-preview?mode=X` | **SBAGLIATO** — mock parallelo |
| Menu modalita' (v90) | `/combat?mode=X` | **NUOVO — corretto** |

## Cosa era sbagliato in v86-v89

v86-v89 hanno costruito un sistema **parallelo** di preview tecnica (`/playable-mode-battle-preview`) invece di riusare `/combat`. Hanno usato:

- griglia 3x3 statica con sprite placeholder
- card tecniche / letter portrait al posto del battlefield
- nessuna integrazione con `buildBattleLayout` / `getHomePosition`
- nessuna integrazione con `pickBattleBackground` reale
- nessuna chiamata a `/api/battle/simulate`
- nessuna animazione / sprite states

Il renderer reale `combat.tsx` era **gia' completo** e **gia' funzionante** — bastava ricollegare i bottoni.

## Piano di ripristino eseguito (v90)

Unico file modificato: `frontend/app/(tabs)/menu.tsx`.

1. **Aggiunta nuova categoria** `Battaglia (Renderer Reale v90)` con 5 entry che puntano a `/combat?mode=<story|tower|arena|training|boss>`.
2. **Marcata vecchia categoria** v88 come `Battle Preview (Wireframe Deprecato v88)` con gradient grigio per segnalare visivamente che e' wireframe diagnostico, non gameplay.

Nessun nuovo componente. Nessun nuovo mock. Nessuna mutazione live.

## Vincoli rispettati

- `db_writes` = 0
- `reward_live` = false
- `endpoint_live` (nuovo) = false
- `battle_engine_authoritative` (nuovo) = false
- File MD5-lockati toccati = 0/8
- Fake PASS = 0
- Validator indeboliti = 0

## Verdict

`MEGA_RELEASE_ACCELERATION_39_RESTORE_HOME_BATTLE_RENDERER_AND_REAL_MODE_ROUTING_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`
