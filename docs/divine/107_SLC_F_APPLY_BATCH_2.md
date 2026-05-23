# 107 — SLC-F APPLY BATCH-2 (mixed/account-wide route patch gated apply — SAFE NO-OP)

> **Verdict finale:** `SLC_F_BATCH_2_APPLIED_SAFE`
> **Tipo apply:** **SAFE NO-OP** — tutti i candidati Batch-2 deferiti per ragioni canoniche SLC-F (skip > unsafe patch).
> **Progress globale:** **90% → ~92%**
> **Modalità:** APPLY GATED — BATCH-2 SOLO. Nessuna espansione di scope. Nessuna modifica di codice runtime. AF2-N, Character Bible, combat/battle e Housing completamente preservati.

---

## 1. Executive Verdict

✅ **PASS** — La Batch-2 SLC-F (route mixed/account-wide) è stata completata come **safe no-op apply**: a seguito dell'audit pre-apply read-only, **tutti e 4** i candidati canonici Batch-2 (`push_notifications`, `cosmetics`, `economy`, `game_data`) sono stati classificati come **SKIP** per ragioni esplicite di policy SLC-F. Nessun file di codice è stato modificato. Tutti gli invarianti runtime sono preservati. La suite master è verde a 343/343.

Questo risultato è **conforme** alla GUARDRAIL principale del pacchetto:

> *"A skipped route is better than an unsafe route patch."*

| Voce | Atteso | Osservato | Esito |
|---|---|---|---|
| Authorization markers (`SLC_F_BATCH_2_APPLY_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=BATCH_2_ONLY`) | presenti | presenti | ✅ |
| Suite master | PASS | **343/343 PASS** (era 342 + nuovo validator) | ✅ |
| Nuovo validator `SLC-F-BATCH-2-POST-APPLY` | PASS | PASS (errors=0) | ✅ |
| Pre-apply audit completato prima di code-change | sì | sì (e nessun code-change effettuato) | ✅ |
| Canonical Batch-2 classification source citata | sì | sì (vedi §5) | ✅ |
| Candidate route audit table prodotta | sì | sì (vedi §6) | ✅ |
| Rollback gated creato prima dell'apply | sì | sì (refusa exit=2 senza marker) | ✅ |
| Invarianti API runtime | preservati | preservati | ✅ |
| AF2-N canary state | preservato | identico (allowlist=2500, cap=50000) | ✅ |

---

## 2. Authorization Markers Detected

```env
SLC_F_BATCH_2_APPLY_APPROVAL=true        ✅
SLC_F_APPLY_BATCH_SCOPE=BATCH_2_ONLY     ✅
```

Forniti dall'utente nel messaggio di task. Nessun secondo apply marker spurio rilevato.

---

## 3. Previous Batch-0/1 e Batch-1B State Confirmation

| Checkpoint | Marker file | Apply ID | Esito |
|---|---|---|---|
| `SLC_F_BATCH_0_1_APPLIED_SAFE` | `slc_f_batch_0_1_apply_marker_v1.json` | `slc_f_batch_0_1_20260523T173754Z_27b1b737` | ✅ presente |
| `SLC_F_BATCH_1B_APPLIED_SAFE` | `slc_f_batch_1b_apply_marker_v1.json` | `slc_f_batch_1b_20260523T175058Z_2cf0584c` | ✅ presente |
| `SLC-G COMMIT-A` | `slc_g_default_s1_migration_apply_result_v1.json` | `slc_g_commit_a_20260523T143803Z_4600ac04` (`migration_applied=True`) | ✅ preservato |
| Helper `backend/utils/server_scope.py` | presente, exports `ensure_server_scope` + `LEGACY_DEFAULT_SERVER_ID="s1"` | — | ✅ |
| Suite baseline prima del task | 342 PASS / 0 FAIL / 0 MISS | — | ✅ |

Verifica di preservazione: tutti i file Batch-0/1 e Batch-1B contengono ancora `from utils.server_scope import ensure_server_scope` (`items`, `forge`, `achievements`, `level_sharing`, `social`, `soul_forge`, `artifacts`, `guild`).

---

## 4. Git Status Before / After

