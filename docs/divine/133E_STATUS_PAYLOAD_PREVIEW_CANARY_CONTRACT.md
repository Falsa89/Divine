# 133E — STATUS PAYLOAD PREVIEW CANARY CONTRACT

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_K` — Track E
**Verdict**: `TRACK_E_STATUS_PAYLOAD_PREVIEW_CANARY_CONTRACT_NO_LEAKAGE`
**Marker JSON**: `/app/data/design/status_effects/project_k_status_payload_preview_canary_contract_v1.json`
**Validator**: `/app/backend/scripts/validate_project_k_status_payload_preview_canary_contract_v1.py`

---

## Obiettivo

Definire il contratto del payload `status_envelope_preview` per la modalità canary e, **in modo non negoziabile**, verificare in-process che il payload non venga mai esposto live con flag OFF.

## Endpoints auditati

| Endpoint | Atteso | Osservato |
|----------|--------|-----------|
| `GET /api/heroes` | nessun `status_envelope_preview` | ✅ 0 leak |
| `GET /api/heroes/borea` | nessun leak | ✅ 0 leak |
| `GET /api/heroes/greek_borea` | nessun leak | ✅ 0 leak |
| `GET /api/server-profiles/select` | nessun leak (503 disabled) | ✅ 0 leak |
| `GET /api/housing/preview` | nessun leak (503 disabled) | ✅ 0 leak |

## Contratto canary

Qualora in futuro Track B (o pack successivi) applicasse cablaggio flag-gated, il payload `status_envelope_preview` potrà essere incluso **solo** nel contesto dry-run/canary, **mai** nel default live con flag OFF. Il presente contratto serve da barriera permanente: il validator continuerà a fallire qualora il payload trapelasse live.

## Conformità ai guardrail

- ✅ Nessuna mutazione live del payload con flag OFF.
- ✅ Nessuna modifica UI / frontend.
- ✅ Verifiche eseguite contro il backend reale (`127.0.0.1:8001`).
