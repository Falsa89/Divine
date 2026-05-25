# 155E — Server Selection Capacity & Maintenance Rules Spec

**Verdict:** `TRACK_E_SERVER_SELECTION_CAPACITY_MAINTENANCE_RULES_SPEC_READY` · design-only

## Legacy behavior preservato
Legacy `POST /api/server/select` (in `economy.py`) preserva: 404 not found · 400 maintenance · 400 capacity · 401 unauthorized. **Deve restare intatto fino a nuovo endpoint live.**

## New state taxonomy
| State | Selectable | Note |
|---|---|---|
| online | ✅ | verde |
| full | ❌ | badge PIENO, reservation futura |
| maintenance | ❌ | badge MANUTENZIONE, account_level resta visibile |
| new | ✅ | badge NUOVO |
| unknown | ❌ | grey, retry prompt |

## Disabled response contract
- full → 400 `capacity` "Server pieno"
- maintenance → 400 `maintenance` "Server in manutenzione"
- unknown → 503 `unavailable`

## Preview allowed durante maintenance: ✅
Envelope mantiene profilo, `select_blocked=true`, notice "Maintenance in corso; il tuo progresso è salvo".

## Account profile quando server unavailable
Show last known `account_level` + `last_played_at` da cached `server_profiles`. Mai mostrare dati >24h senza timestamp esplicito.

## Gates futuri server opening
`PROJECT_SECOND_SERVER_OPENING_APPROVAL` (già gated) + capacity headroom + dual-write live + canary.