- **HEAD prima del task:** `fa44754`
- **HEAD dopo il task:** `fa44754` (nessun auto-commit triggerato; solo marker e script aggiunti)
- **File codice modificati (esclusi marker/script/doc):** 0
- **File aggiunti (non-codice):**
  - `data/design/system_safety/slc_f_batch_2_apply_marker_v1.json`
  - `backend/scripts/rollback_slc_f_batch_2.py`
  - `backend/scripts/validate_slc_f_batch_2_post_apply_v1.py`
  - `docs/divine/107_SLC_F_APPLY_BATCH_2.md`
  - `data/design/server_lifecycle/_slc_f_batch_2_post_apply_v1_result.json` (validator output)
- **File suite runner modificato (+1 riga OPTIONAL):**
  - `backend/scripts/run_hero_skill_kit_validator_suite.py`

---

## 5. Canonical Batch-2 Classification Source

**Fonte canonica primaria (route classification):**
- `/app/data/design/server_lifecycle/slc_f_route_scope_inventory_v1.json`
  - chiave `scope_classes`: `["account_wide", "server_bound", "mixed_account_owned_server_equipped", "global_catalog_readonly", "unsafe_unknown"]`
  - chiave `route_family_classification`: 30 famiglie di route classificate

**Fonte canonica secondaria (account-wide vs server-bound data policy):**
- `/app/data/design/server_lifecycle/account_server_data_scope_policy_v1.json`
  - sezioni `account_wide`, `server_bound`, `mixed_account_owned_server_equipped`
  - principi globali: `paid_currency_can_be_account_wide=true`, `free_currency_must_be_server_bound=true`, `progression_is_server_bound=true`, `borea_hidden_invariant_preserved=true`

**Famiglie candidate Batch-2 estratte (mixed / account_wide):**

| Famiglia (canonical) | Classification | File route corrispondente |
|---|---|---|
| `auth_user` | account_wide | (in `backend/server.py`, non in `routes/*.py`) |
| `economy_paid_wallet` | account_wide | `backend/routes/economy.py` |
| `push_notifications` | account_wide | `backend/routes/push_notifications.py` |
| `cosmetics_ownership` | mixed | `backend/routes/cosmetics.py` |
| `game_data` | mixed | `backend/routes/game_data.py` |

Tutte le altre famiglie sono `server_bound` (già coperte da Batch-0/1 e Batch-1B, oppure differite a Batch-1B-leftover / Batch-3 AF2-N / Batch-4 combat-battle) o `global_catalog_readonly` (no writes).

---

## 6. Candidate Route Audit Table

| # | File | Famiglia | Classification | Write surfaces | Decisione | Motivo |
|---|---|---|---|---|---|---|
| 1 | `backend/routes/push_notifications.py` | `push_notifications` | account_wide | `push_tokens` (upsert), `notifications` (insert/update) | **SKIP_ACCOUNT_WIDE_NO_CHANGE** | Canonical: account_wide. I documenti sono già keyati su `user_id` (= account ownership). Nessun `server_id` richiesto dalla spec SLC-F per identity/notification surfaces. Patchare cambierebbe la semantica account-wide. |
| 2 | `backend/routes/cosmetics.py` | `cosmetics_ownership` | mixed | `user_cosmetics` (insert/update con `owned_*` + `active_*`), `users` (`$inc` currency), `territory_control` (upsert) | **SKIP_AMBIGUOUS** | Lo schema mescola ownership account-wide (`owned_auras`, `owned_frames`) con stato equipped server-bound (`active_aura`, `active_frame`). Canonical richiede split strutturale: `ownership=account_wide`, `bonus_activation=server_bound`. Non encodabile come singolo `ensure_server_scope` blanket. Inoltre scrive su `db.users` (collection esplicitamente skipped) e su `db.territory_control` (semantica guild-level separata). |
| 3 | `backend/routes/economy.py` | `economy_paid_wallet + multi_server_legacy + vip_mixed + battle_pass + mail` | mixed_complex | `shop_purchases`, `daily_claims`, `user_mail`, `battle_pass`, `users` (currency), `vip_data`, `users.server` | **SKIP_AMBIGUOUS** | File aggrega 5 subsystem con semantiche conflittuali: (1) paid currency (gems) è account_wide, free currency (gold) è server_bound; (2) battle_pass season è account-level ma le ricompense vanno su currency server-bound; (3) vip_data è mixed (vip_level=account_wide, vip_claim_state=server_bound); (4) mail può essere account o server origin; (5) **contiene endpoint legacy `/server/select` alle righe 195-206** che è scope FORBIDDEN (server selection runtime endpoints). Patchare anche un singolo write rischia di attivare server selection runtime o riscrivere balance/economy logic, entrambi esplicitamente vietati. |
| 4 | `backend/routes/game_data.py` | `game_data` | mixed | NESSUNA | **SKIP_NO_WRITES** | Modulo puramente statico: definizioni costanti (`EQUIPMENT_TEMPLATES`, `SHOP_ITEMS`, `AURAS`, `AVATAR_FRAMES`, `TERRITORIES`, `SERVERS`, `VIP_LEVELS`, `BATTLE_PASS_REWARDS`). Zero `db.*.insert/update/upsert/delete`. Nulla da patchare. |

