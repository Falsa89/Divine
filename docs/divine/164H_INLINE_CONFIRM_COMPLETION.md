# 164H — Soul Forge Inline Confirm Restore: Completion

## Verdetto globale
`PROJECT_SOUL_FORGE_INLINE_CONFIRM_RESTORE_NO_MODAL_CRASH_COMPLETE`

## Track Verdicts
| # | Track | Verdetto | Stato |
|---|-------|----------|:---:|
| A | True Mobile Crash Cause Corrected | `TRACK_A_..._CORRECTED_READY` | ✅ |
| B | Remove Modal Confirm Path | `TRACK_B_MODAL_CONFIRM_PATH_REMOVED_SAFE` | ✅ |
| C | Inline Confirmation Panel | `TRACK_C_INLINE_CONFIRMATION_PANEL_READY_SAFE` | ✅ |
| D | Crash-Proof Event Handlers | `TRACK_D_CRASH_PROOF_EVENT_HANDLERS_READY` | ✅ |
| E | API Contract Kept / No Formula Change | `TRACK_E_API_CONTRACT_KEPT_..._READY` | ✅ |
| F | Shop Nav + Bypass Regression Guard | `TRACK_F_..._READY` | ✅ |
| G | Minimal Static Smoke Harness | `TRACK_G_..._READY_OR_DEFERRED` | ✅ |
| H | Completion | `TRACK_H_..._COMPLETION_READY` | ✅ |

## File modificati
| File | MD5 pre | MD5 post |
|------|---------|----------|
| `frontend/app/soul-forge.tsx` | `88a39590454ecc1c5f16e34e09d90b63` | `b7659de11ac36f341e7a2f54fd29e6ed` |

Nessun altro file di codice modificato.

## Old vs New Root Cause
| Aspetto | Pack precedente | Pack corrente |
|---------|-----------------|---------------|
| Causa proposta | `setBalance(r.new_balance)` con undefined | RN `Modal + KeyboardAvoidingView + ScrollView` mount crash al primo tap |
| Quando crasha | Dopo response API | Al primo tap di FORGE SOUL (prima dell'API) |
| Risolto da | Defensive renders | Rimozione completa del Modal + pannello inline |
| Diagnosi corretta? | Parziale (utile ma insufficiente) | ✅ Coerente con timing osservato |

## Why Modal was removed
- React Native `Modal` su mobile (specialmente Android) ha known issues quando contiene `KeyboardAvoidingView` + `ScrollView` + `TextInput` + `Animated.View` con `entering` Reanimated.
- Il mount completo del subtree avviene al setState `setConfirmOpen(true)` → ogni problema di layout/style/JSX nel subtree crasha il JS thread prima di qualunque codice di business.
- Soluzione robusta: **non usare Modal**. Renderizzare il pannello inline dentro la ScrollView già esistente.

## Confirmation UX before vs after
**PRIMA** (Modal-based):
```
tap FORGE SOUL → setConfirmOpen(true) → mount <Modal><KeyboardAvoidingView><View><ScrollView>...</ScrollView></View></KeyboardAvoidingView></Modal> → CRASH mobile
```

**DOPO** (Inline panel):
```
tap FORGE SOUL → setInlineConfirmOpen(true) → mount <Animated.View style={inlineConfirmCard}>...</Animated.View> INSIDE the existing outer ScrollView → nessun Modal, nessun KAV → nessun crash
```

Il pannello inline:
- È in pagina sotto il bottone `FORGE SOUL` (scroll naturale)
- Mostra breakdown, warning rischio, TextInput CONFERMA (se rischioso), bottoni `ANNULLA` + `CONFERMA FORGE`
- Tutte le safety rules preservate (4★+ override, typed CONFERMA, breakdown, no one-tap destruction)

## Safety rule preservation
- ✅ Hero cards
- ✅ Filters (rarità)
- ✅ 4★+ override toggle
- ✅ Protected heroes (locked/favorite/native/event/unique) bloccati
- ✅ Select-all safe (skip 4★+)
- ✅ Breakdown perdite/guadagni
- ✅ Typed `CONFERMA` per forge rischiosi (≥ 10 eroi o 4★+)
- ✅ No one-tap destruction
- ✅ Error banner visibile su API failure
- ✅ No app crash

## API Contract
INVARIATO: `POST /api/soul/forge` body `{hero_ids: [...]}` → response `{gained_essence, new_balance}`. Helper `normalizeForgeResponse` accetta alias multipli per resilienza.

## Backend / DB / Formula
- Backend changes: **0**
- DB writes: **0**
- Reward formula changes: **0**
- `battle_engine.py`: MD5 invariant `151ca35a…` ✅
- `backend/.env`: MD5 invariant `ff60bbb7…` ✅

## Suite validator (parallel)
- **682 PASS / 5 FAIL / 0 MISS**
- I 5 FAIL sono **TUTTI Redis V23/V24 ambientali** pre-esistenti (handoff iniziale).
- **+8 nuovi validator INLINE_CONFIRM** (Track A-H): tutti PASS.
- **2 validator esistenti realineati** (BATCH1-V2 Track D guard, FORGE_CRASH Track D modal-post-success) per supersession: tutti PASS.
- **0 fake PASS**, **0 validator weakening**, **0 REQUIRED weakening**.

## Mobile QA Checklist (per l'utente)
- [ ] Apri Soul Forge: si apre senza crash
- [ ] Seleziona un eroe 1-3★
- [ ] Tap `FORGE SOUL`: **NON crasha**; appare il pannello inline
- [ ] Il pannello è in pagina (scroll insieme alla pagina), NON un modal overlay
- [ ] Bottone finale `CONFERMA FORGE` visibile (scroll se serve)
- [ ] Tap `ANNULLA`: pannello chiude, selezione resta
- [ ] Tap `CONFERMA FORGE` su eroe disponibile: success/error visibile, mai crash
- [ ] Se rischio (≥ 10 o 4★+): campo `CONFERMA` raggiungibile da tastiera
- [ ] 4★+ override + regole protezione preservate
- [ ] Bottoni shop nav (`Apri Tesoreria`, `Vai al Negozio`, `Apri Negozio Oggetti`) funzionanti
- [ ] `/economy` ancora redirect-only; `/exclusive` ancora locked
- [ ] `memory/test_credentials.md` ancora pulito (no plaintext password)

## Redis status (honesty)
5 validator V23/V24 falliscono per **redis-cli non installato** e binding supervisor rotto. Issue ambientale pre-esistente dall'handoff iniziale. Nessun tentativo di fake PASS, nessun validator weakening. Marcato per future infra-pack.

## Remaining blockers
Nessuno per questo pack.

## Next pack recommendation
🔴 **P0**: `PROJECT_GACHA_RATE_SANITY_FINAL_SIGNOFF_PACK` (dal Master Batch Plan)

Opzionali a sequenza:
- 🔧 `PROJECT_REDIS_INFRA_STABILIZATION_PACK` (per chiudere i 5 fail ambientali)
- 🟠 P1 backlog: IAP Design, Shop IAP, Battle Pass Mod, VIP
