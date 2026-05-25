# 158C — Artifact/Constellation Surface Lock (Track C)

Verdetto: `TRACK_C_ARTIFACT_CONSTELLATION_SURFACE_LOCKED_TO_PREVIEW_SAFE`
File: `frontend/app/artifacts.tsx` (riscritto come redirect-only screen)

## Comportamento
Utenti che arrivano a `/artifacts` (deep link, vecchio bookmark) vedono uno schermo informativo per ~50ms e vengono immediatamente reindirizzati a `/artifacts-preview` (locked, read-only).

Tutta la logica originale (pull/pull10/fuse/equip) e i bottoni live non sono più raggiungibili dal frontend.

## Backend
Le route `/api/artifacts/*` rimangono invariate (nessuna cancellazione). Solo il frontend filtra l'accesso.

## Coerenza prodotto
- Artifact = collezione account-wide futura (non equipment, non divine weapon).
- Artefatti senza eroe associato (es. Santo Graal, Occhio di Ra) sono `future_reserved`.