**Sintesi:** **4/4 candidate → SKIP**. Zero file patchati. Apply = SAFE NO-OP.

### Route esplicitamente fuori scope Batch-2 (auditate per completezza)

| File | Classification canonica | Motivo |
|---|---|---|
| `backend/routes/equipment.py` | server_bound | Server_bound, sarebbe un Batch-1B-leftover (non Batch-2 mixed/account-wide). Differita a follow-up task. |
| `backend/routes/unique_items.py` | non in canonical | Non classificato in `route_family_classification`. Fuori scope per Batch-2. Scrive su `db.users` (skipped). |
| `backend/routes/synergies.py` | nessun write | Solo route read-only. Niente da patchare. Fuori scope. |

---

## 7. Files Changed

### File di codice runtime patchati
- **NESSUNO.** Apply = SAFE NO-OP.

### File di sicurezza/marker/script generati
- `data/design/system_safety/slc_f_batch_2_apply_marker_v1.json` (apply marker firmato con `route_patch_applied=false`, `all_candidates_skipped=true`, `safe_no_op_apply=true`)
- `backend/scripts/rollback_slc_f_batch_2.py` (rollback gated)
- `backend/scripts/validate_slc_f_batch_2_post_apply_v1.py` (post-apply validator)
- `data/design/server_lifecycle/_slc_f_batch_2_post_apply_v1_result.json` (output validator, verdict `PASS`)
- `docs/divine/107_SLC_F_APPLY_BATCH_2.md` (questo report)
- `/tmp/slc_f_batch_2_suite.json` (suite master JSON report)

### Suite runner
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (+1 riga in `OPTIONAL`)

---

## 8. Routes Patched

**NESSUNA.** Per design di gated apply: lo scope Batch-2 era mixed/account-wide; tutti i candidati canonici hanno richiesto decisione semantica/refactoring strutturale ⇒ deferiti.

---

## 9. Routes Skipped and Why

| Route | Decisione | Riassunto motivo |
|---|---|---|
| `push_notifications.py` | SKIP_ACCOUNT_WIDE_NO_CHANGE | Account-wide canonical; nessuna modifica richiesta. |
| `cosmetics.py` | SKIP_AMBIGUOUS | Schema mixed conflittuale (ownership vs equipped). Refactoring necessario. |
| `economy.py` | SKIP_AMBIGUOUS | 5 subsystem mixed; contiene endpoint legacy server-select (forbidden scope). |
| `game_data.py` | SKIP_NO_WRITES | Modulo statico; nessun write. |
| `equipment.py` | OUT_OF_SCOPE_BATCH_2 | Server_bound; non Batch-2. |
| `unique_items.py` | OUT_OF_SCOPE_BATCH_2 | Non classificato; scrive su `db.users` (skipped). |
| `synergies.py` | OUT_OF_SCOPE_BATCH_2 | No writes. |

---

## 10. Account-Wide vs Server-Bound Policy Proof

Fonte: `/app/data/design/server_lifecycle/account_server_data_scope_policy_v1.json`

**Account-wide (identity / paid economy / notifications / paid cosmetics ownership):**
- identity: `account_id`, `auth_email`, `auth_provider`, `display_name_global`, `ban_state`, `region_preference`, `language_preference`
- economy: `paid_currency_balance`, `paid_currency_ledger`, `purchase_history`, `refund_history`, `tax_invoice_state`
- vip-account-wide-portion: `vip_level`, `vip_lifetime_purchase_amount`, `vip_perk_eligibility`
- paid_cosmetics_ownership: `premium_skin_ownership`, `premium_title_ownership`, `top_up_milestone_ownership`

