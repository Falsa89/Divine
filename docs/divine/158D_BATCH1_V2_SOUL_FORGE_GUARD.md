# 158D — Soul Forge Permanent Destruction Guard (Track D)

Verdetto: `TRACK_D_SOUL_FORGE_PERMANENT_DESTRUCTION_GUARD_IMPLEMENTED_SAFE`
File: `frontend/app/soul-forge.tsx`

**Soul Forge resta una modalità valida e intenzionale.** L'utente sacrifica eroi non necessari per ottenere Soul Essence, valuta spendibile in potenziamenti / shop dedicato. Il pack NON rimuove la modalità: la rende sicura.

## Layer di protezione (tutti frontend-only)
1. **Team filter** — eroi nel team attivo già esclusi.
2. **Flag filter** — eroi con `locked`/`favorite`/`native`/`event`/`unique` esclusi dalla griglia disponibili.
3. **High-rarity default protect** — eroi ≥4★ mostrati con badge `🔒` ma NON selezionabili one-tap. Richiedono toggle esplicito “Sblocca selezione eroi 4★+”.
4. **Select-all sicuro** — il bottone Tutti seleziona SOLO eroi 1–3★.
5. **Multi-step confirm modal** — prima del POST `/api/soul/forge`, modale con preview esatta (breakdown per stelle, essenza ottenibile, bilancio finale stimato).
6. **Typed confirmation** — per forge rischiose (≥10 eroi OR presenza di eroi ≥4★) l'utente deve digitare esattamente `CONFERMA` per abilitare il bottone FORGE finale.
7. **One-tap impossibile** — nessun percorso permette distruzione senza modal.
8. **Soft warning** — testo rosso "distrutti PERMANENTEMENTE" sempre visibile.

## Vincoli
- 0 hero deletion outside flow
- 0 user_heroes mutation outside backend
- 0 backend route changes
- 0 DB writes nel pack
