# 518 · MEGA_RELEASE_ACCELERATION_37 · v88

**Pack:** `MEGA_RELEASE_ACCELERATION_37_PLAYABLE_MODE_REAL_UI_WIRING_AND_BATTLE_PREVIEW_EXPERIENCE_PACK_v88`
**Verdict:** `MEGA_RELEASE_ACCELERATION_37_PLAYABLE_MODE_REAL_UI_WIRING_AND_BATTLE_PREVIEW_EXPERIENCE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Scope
- Real UI wiring: nuova categoria "Battle Preview QA (v88)" nel Menu mobile reale, 5 deeplink.
- Battle Preview Experience: autoplay/pause/speed 1x-2x, enemy AI hints, floating mock damage/heal toast, end-summary card.
- 5 raid boss visual preview profiles design-only (Jormungandr, Fenrir, Apophis, Yamata no Orochi, Crono).
- 4 validator v88 + rollup.

## Vincoli rispettati
- `db_writes=0`, `reward_live=false`, `endpoint_live=false`, `battle_engine_authoritative=false`, `applied_to_live=false`.
- Nessuna mutazione: account, inventory, MMR, story progress, tower completion, event currency, fragments.
- Nessun fetch HTTP, nessun AsyncStorage, nessun import `combat.tsx`/`story.tsx`/`battle_engine`.
- MD5 lock 8/8 intatti.
