# 327 — Training Visual Preview Local Timeline

Pack: `MEGA_RELEASE_ACCELERATION_5_TRAINING_VISUAL_PREVIEW_LOCAL_DUMMY_SEED_WIRING_PACK_v56`
Track: B
Tag: `PUBLIC_SYNC_TAG_v56_MEGA_RELEASE_ACCELERATION_5_TRAINING_VISUAL_PREVIEW_LOCAL_DUMMY_SEED`

La timeline locale 5–7 step per Training Visual Preview è deterministica a partire dal `seed = training-alpha-v56`.

## Campi richiesti per step
`step_index`, `actor_side`, `actor_label`, `action_key`, `target_label`, `floating_text_preview`, `hp_delta_preview`, `pose_hint`, `vfx_hint`, `duration_ms`

## UI elementi
- step corrente (indice + descrizione)
- placeholder team / enemy
- action label e hp delta preview
- floating text preview
- guardrails visibili (db_writes=0, result_authoritative=false, battle_engine_runtime_used=false)
- warning italiani: "Preview visuale locale non autoritativa", "Nessun reward verrà assegnato"
- pulsanti: Step successivo, Reset, Apri router generico, Indietro
- opzionale Play/Pause con cleanup obbligatorio del timer

## Vincoli
Deeplink-only. No backend. No `combat.tsx` import. No Reanimated. No claim.
