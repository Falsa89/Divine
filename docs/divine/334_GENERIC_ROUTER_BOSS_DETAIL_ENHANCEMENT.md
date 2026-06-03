# 334 — Generic Router Boss Detail Enhancement

Pack: `MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE_PACK_v57`
Track: C
Tag: `PUBLIC_SYNC_TAG_v57_MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE`

Quando `mode=boss`, il router generico `/visual-battle-preview-router` mostra un blocco dettaglio:
- "Boss Preview Details"
- stato: `preview_shell_v57`
- `boss_family_id`, `boss_display_name`, `boss_phase_preview` se presenti
- disclaimer no backend / no battle_engine / no reward
- nessun fetch
- comportamento per Material Raid e Training INVARIATO
- no crash su param mancanti
