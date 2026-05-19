# Redis HA Decision Plan — V24 (PLAN ONLY)

**Task origin**: `AF2-N-V24-REDIS-HA-DECISION-PLAN`  
**Status**: 📋 **PLAN ONLY** — nessuna mutazione runtime implementata in questa run.  
**Scope**: Definire la strategia di alta disponibilità per il backend Redis che
oggi sostiene il rate-limiting di `/api/affinity/gift-spend` durante Stage 4
Internal Beta (700 utenti, cap 5.000).  
**Production impact**: nessuno — questo è un documento di decisione, non un
deploy.

---

## 1. Stato attuale (post-V23/V24)

| Componente | Versione | Modalità | Note |
|---|---|---|---|
| `redis-server` | 7.0.15 | Standalone, single-node | Avviato via supervisor (`/etc/supervisor/conf.d/redis.conf`), porta 6379, bind 127.0.0.1 |
| Persistenza | OFF | `--save "" --appendonly no` | Scelta deliberata: rate-limit counters sono effimeri |
| `AFFINITY_RATE_LIMIT_BACKEND` | `redis` | Live in Stage 4 | Verificato in V24 (snapshot reale, 4 × 429 con `backend=redis`) |
| Fallback in-memory | Presente | `memory_fallback` | Si attiva se Redis non risponde → counter `af2_ratelimit_redis_fail_open_total` |
| Failure domain | Container singolo | **SPOF** | Stesso pod del backend; container effimero |

### 1.1 Evidenza osservata in V24

- Reinstallo Redis era necessario dopo restart del container: il binario
  `/usr/bin/redis-server` era sparito dal filesystem. Confermato che il
  filesystem del container è **effimero per i pacchetti di sistema**.
- `redis.conf` di supervisor è invece persistito (sotto `/etc/supervisor/conf.d/`).
- Fallback in-memory è esercitato e funzionante (test V23/V22).

---

## 2. Rischi attuali

| ID | Rischio | Severità | Probabilità | Mitigazione attuale |
|---|---|---|---|---|
| R1 | Container restart → binario Redis sparisce | **ALTA** | ALTA | Reinstall manuale o init-script (vedi §5) |
| R2 | Redis crash → contatori azzerati | MEDIA | BASSA | Fail-open al backend memory (counters locali al processo) |
| R3 | Backend pid restart → memory fallback azzera | BASSA | BASSA | Burst window 10s, hour window mitigato da Redis quando UP |
| R4 | Latency Redis > 1s | BASSA | BASSA | `socket_timeout=1.0` + fail-open |
| R5 | Memory pressure su Redis | BASSA | BASSA | Solo zset effimeri, dataset minimo (<100KB) |
| R6 | Split-brain in HA multi-node | N/A | N/A | Non rilevante in standalone |

---

## 3. Opzioni HA valutate

### Opzione A — **Standalone hardenizzato** (status quo + init-script)
- **Costo**: 0 (zero infra)
- **Pro**: Minimo footprint, già operativo, fail-open ben testato
- **Contro**: Resta SPOF
- **Failure handling**: fallback memory in-process

### Opzione B — **Replica primary/secondary** (Redis Sentinel)
- **Costo**: +1 pod Redis + 3 pod Sentinel (≥ 2 vCPU, 256MB RAM totali)
- **Pro**: failover automatico, RTO < 30s
- **Contro**: complessità operativa, ancora SPOF di rete (Sentinel quorum)
- **Sconsigliato**: overhead troppo alto per il dataset effimero di rate-limit

### Opzione C — **Redis Cluster (multi-shard)**
- **Costo**: alto (≥ 6 pod), management complesso
- **Pro**: scalabilità orizzontale
- **Contro**: nessuno shard hot key reale al traffico Stage 4 (700 users)
- **Sconsigliato per Stage 4**: overkill

