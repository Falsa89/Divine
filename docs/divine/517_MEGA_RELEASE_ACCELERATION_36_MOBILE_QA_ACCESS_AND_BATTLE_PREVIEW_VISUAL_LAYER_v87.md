# 517 · MEGA_RELEASE_ACCELERATION_36 · v87

**Pack:** `MEGA_RELEASE_ACCELERATION_36_MOBILE_QA_ACCESS_AND_BATTLE_PREVIEW_VISUAL_LAYER_PACK_v87`
**Verdict:** `MEGA_RELEASE_ACCELERATION_36_MOBILE_QA_ACCESS_AND_BATTLE_PREVIEW_VISUAL_LAYER_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Scope
- Hub QA mobile `/mobile-qa-battle-preview` con 6 link diretti alle modalità preview v86.
- Visual layer su `playable-mode-battle-preview`: portrait placeholder, HP bar locali reattive, turn highlight, bersaglio del turno.
- Catalogo portrait placeholder design-only.
- 4 validator v87 + rollup.

## Vincoli rispettati
- `db_writes=0`, `reward_live=false`, `endpoint_live=false`, `battle_engine_authoritative=false`, `applied_to_live=false`.
- Nessuna mutazione: account, inventory, MMR, story progress, tower completion, event currency, fragments.
- Nessun fetch HTTP, nessun AsyncStorage, nessun import `combat.tsx` / `story.tsx` / `battle_engine`.
- MD5 lock 8/8 intatti.
