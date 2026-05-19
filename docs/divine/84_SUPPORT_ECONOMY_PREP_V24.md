# Support / Economy Prep — V24

**Task origin**: `AF2-N-V24-SUPPORT-ECONOMY-PREP`  
**Audience**: Support team (Tier 1 + escalation), Economy ops  
**Scope**: Playbook minimo per gestire ticket relativi a Stage 4 Internal Beta
durante la finestra di osservazione attiva.

---

## 1. Cosa è in produzione adesso (Stage 4)

| Feature | Stato | Visibilità utenti |
|---|---|---|
| Affinity gift-spend canary | ✅ ON | **Solo 700 allowlist QA** |
| Inventory live writes | ✅ ON | Stage1 allowlist subset |
| Affinity points mutation | ✅ ON | Stage1 allowlist subset |
| Rate-limit (Redis) | ✅ ON | Tutti i requests |
| Public Spend UI | ❌ OFF | **Mai visibile** |
| STACK-G battle wiring | ❌ OFF | Affinity NON influenza combat |
| Broad rollout | ❌ OFF | Solo allowlist |

---

## 2. Cosa NON è in produzione

- **Nessun utente reale non-QA** può fare gift-spend visibile in UI.
- **Combat e gacha non sono toccati** da Stage 4. Bug report su combat o gacha
  → NON correlati a Stage 4 → triage normale.
- **Borea / greek_borea / primordial_gaia non sono spendibili** (404 garantito).

---

## 3. Ticket triage cheat-sheet

### 3.1 "Il mio gift non è stato applicato"

1. **Check 1**: l'utente è nella canary allowlist?
   - Allowlist viewer (read-only): `curl /api/affinity/gift-spend/canary-status`
     campo `canary_allowlist_size=700`. La lista è in env
     `AFFINITY_GIFT_CANARY_ALLOWLIST`.
   - Se NO → "Stage 4 è una beta interna QA. La feature non è ancora pubblica."
2. **Check 2**: l'utente ha visto un 429?
   - Verifica nei log applicativi del backend o nel counter
     `af2_ratelimit_429_total`.
   - Se SÌ → "Hai colpito il rate-limit: max 30/min, 240/h, burst 6/10s."
3. **Check 3**: hero_id era Borea?
   - Allora 404 (atteso) — non è un bug.
4. **Check 4**: stesso `idempotency_key` riusato?
   - Allora la transazione è stata deduplicata, è normale, ledger conserva solo
     la prima.

### 3.2 "Vedo un errore 5xx"

- 🚨 **Escalate immediatamente**: deve essere ZERO 5xx in Stage 4.
- Cattura: timestamp UTC, user_id (se loggato), endpoint chiamato, response body.
- Page on-call.

### 3.3 "Vedo Borea/greek_borea in lista heroes"

- 🚨 **Escalate**: invariante violato.
- Cattura: screenshot + payload `/api/heroes` filtrato per id contenente
  `borea`.

### 3.4 "Sono nella allowlist ma ricevo 423"

- L'utente NON è nell'allowlist anche se dovrebbe.
- 423 = utente fuori allowlist o feature flag spent. Verifica
  `AFFINITY_GIFT_CANARY_ALLOWLIST` in `backend.conf`.

### 3.5 "Posso comprare nuovi gift?"

- ❌ NO. Stage 4 NON espone UI di acquisto. Gli spend in beta sono di
  validazione tecnica.

---

## 4. Escalation matrix

| Sintomo | Tier 1 | Tier 2 | On-call |
|---|---|---|---|
| Domanda di prodotto | ✅ | — | — |
| 429 isolato | ✅ | — | — |
| Borea leak in heroes | — | — | 🚨 immediate |
| 5xx error | — | — | 🚨 immediate |
| Spend non applicato (utente in allowlist) | — | ✅ | — |
| Ledger row missing | — | ✅ | — |
| Redis fail-open spike | — | — | ⚠️ se > 100/h |

---

## 5. Economy snapshot (V24)

- **Ledger canary rows**: ~144 (Stage 4 active)
- **Cap totale**: 5.000 transazioni
- **Allowlist size**: 700 utenti QA
- **Inventory writes scope**: Stage1 subset (sottoinsieme allowlist)
- **Unauthorized spend**: 0 osservati in V21→V24
- **Refund queue**: 0 (no refund attivo in Stage 4)

---

## 6. Comandi utili (Tier 2)

```bash
# Status generale
curl -s http://localhost:8001/api/affinity/gift-spend/canary-status | jq .

# Metriche abuse (read-only)
curl -s http://localhost:8001/api/affinity/gift-spend/_admin/metrics-snapshot | jq .

# Ping Redis
redis-cli ping

# Verifica Borea aliases (devono → 404)
curl -X POST http://localhost:8001/api/affinity/gift-spend \
  -H "Content-Type: application/json" \
  -d '{"gift_id":"x","hero_id":"borea","quantity":1,"idempotency_key":"support_check","user_id":"stage4_qa_001"}'
```

---

## 7. SLO impliciti Stage 4

| Metric | Target | Misurazione V24 |
|---|---|---|
| 5xx rate | 0 % | ✅ 0 / ~30 req |
| 429 rate | < 10% nominal | ✅ ~13% solo in burst test indotto |
| Borea 404 hit rate | 100% | ✅ 3 / 3 |
| Canary spend success | ≥ 95% | ✅ 10 / 10 |
| Redis available | ≥ 99% | ✅ 100% durante finestra V24 |

---

**Approval**: Support lead + Economy ops  
**Next review**: V25 (ULTRA-COMBO seguente)
