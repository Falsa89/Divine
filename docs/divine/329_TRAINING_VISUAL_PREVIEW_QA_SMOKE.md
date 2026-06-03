# 329 — Training Visual Preview QA Smoke Matrix

Pack: `MEGA_RELEASE_ACCELERATION_5_TRAINING_VISUAL_PREVIEW_LOCAL_DUMMY_SEED_WIRING_PACK_v56`
Track: D
Tag: `PUBLIC_SYNC_TAG_v56_MEGA_RELEASE_ACCELERATION_5_TRAINING_VISUAL_PREVIEW_LOCAL_DUMMY_SEED`

Matrice QA smoke per 16 flussi P0–P3.

## P0
- open /training-visual-preview senza crash
- timeline 5–7 step deterministica
- nessun claim button
- nessun reward
- nessun DB write
- nessuna fetch backend
- nessuna chiamata battle_engine

## P1
- seed locale visibile
- step next funziona, reset funziona
- play/pause cleanup
- generic router mode=training mostra training detail
- missing params no crash

## P2
- layout mobile / safe area / rotation

## P3
- testo italiano sui warning