### Opzione D — **Managed Redis** (AWS ElastiCache / Upstash / Redis Cloud)
- **Costo**: ~ $15-30/mese per istanza minima
- **Pro**: HA gestita, backup, monitoring, scaling, multi-AZ
- **Contro**: dipendenza cloud provider, latenza di rete +1-5ms
- **Raccomandato per Broad Rollout** (P1 quando autorizzato)

### Opzione E — **Fail-open puro + memory persistito**
- **Costo**: 0
- **Pro**: zero infra
- **Contro**: nessuna distribuzione tra pod
- **Sconsigliato in produzione multi-pod**

---

## 4. Decisione raccomandata

| Fase | Soluzione | Quando |
|---|---|---|
| **Stage 4 (NOW)** | **A** — Standalone hardenizzato + fail-open memory documentato | ✅ Live |
| **Pre Broad Rollout** | **D** — Migrazione a Managed Redis (single-AZ minimo) | Plan-only |
| **Broad Rollout** | **D + multi-AZ** | Plan-only, gated da V26 signoff |

**Razionale**: il rate-limit per Stage 4 non richiede HA forte perché il
fallback memory è già esercitato e produce un graceful degradation. Il salto a
Managed Redis va fatto **prima** di moltiplicare il traffico (>700 → broad
rollout), non durante.

---

## 5. Action items concreti

### 5.1 Stage 4 — immediati (NON bloccanti)

- [ ] Aggiungere init-script `/app/scripts/ensure_redis_installed.sh` chiamato
      da supervisor pre-start, che fa `which redis-server || apt-get install -y
      redis-server` (idempotent). Mitiga R1.
- [ ] Documentare la procedura di **manual reinstall** in
      `/app/docs/divine/RUNBOOK_REDIS_RESTART.md`.
- [ ] Aggiungere alarm soft: se `af2_ratelimit_redis_fail_open_total` > 100 in
      1 ora → notify on-call (oggi metric esiste, alarming TBD).
- [ ] Verificare in CI / pre-deploy che `redis-cli ping` ritorni `PONG` dentro
      lo health endpoint del backend (gated, read-only).

### 5.2 Pre Broad Rollout (Plan-only, V26 gate)

- [ ] Procurement Managed Redis (Upstash o ElastiCache, single AZ minimo).
- [ ] Aggiornare `REDIS_URL` da `redis://127.0.0.1:6379/0` a TLS URL.
- [ ] Test di failover su staging (kill primary, verifica fallback memory
      attivato + counters non corrotti).
- [ ] Migrare zset key namespacing: prefix `prod:` vs `stage4:` per evitare
      crossing.
- [ ] Definire TTL massimo per zset (oggi nessun TTL esplicito; aggiungere
      `EXPIRE key 7200`).

### 5.3 Post Broad Rollout (Future)

- [ ] Multi-AZ replica + failover automatico
- [ ] Monitoring Prometheus-style su Redis hit/miss
- [ ] Backup giornalieri (anche se dataset effimero, utile per debug)

---

## 6. Invariants e safety

✅ Nessuna modifica a `battle_engine.py` / `battle_core.py` / `combat.tsx`  
✅ `/api/heroes` count = 100 invariato  
✅ Borea / greek_borea / primordial_gaia → 404 su gift-spend  
✅ Broad rollout / Public Spend UI / STACK-G wiring restano **OFF**  
✅ Nessun restore distruttivo DB production

---

## 7. Blockers aperti

- 🟠 **BLK-REDIS-01**: Container effimero — binario Redis perso a ogni restart.
  Mitigation: §5.1.1 (init-script). Tracked in Blocker Matrix V3.
- 🟢 **BLK-REDIS-02**: Fail-open memory backend è già testato (V23 stress) →
  closed.

---

**Owner**: backend ops  
**Review cadence**: ogni ULTRA-COMBO (V25, V26)  
**Promotion gate**: Managed Redis attivo prima di Broad Rollout (V26).
