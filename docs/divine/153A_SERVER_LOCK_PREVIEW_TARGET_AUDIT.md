# 153A — Track A: Server Lock Preview Target Audit

**Verdict:** `TRACK_A_SERVER_LOCK_PREVIEW_TARGET_AUDIT_READY` · audit

## Target identificato
- File: `/app/frontend/app/servers.tsx` (MD5 pre-pack `26f5c796…`)
- 81 LOC originali
- API calls da rimuovere/modificare:
  - GET `/api/servers` → mantenere come lettura informativa
  - POST `/api/server/select` → **RIMUOVERE** (mutation)
- Success Alert da rimuovere: `Alert.alert('Server Selezionato!', 'Benvenuto!')`
- SafeFeatureCard è riutilizzabile
- Menu entry resta invariato ("Seleziona Server")

## Italian copy obbligatoria
- **Title**: "Selezione Server in aggiornamento"
- **Body**: "La gestione dei profili server è in fase di migrazione. Il cambio server sarà riattivato quando il nuovo sistema sarà pronto."
