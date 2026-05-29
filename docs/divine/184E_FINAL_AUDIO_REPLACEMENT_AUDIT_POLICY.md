# 184E — Final Audio Replacement Audit Policy

**Track:** E — Final Audio Replacement Audit Policy
**Verdict:** `TRACK_E_FINAL_AUDIO_REPLACEMENT_AUDIT_POLICY_READY`
**Pack:** `PROJECT_AUDIO_PLACEHOLDER_FOUNDATION`

## Core rule
Nessun build di produzione (`RELEASE_TAG_v1+`) può essere prodotto se qualsiasi entry del registry audio TEST ha `replace_before_release=true` AND `audio_status != 'final_ready'`.

## Authority
- **Audit responsibility:** validator OPTIONAL di questo pack + future `PROJECT_RELEASE_GATE_AUDIT_PACK`
- **Chi può flippare `audio_status` a `final_ready`:**
  - `PROJECT_FINAL_AUDIO_BGM_SFX_KIT_PACK`
  - `PROJECT_FINAL_AUDIO_VO_KIT_PACK` (future voice)
  - `PROJECT_FINAL_AUDIO_MUSIC_KIT_PACK` (future)

## Replacement checklist (10 punti)
1. Audio finale ha stesso `audio_key` del placeholder che sostituisce
2. Audio finale ha stessa o simile `duration_target_ms` (±10%)
3. Audio finale rispetta `volume_hint` del registry o la sostituzione documenta il cambio
4. Audio finale ha stesso `loop` flag
5. Audio finale encoded in formato production (mp3/ogg/aac preferito; wav solo per sfx ultra-short)
6. Audio finale rispetta licensing canonico (no copyrighted material)
7. `manifest.json` aggiornato con `audio_status='final_ready'`
8. `replace_before_release=false` dopo sostituzione
9. File path aggiornato se cambia da `test_placeholders/` a `final/`
10. Audit query `find_all_replace_before_release_true` deve essere ZERO prima del release

## Final audio storage layout (future design)
```
frontend/assets/audio/final/
├── ui/
├── battle/
├── bgm/
├── voice/
└── ambient/
```
- Placeholder files deletion: **REQUIRED** dopo replacement
- Audit query: find file in `test_placeholders/` senza entry final corrispondente → BLOCK release

## Release gate blocking rules
- **BLOCK RELEASE** se qualsiasi entry ha `replace_before_release=true`
- **BLOCK RELEASE** se qualsiasi entry ha `audio_status` ∈ {`test_placeholder`, `placeholder_dev`}
- **BLOCK RELEASE** se `frontend/assets/audio/test_placeholders/` directory contiene ancora file
- **ALLOW RELEASE** solo se 100% `final_ready` AND 100% `replace_before_release=false` AND directory placeholder vuota/rimossa

## QA acceptance criteria pre-release (10 checks)
1. 100% audio entries `final_ready`
2. 100% placeholder files deleted
3. Master volume slider working
4. Mute persistence working
5. Audio pauses on app background, resumes on foreground
6. No autoplay senza user interaction (mobile platform policy)
7. Tutti locked surfaces (VIP/BP/Shop/Item Shop) NON play audio mentre locked
8. Tutti gli audio rispettano `volume_hint` o QA override
9. Battle hit/victory/defeat stinger latency <100ms da event trigger
10. Ambient loop seamless (zero click udibile al loop boundary)

## Verdict
`TRACK_E_FINAL_AUDIO_REPLACEMENT_AUDIT_POLICY_READY` — Policy completa per il release gate audio. Replacement checklist 10 punti. Release blocking rules canoniche. QA acceptance 10 criteri.
