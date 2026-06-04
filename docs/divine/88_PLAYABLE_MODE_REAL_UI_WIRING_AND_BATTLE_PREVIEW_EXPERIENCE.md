# 88 · Playable Mode Real UI Wiring + Battle Preview Experience

## Real UI wiring (categoria "Battle Preview QA (v88)" nel tab Menu)
La categoria appare visivamente nel menu reale dell'app mobile.
Deeplink:
- Storia · Battle Preview → `/playable-mode-battle-preview?mode=story`
- Torre · Battle Preview → `/playable-mode-battle-preview?mode=tower`
- Arena PvP · Battle Preview → `/playable-mode-battle-preview?mode=arena`
- Addestramento · Battle Preview → `/playable-mode-battle-preview?mode=training`
- Raid · Battle Preview → `/playable-mode-battle-preview?mode=boss`

NESSUNA modifica a `story.tsx`/`combat.tsx`/`server.py`/`battle_engine.py` (MD5-lock).

## Battle Preview Experience (v88)
- Autoplay / Pause (toggle): timer locale `setTimeout`, NESSUNA chiamata di rete.
- Speed 1x / 2x (toggle): dimezza il delay locale (1200ms / 600ms).
- Enemy AI hints (badge giallo italic): derivati LOCALMENTE dal payload guardando l'azione futura dell'unità.
- Floating mock damage/heal: toast sopra il portrait, durata `900ms / speed`. Solo visivo, nessun applicazione reale.
- End Preview Summary: card verde mostrata quando `step == totalSteps-1` con esito mock + label NON AUTHORITATIVE · NO REWARD APPLIED.

## Vincoli
- `db_writes=0`, `reward_live=false`, `endpoint_live=false`, `battle_engine_authoritative=false`, `applied_to_live=false`.
- Nessuna mutazione di account/inventory/MMR/story progress/tower completion/event currency/fragments.
- Nessun fetch HTTP, nessun AsyncStorage, nessun import `battle_engine`/`combat`/`story`.
- MD5 lock 8/8 intatti.
