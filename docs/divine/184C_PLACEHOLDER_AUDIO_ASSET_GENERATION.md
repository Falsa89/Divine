# 184C — Placeholder Audio Asset Generation

**Track:** C — Placeholder Audio Asset Generation
**Verdict:** `TRACK_C_PLACEHOLDER_AUDIO_ASSET_GENERATION_READY`
**Pack:** `PROJECT_AUDIO_PLACEHOLDER_FOUNDATION`

## Metodo generazione
- **Procedural Python stdlib only:** `wave` + `struct` + `math`
- **No external audio files used:** 0
- **No copyrighted content:** 0
- **No voice acting:** 0
- **No audio engine modifications:** 0
- **Generator script:** `backend/scripts/generate_audio_test_placeholders_v1.py`

## Audio format
```
sample_rate_hz       = 16000
channels             = 1 (mono)
bit_depth            = 16
format               = WAV PCM uncompressed
global_max_amplitude = 0.4 (safety cap)
envelope             = AR (attack-release) for anti-click
```

## 12 file generati

| File | Size | Duration | Placeholder |
|---|---|---|---|
| `test_ui_click.wav` | 1644 B | 50ms | 1500Hz exponential decay |
| `test_ui_confirm.wav` | 3884 B | 120ms | 880Hz tone |
| `test_ui_back_cancel.wav` | 3244 B | 100ms | chirp 660→330Hz |
| `test_ui_error_locked.wav` | 9644 B | 300ms | dissonant 220+233Hz |
| `test_reward_basic.wav` | 16044 B | 500ms | chirp 440→880Hz |
| `test_notification_basic.wav` | 8044 B | 250ms | B5+E6 chord |
| `test_mode_enter.wav` | 12844 B | 400ms | chirp 220→880Hz |
| `test_battle_start.wav` | 22444 B | 700ms | C4-E4-G4 arpeggio |
| `test_battle_hit_soft.wav` | 2604 B | 80ms | LFSR pseudo-noise |
| `test_battle_victory_stinger.wav` | 48044 B | 1500ms | C5-E5-G5-C6 |
| `test_battle_defeat_stinger.wav` | 48044 B | 1500ms | A4→A3 |
| `test_ambient_placeholder_loop.wav` | 128044 B | 4000ms | 110+110.7Hz detuned drone |
| **TOTAL** | **304528 B (297.4 KiB)** | | |

## File size summary
```
total_bytes        = 304528
total_kib          = 297.4
largest_file_kib   = 125.04 (ambient loop)
smallest_file_kib  = 1.61 (ui_click)
average_kib        = 24.78
hard_cap_total     = 1500000 B (1.5 MB) — OK con largo margine
```

## Safety properties
- Tutte le ampiezze cap a 0.4 max int16 — nessun rischio per gli speaker
- AR envelope anti-click su tutti i sample boundaries
- Ambient loop ha fade-in/fade-out edges per loopability seamless
- Total package <300 KiB (negligible binary bloat per il bundle)
- Generazione deterministica (LFSR seed costante) — zero copyright issues
- Chiaramente percepibili come placeholder (pure tones, chirp, deterministic noise) durante QA — impossibile scambiarli per audio finale

## Verdict
`TRACK_C_PLACEHOLDER_AUDIO_ASSET_GENERATION_READY` — 12 WAV procedurali, 297 KiB totali, stdlib only, deterministico, sicuro, chiaramente percepibili come placeholder. AR envelope verificato. Loop seamless.