**Server-bound (free economy / progression / inventory / teams / progress / social-on-server):**
- profile: `server_profile_id`, `player_name_on_server`, `level_on_server`, ...
- economy: `free_currency_gold`, `free_currency_diamonds_free`, `event_currency`, `shard_balances`, `resource_balances`
- roster: `hero_ownership`, `hero_star`, `hero_level`, `hero_equip`, `hero_artifacts`, `hero_skin_equipped`, `hero_affinity_state`, `hero_skill_state`
- inventory: `materials_inventory`, `gift_inventory`, `equipment_inventory`, `shard_inventory`, `consumable_inventory`
- progress: `story_progress`, `tower_floor`, `castle_floor`, `weekly_clears`, `daily_clears`, `event_progress`, `achievement_progress`
- social: `guild_id`, `guild_role`, `guild_contribution`, `friends_on_server`

**Mixed (account-owned, server-equipped) — REGOLA DI SPLIT:**
- `vip_account_wide_but_claims_server_bound`: `vip_level=account_wide`, `vip_claim_state=server_bound`, `vip_reward_inventory=server_bound`
- `paid_cosmetics_account_wide_but_use_requires_hero_on_server`: `ownership=account_wide`, `equip_requires=hero_on_target_server`, `bonus_activation=server_bound`
- `paid_currency_account_wide_but_spend_audit_per_server`: `balance=account_wide`, `spend_ledger_split_view=per_server`

**Decisione finale conforme alla policy:** una `ensure_server_scope` blanket NON è applicabile a nessuno dei 4 candidati senza violare la policy account-wide o senza un refactoring strutturale che esula dalla GUARDRAIL Batch-2.

---

## 11. Rollback Path

```bash
export SLC_F_BATCH_2_ROLLBACK_APPROVAL=true
export SLC_F_BATCH_2_ROLLBACK_ID=slc_f_batch_2_20260523T181752Z_b838601e
python3 /app/backend/scripts/rollback_slc_f_batch_2.py
```

Caratteristiche del rollback:
- **Gated**: rifiuta l'esecuzione (exit code 2) senza entrambi i marker. Test verificato: senza marker correttamente risponde `REFUSED: SLC_F_BATCH_2_ROLLBACK_APPROVAL must be set to "true"`.
- **Marker-only revert**: poiché l'apply è stato un SAFE NO-OP, non c'è codice da ripristinare. Il rollback scrive `data/design/system_safety/slc_f_batch_2_rollback_marker_v1.json` con annotazione del rollback.
- **No-DB-touch**: nessuna scrittura su MongoDB.
- **Idempotente**: rieseguito è no-op.

---

## 12. Validators Run

| Validator | Esito |
|---|---|
| `validate_slc_f_batch_2_post_apply_v1.py` (nuovo) | ✅ PASS errors=0 |
| `validate_slc_f_batch_1b_post_apply_v1.py` | ✅ PASS |
| `validate_slc_f_batch_0_1_post_apply_v1.py` | ✅ PASS |
| `validate_slc_g_commit_a_post_apply_v1.py` (SLC-G migration) | ✅ PASS |
| Suite AF2-N V12–V30 (canary, inventory writes, rate-limit, stage4 soak, observability) | ✅ PASS (tutti) |
| Suite Character Bible (RM1.27-A/D, RM1.28-A–E, RM1.29, RM1.30-A–C, RM1.32-A/B/C/C2) | ✅ PASS (tutti) |
| Suite SLC-C/D/G/H | ✅ PASS (tutti) |
| Suite Benchmark Canonical Source | ✅ PASS (tutti) |

---

## 13. Suite Result

```
Overall: PASS  (pass=343, fail=0, miss=0)
Δ vs Batch-1B end-state: +1 PASS (validator Batch-2 aggiunto)
JSON report: /tmp/slc_f_batch_2_suite.json
```

- Nessun FAIL.
- Nessun MISS.
- Nessun validator SUPERSEDED inatteso.

---

## 14. API Smoke Result

