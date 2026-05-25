# 153D — Track D: Locked Copy & 503 Handling

**Verdict:** `TRACK_D_SERVER_PROFILE_LOCKED_COPY_AND_503_HANDLING_READY`

## Copy presente nella schermata
- Banner title: **"Selezione Server in aggiornamento"**
- Banner body: **"La gestione dei profili server è in fase di migrazione. Il cambio server sarà riattivato quando il nuovo sistema sarà pronto."**
- Section title: "Stato nuovo sistema"
- Card 503 subtitle: "Servizio profili server temporaneamente disabilitato."
- Card 503 lock reason: "Il nuovo endpoint è gated (HTTP 503). In attesa delle firme di abilitazione runtime e preview."
- Footer: "Nessuna azione di selezione server disponibile in questa fase. Il tuo server attuale resta invariato…"

## 503 handling
- Stati gestiti: `loading`, `preview_503`, `unavailable`, `live`
- Cleanup `alive` flag su unmount per prevenire setState dopo unmount
- Nessun retry storm
- Nessun crash se servizio offline

## Anti-claim
- `fake_availability_claim`: **false**
- `new_profiles_live_claim`: **false**
