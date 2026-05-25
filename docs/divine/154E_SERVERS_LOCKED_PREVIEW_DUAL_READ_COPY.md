# 154E — /servers Locked Preview Dual-Read Copy

**Verdict:** `TRACK_E_SERVERS_LOCKED_PREVIEW_DUAL_READ_COPY_READY` · frontend copy polish

## File modificato
- `/app/frontend/app/servers.tsx`
- Pre-pack MD5: `bb5fbd29db70ab942dc9f79dcfa6694c`
- Post-pack MD5: `4e08d0186ed31785e912b8f69d30e9cb`

## Polish applicato
- Nuova sezione **"Server attuale"**
- Valore placeholder: **"Anteprima dual-read in preparazione"**
- Hint: "Il tuo server attuale resta invariato. Il dettaglio 'server attuale' sarà visibile in sola lettura dopo l'attivazione sicura dell'auth/contract hardening del nuovo sistema."
- Stili aggiunti: `currentServerCard`, `currentServerLabel`, `currentServerValue`, `currentServerHint`
- accessibilityRole="text" + label descrittiva sulla card

## Sicurezza
- 0 nuova fetch introdotta
- 0 select button aggiunto
- 0 mutation call aggiunta
- 0 menu change
- `fake_availability_claim`: **false**
- `new_profiles_live_claim`: **false**
- 0 implicazione di switching attivo

## Anti-reintroduction
Reintroduction risk: **none** — solo testo statico + stili, nessun handler.
