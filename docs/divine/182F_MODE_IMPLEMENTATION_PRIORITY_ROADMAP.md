# 182F — Mode Implementation Priority Roadmap

**Track:** F — Mode Implementation Priority Roadmap
**Verdict:** `TRACK_F_MODE_IMPLEMENTATION_PRIORITY_ROADMAP_READY`
**Pack:** `PROJECT_FULL_RUNTIME_FEATURE_REALITY_AUDIT_WITH_TEST_ASSET_REGISTRY`

## Priority buckets

### 🔴 P0 — Release Blockers (5 pack)
1. **PROJECT_NO_STAMINA_REMEDIATION_PACK** — rimuovere 5 backend + 5 frontend violations (medium)
2. **PROJECT_AUDIO_PLACEHOLDER_FOUNDATION_PACK** — kit minimo SFX/BGM TEST (medium)
3. **PROJECT_COMBAT_FINALIZE_FOR_RELEASE_PACK** — battle_engine green ma VFX/audio/report (high)
4. **PROJECT_LOGIN_AUTH_HARDENING_PACK** — email verify + password reset (low)
5. **PROJECT_SERVER_PROFILES_LIVE_MULTISHARD_PACK** — SLC_H release candidate gate (high)

### 🟡 P1 — Core Playable Mode Completion (6 pack)
1. Hero progression runtime green
2. Teams/formations finalization
3. Inventory/equipment/forge polish
4. Gacha pity activation design → runtime
5. **Tower of the Hells runtime** (🖋️ sketch recommended)
6. PvP Arena runtime

### 🟡 P2 — Live Modes (12 pack)
1. **Guild War / Fronti del Valhalla MVP** (🖋️ sketch)
2. **Guild Boss / Fame del Behemoth MVP** (🖋️ sketch)
3. **Guild Raid / Furie del Pantheon MVP** (🖋️ sketch)
4. **Territory / Guerra dei Tre Troni MVP** (🖋️ sketch, very_high complexity)
5. **Crepuscolo dei Titani World Boss MVP** (🖋️ sketch)
6. Giudizio delle Stirpi Faction Boss MVP
7. Titanomachia MVP
8. Assalto del Ragnarok MVP
9. Trial / Prove del Pantheon MVP
10. **Housing / Dimora Divina MVP** (🖋️ sketch, very_high complexity)
11. **Event Hub Seasonal Pack** (🖋️ sketch)
12. Rankings / Leaderboards Final

### 🟢 P3 — Polish / Asset / Audio (6 pack)
1. Final Art Heroes (very_high)
2. Final Audio BGM/SFX kit (high)
3. Combat VFX final (high)
4. Story content & voice (very_high)
5. Runes Foundation (medium)
6. Notifications Foundation (medium)

### 🟢 P3 — Monetization Release Unlock Sequence (4 pack)
1. **Shop public UI unlock stage** — depends on 179 Stage 5+
2. **IAP live receipt verifier** — depends on 178 Stage 4+
3. **Battle Pass UI impl + canary** — depends on 180 Stage 5+
4. **VIP UI impl + canary** — depends on 181 Stage 5+

## Modes needing user sketches (10)
guild_war, war_three_thrones, housing, tower, world_boss, guild_raid, sanctuary, event_hub, territory_map, live_multi_panel_modes

## Modes con standard placeholder kit sufficient (15)
daily_guide, mail, plaza, friends, dm, rankings, settings, notifications, trial_pantheon, sigilli_degli_dei, giudizio_di_asgard, cammino_dell_ade, scala_dell_olimpo, troni_dell_eclissi, abisso_del_colosso

## Implementation order recommendation (8 steps)
1. P0 stamina removal + audio foundation + login hardening (parallelizable)
2. P1 hero progression / teams / inventory polish
3. P1 gacha pity activation
4. P1 tower + PvP runtime
5. P2 guild war come prima live mode (with sketch)
6. P2 territory + world boss with sketches
7. P3 audio/art polish + monetization unlock in parallelo
8. P3 housing come ultimo big content drop

## Honest Project Completion Estimate (💥)

```
design_architecture_pct                          = 75%
runtime_playable_pct                             = 38%
release_ready_excluding_graphics_audio_pct       = 32%
release_ready_including_graphics_audio_pct       = 18%
```

### Razionale
- **Design 75%:** strong foundation (16 modes canonical, monetization 178/179/180/181 designed, gacha rates green, artifact Stage 8 canary).
- **Runtime 38%:** solo Soul Forge, Gacha standard, Daily Guide, Divine Weapons sono CANONICAL_RUNTIME_READY. Combat partial. 9+ live modes design-only.
- **Release no-graphics 32%:** stamina violation blocca 6 features, server multi-shard non live, story content vuoto, audio assente.
- **Release con graphics+audio 18%:** finale art + final audio + final cutscenes = lavoro enorme ancora da fare.

## Verdict
`TRACK_F_MODE_IMPLEMENTATION_PRIORITY_ROADMAP_READY` — 5 buckets prioritari, 33 pack proposti, completion estimate brutale ma onesto.
