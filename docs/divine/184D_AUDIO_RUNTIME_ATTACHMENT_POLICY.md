# 184D — Audio Runtime Attachment Policy

**Track:** D — Audio Runtime Attachment Policy
**Verdict:** `TRACK_D_AUDIO_RUNTIME_ATTACHMENT_POLICY_READY`
**Pack:** `PROJECT_AUDIO_PLACEHOLDER_FOUNDATION`

## Stato runtime in questo pack
```
run_attached_in_this_pack                 = false
runtime_engine_implementation_in_this_pack = false
current_runtime_engine                    = NONE_INSTALLED
engine_selection_required_before_attach   = true
```

## Feature flags forced OFF
```
AUDIO_ENGINE_ENABLED              = false
AUDIO_PLACEHOLDER_AUDIBLE_IN_QA   = true (when manually run; not in production)
AUDIO_GLOBAL_DISABLED             = true
AUDIO_CANARY_INTERNAL             = false
```

## Future engine candidates
1. **`expo-audio`** (preferred per Expo SDK 51+; nuovo, lighter)
2. **`expo-av`** (deprecated track ma supportato; cross-platform unified)
3. **`react-native-sound`** (fallback se expo audio rimosso)

**Engine selection è nel future pack:** `PROJECT_AUDIO_RUNTIME_ENGINE_SELECTION_PACK`.

## Runtime attach contract (future loader)
1. Read `frontend/assets/audio/test_placeholders/manifest.json`
2. Preload solo `runtime_attached=true` (attualmente nessuno)
3. Register audio con engine usando `audio_key` come identificatore
4. Espone funzione `play(audio_key)` alla UI
5. Rispetta `volume_hint` quando triggera playback
6. Rispetta `loop` flag per ambient_loop entries
7. Pause all su app background; resume su foreground

## Safety constraints (per future runtime)
- ❌ Mai caricare real money SFX (cash register etc.) durante pack experiments
- ❌ Mai autoplay senza user interaction (mobile platform policy)
- ❌ Mai play audio su screens con `VIP_LOCKED_V2` / `BP_LOCKED_V2` / `SHOP_LOCKED_V2` / `ITEM_SHOP_LOCKED_V2` attivi
- ❌ Mai caricare placeholder in production release (`replace_before_release=true` check)
- ❌ Mai hardcoded audio paths (sempre via manifest + audio_key resolution)
- ✅ FAIL SAFE: missing audio_key → silent no-op (mai crash UI)

## HUD visibility requirements (future settings UI)
- Audio settings screen: **required**
- Volume master slider: **required**
- Volume per category: optional
- Mute all toggle: **required**
- Mute persists via `SecureStore`: **required**

## Surfaces NON attached in questo pack
- Tutte le tab routes (home, battle, gacha, heroes, menu)
- Tutte le stack routes player-facing
- Tutti i locked surfaces (Shop, BP, VIP, Item Shop)
- `combat.tsx` (broad refactor vietato)
- `soul-forge.tsx` (Soul Forge PROTECTED)
- `battle_engine.py` / `battle_core.py` (combat runtime intatti)

## Roadmap futura (7 stage)
1. `PROJECT_AUDIO_RUNTIME_ENGINE_SELECTION_PACK` — selezione engine + install lib + smoke screen
2. `PROJECT_AUDIO_LOADER_AND_MANIFEST_CONSUMER_PACK` — loader da manifest.json con audio_key lookup
3. `PROJECT_AUDIO_SETTINGS_UI_PACK` — audio settings UI + master volume + mute persistence
4. `PROJECT_AUDIO_UI_HOOKS_CANARY_PACK` — attach ui_click/confirm/back/error a global UI events
5. `PROJECT_AUDIO_BATTLE_HOOKS_CANARY_PACK` — attach battle stingers a combat phases (NO battle_engine modifications; pure observer pattern frontend)
6. `PROJECT_AUDIO_AMBIENT_LOOPS_CANARY_PACK` — attach ambient_loop a idle screens con fade-in/out
7. `PROJECT_FINAL_AUDIO_BGM_SFX_KIT_PACK` — sostituire tutti i placeholder con final commissioned audio; flip `AUDIO_ENGINE_ENABLED=true`

## Verdict
`TRACK_D_AUDIO_RUNTIME_ATTACHMENT_POLICY_READY` — Policy design-only. Zero runtime audio installation. Future roadmap 7 stage definita. Safety constraints e HUD visibility design definiti.
