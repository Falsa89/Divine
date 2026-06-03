# 325 — MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW_PACK_v55

## Verdetto atteso
`MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Tag
`PUBLIC_SYNC_TAG_v55_MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW`

## Tracks
- A Battle Entrypoint Registry v2 Preview (8 modalità)
- B Generic Visual Battle Preview Router Shell (`/visual-battle-preview-router`)
- C Training Visual Preview deeplink (`/training-visual-preview`)
- D Story + multi-mode contracts (design-only)
- E QA smoke matrix (16 flussi, P0–P3)
- F Rollup, validators, docs, markers, suite tuples

## OPTIONAL tuples
- PROJECT-BATTLE-ENTRYPOINT-REGISTRY-v2-PREVIEW
- PROJECT-GENERIC-VISUAL-BATTLE-PREVIEW-ROUTER
- PROJECT-TRAINING-VISUAL-PREVIEW-DEEPLINK
- PROJECT-MULTI-MODE-VISUAL-BATTLE-PREVIEW-CONTRACTS
- PROJECT-VISUAL-BATTLE-ROUTING-EXPANSION-SMOKE-MATRIX
- MEGA-RELEASE-ACCELERATION-4-v55-ROLLUP

## Director approval
- Approvato: B7 (visual battle routing expansion plan) in modalità preview/design/runtime-shell
- NON approvato: B8, economy live, DB writes, reward grant/claim, battle_engine runtime

## Invariants
- 5 MD5-locked core files unchanged
- preferred-unchanged (server.py / combat.tsx / story.tsx) preserved
- Guild War policy autoresolve+replay invariata
- db_writes = 0
- no MONGO_URL / pymongo / motor / redis / filesystem writes
- no validator weakening / no fake PASS / no tuple duplicate
