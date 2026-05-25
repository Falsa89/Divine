# 160B — Soul Forge High-Rarity Override Fix (Track B)

Verdetto: `TRACK_B_SOUL_FORGE_HIGH_RARITY_OVERRIDE_FIXED_SAFE`
File: `frontend/app/soul-forge.tsx` (`94da10c6...` → `152e1fbd...`)

## Cosa cambia
- **Tap su eroe 4★+ senza override** → mostra Alert nativo con CTA “Sblocca ora” che attiva l'override.
- **Banner di stato prominente** quando l'override è attivo (sopra la griglia eroi).
- **Toggle label aggiornata** in “Permettimi di sacrificare anche eroi 4★+ (rischio alto)” / “Sacrifica anche eroi 4★+ — ATTIVO”.

## Cosa NON cambia (invarianti V2)
- Protezione di default per 4★+ ✅
- Eroi team / locked / favorite / native / event / unique sempre bloccati ✅
- Select-all seleziona solo 1–3★ ✅
- Typed CONFERMA per forge rischiose ✅
- Breakdown esatto nel modal ✅
- 0 backend changes / 0 reward formula / 0 hero deletion / 0 user_heroes mutation