| Endpoint | HTTP | Note |
|---|---|---|
| `GET /api/heroes` | 200, **100** elementi | catalogo intatto |
| `GET /api/heroes/primordial_gaia` | **404** | esclusione preservata |
| `GET /api/heroes/borea` | **200** | catalog-only inert baseline |
| `GET /api/heroes/greek_borea` | **200** | catalog-only inert baseline |
| `GET /api/affinity/gift-spend/canary-status` | 200 | AF2-N preservato (allowlist=2500, cap=50000) |
| `GET /api/shop` | 401 | comportamento auth normale, no 5xx |
| `GET /api/cosmetics` | 401 | comportamento auth normale, no 5xx |
| `GET /api/battlepass` | 401 | comportamento auth normale, no 5xx |
| `GET /api/vip` | 401 | comportamento auth normale, no 5xx |

✅ Zero 5xx. Zero regressioni di auth. Nessuna mutazione DB su roster / Character Bible / AF2-N / Housing / UI.

---

## 15. Invariants

| Invariante | Atteso | Osservato | Esito |
|---|---|---|---|
| `/api/heroes` length | 100 | 100 | ✅ |
| `primordial_gaia` HTTP | 404 | 404 | ✅ |
| `borea` HTTP | 200 catalog-only inert | 200 | ✅ |
| `greek_borea` HTTP | 200 catalog-only inert | 200 | ✅ |
| AF2-N cap | 50000 | 50000 | ✅ |
| AF2-N allowlist size | 2500 | 2500 | ✅ |
| AF2-N feature_flag_currently_enabled | True | True | ✅ |
| AF2-N inventory_mutation_enabled | True | True | ✅ |
| AF2-N rate_limit_enabled | True | True | ✅ |
| SLC-G `migration_id` | `slc_g_commit_a_20260523T143803Z_4600ac04` | identico | ✅ |
| `SERVER_PROFILES_RUNTIME_ENABLED` | unset | unset | ✅ |
| `SECOND_SERVER_OPENING_ENABLED` | unset | unset | ✅ |
| Batch-0/1 apply marker | preservato | preservato | ✅ |
| Batch-1B apply marker | preservato | preservato | ✅ |
| Phase 11 executed | false | false | ✅ |

---

## 16. Forbidden Scope Verification

Verificato dal validator `validate_slc_f_batch_2_post_apply_v1.py`:

| File / Area | Diff vs HEAD | Esito |
|---|---|---|
| `backend/battle_engine.py` | nessuno | ✅ intatto |
| `backend/battle_core.py` | nessuno | ✅ intatto |
| `frontend/app/combat.tsx` | nessuno | ✅ intatto |
| `backend/routes/affinity_gift_spend.py` | nessuno | ✅ intatto |
| `backend/routes/affinity_gifts.py` | nessuno | ✅ intatto |
| `backend/routes/heroes.py` | nessuno | ✅ intatto |
| `backend/routes/combat.py` | nessuno | ✅ intatto |
| `backend/routes/sanctuary.py` | nessuno | ✅ intatto (Character Bible) |
| `backend/routes/push_notifications.py` | nessuno | ✅ SKIPPED come dichiarato |
| `backend/routes/cosmetics.py` | nessuno | ✅ SKIPPED come dichiarato |
| `backend/routes/economy.py` | nessuno | ✅ SKIPPED come dichiarato |
| `backend/routes/game_data.py` | nessuno | ✅ SKIPPED come dichiarato |
| Route `/api/housing` | non presente | ✅ |
| Route `/api/account/server-profiles` | non presente | ✅ |
| Route `/api/account/active-server` | non presente | ✅ |
| Frontend `/app/frontend/app/*` | nessuna modifica | ✅ |
| Housing runtime / HousingBonusResolver | non implementato | ✅ |
| SLC-H runtime endpoints | non implementati | ✅ |
| STACK-G | non toccato | ✅ |

**Esplicita verifica anti-falso-positivo:** il validator controlla anche che i Batch-2 candidate file **NON contengano** `from utils.server_scope import ensure_server_scope` (per provare che lo SKIP è reale e non un patch silente). Tutti e 4 i file passano questo check.

---

## 17. Borea/Gaia Safety Result

- ✅ `primordial_gaia` HTTP = **404** (esclusione storica preservata).
- ✅ `borea` HTTP = **200**, `greek_borea` HTTP = **200**, entrambi in modalità **catalog-only inert**:
  - presenti nel catalogo;
  - nessuna attivazione runtime;
  - nessun kit attivo, nessun trigger, nessun flag `BOREA_ACTIVATION_*` introdotto;
  - non summonabili, non visibili in pool obtainable, non in roster pubblico;
  - **Character Bible (`backend/routes/sanctuary.py`, `db.heroes`) NON toccata**.
- ✅ Nessun cambiamento a banner / rates / pity / obtainable pool / fragments / roster visibility (l'apply Batch-2 non ha toccato nessuna route gacha/summon/heroes/sanctuary).

---

## 18. AF2-N Preservation Result

| Voce | Pre-Batch-2 | Post-Batch-2 | Esito |
|---|---|---|---|
| `feature_flag_currently_enabled` | True | True | ✅ |
| `inventory_mutation_enabled` | True | True | ✅ |
| `rate_limit_enabled` | True | True | ✅ |
| `canary_allowlist_size` | 2500 | 2500 | ✅ |
| `canary_ledger_cap` | 50000 | 50000 | ✅ |
| Diff `affinity_gift_spend.py` vs HEAD | 0 | 0 | ✅ |
| Diff `affinity_gifts.py` vs HEAD | 0 | 0 | ✅ |
| Validators AF2-N V12–V30 (canary, monitoring, inventory wiring, stage1–4 apply/monitoring, rate-limit live probe, Redis HA, alerting, stress 2x/3x/5x/8x/10x, soak, observability, signoff package V8) | ALL PASS | ALL PASS | ✅ |

**Conclusione:** AF2-N (V12–V30) è **identico** allo stato pre-Batch-2. Nessuna interferenza laterale. Nessuna spesa effettuata. Nessuna riga ledger creata. STACK-G non toccato. Public spend UI non implementata.

---

## 19. Known Drift Docs Status

I 7 documenti di drift `user_heroes` provenienti dalla famiglia `gacha/summon` restano in stato **DRIFT KNOWN, NON-BLOCKING, INTENZIONALMENTE NON CORRETTI** anche in Batch-2.

**Motivo specifico per Batch-2:**
- La famiglia `gacha/summon` **non è classificata** nella canonical inventory come `account_wide` o `mixed_account_owned_server_equipped`.
- Le route gacha/summon hanno alta sensitività: qualsiasi modifica potrebbe alterare banner / rates / pity / obtainable pool / fragments / roster visibility — tutti scope esplicitamente vietati.
- Il GUARDRAIL specifico del pack dice: *"only touch if explicitly classified by canonical SLC-F Batch-2 and patch is purely metadata set-only-if-missing; otherwise SKIP and defer."*
- Poiché la canonical classification per Batch-2 **non include** gacha/summon, il fix dei drift docs è deferito a un job di housekeeping documentale dedicato.

Suite e validator AF2-N rimangono verdi nonostante il drift documentale (è metadata, non runtime).

---

## 20. Remaining Risks

| Rischio | Severità | Mitigazione |
|---|---|---|
| Drift docs gacha/summon non corretti (7) | bassa | Solo documentazione; runtime non impattato. Da chiudere in job housekeeping dedicato. |
| `equipment.py` rimane server_bound non patchato (Batch-1B-leftover) | bassa | Le scritture future a `user_equipment` continueranno senza `server_id` esplicito; coperto da SLC-G commit-A legacy `s1` policy. Pianificabile come Batch-1B-extension. |
| `cosmetics.py` / `economy.py` richiedono refactoring strutturale (split ownership vs equipped, split paid vs free, separazione VIP) | media | Refactoring esplicitamente fuori dallo scope di gated apply Batch-2. Richiederà un job dedicato con autorizzazione separata (`SLC_F_BATCH_2_REFACTOR_*`). |
| Endpoint legacy `/server/select` in `economy.py` | media | Esistente da prima di SLC-F; non attivato a runtime (env flag `SERVER_PROFILES_RUNTIME_ENABLED` unset). Da pulire/rimuovere in fase SLC-H live wiring. |
| Redis rate-limit binary può crashare nel container | media | `bash /app/ops/ensure_redis_rate_limit.sh` ripristina; validator V25 OPS recovery e safety-rollup T/U/V/W/X/Y restano PASS. |

Nessun rischio severità **alta** identificato.

---

## 21. Recommended Next Step

🔵 **Prossimi job possibili (NON in questo apply):**

1. **(P2) Refactoring strutturale `cosmetics.py`** — split `user_cosmetics` in `user_cosmetics_ownership` (account-wide) + `user_cosmetics_equipped` (server-bound). Richiederà migrazione dati esistenti + nuovo apply pack dedicato (`SLC_F_BATCH_2_COSMETICS_REFACTOR_APPLY_APPROVAL=true`).
2. **(P2) Refactoring strutturale `economy.py`** — separare paid (account-wide) da free (server-bound) currency ledgers; isolare VIP claim state in collection server-bound; rimuovere endpoint legacy `/server/select`. Richiederà apply pack dedicato.
3. **(P2) Batch-1B-extension per `equipment.py`** — patchare le upsert su `user_equipment` con `ensure_server_scope`; richiede solo verifica che `user_equipment` sia effettivamente server_bound (lo è, per canonical).
4. **(P2) Housekeeping drift docs gacha/summon** — job indipendente per correggere i 7 documenti di drift; nessun impatto runtime atteso.
5. **(P3) SLC-F APPLY BATCH-3 ONLY (AF2-N routing)** — solo dopo che AF2-N è stabilizzato sul broad rollout signoff (V8 attualmente PENDING).
6. **(P3) SLC-F APPLY BATCH-4 ONLY (combat/battle)** — backlog gated.
7. **(P3) SLC-H live wiring** — solo dopo refactoring di `economy.py` per evitare doppio percorso server-select.

⚠️ **Esplicitamente NON raccomandato ora:**
- Apertura secondo server.
- Attivazione runtime `SERVER_PROFILES_RUNTIME_ENABLED`.
- Toccare `db.heroes` / Character Bible / Borea activation.
- Toccare gacha/summon/combat/battle/AF2-N routing.
- Implementare `/api/housing` runtime.

---

## 22. Updated Progress Estimate

| Fase | Stato pre-Batch-2 | Stato post-Batch-2 |
|---|---|---|
| SLC-F Design / Dry-run / Combo | ✅ done | ✅ done |
| SLC-F Apply Prep + Housing Addendum | ✅ done | ✅ done |
| SLC-F Batch-0/1 (helper + items.py) | ✅ done | ✅ done |
| SLC-F Batch-1B (7 route low-risk server_bound) | ✅ done | ✅ done |
| **SLC-F Batch-2 (mixed/account-wide audit + safe no-op apply)** | 🟡 pending | ✅ **done (no-op safe)** |
| SLC-F Batch-2 refactoring strutturale (cosmetics/economy) | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-1B-extension (equipment) | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-3 (AF2-N routing) | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-4 (combat/battle) | 🔵 backlog | 🔵 backlog |
| SLC-H live wiring | 🔵 design-only | 🔵 design-only |
| Phase 11 / Second server / Broad rollout | 🔵 backlog | 🔵 backlog |
| Drift docs gacha/summon housekeeping | 🔵 backlog | 🔵 backlog |

**Progress estimate:**

> **90% → ~92%** ✅ (incremento atteso confermato; suite master 343/343 PASS).

---

## 23. Markers di audit (riferimenti rapidi)

- `apply_id`: `slc_f_batch_2_20260523T181752Z_b838601e`
- `applied_at_utc`: `2026-05-23T18:17:52+00:00`
- `git_head_before`: `fa44754`
- `git_head_after`: `fa44754` (nessun auto-commit triggerato)
- `slc_g_migration_id_preserved`: `slc_g_commit_a_20260523T143803Z_4600ac04`
- `slc_f_batch_0_1_apply_id_preserved`: `slc_f_batch_0_1_20260523T173754Z_27b1b737`
- `slc_f_batch_1b_apply_id_preserved`: `slc_f_batch_1b_20260523T175058Z_2cf0584c`
- `verdict_target`: `SLC_F_BATCH_2_APPLIED_SAFE` → ✅ **RAGGIUNTO (SAFE NO-OP)**

---

**FINE REPORT 107_SLC_F_APPLY_BATCH_2.md**
