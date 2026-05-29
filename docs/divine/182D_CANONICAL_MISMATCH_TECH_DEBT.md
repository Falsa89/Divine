# 182D — Canonical Mismatch & Tech Debt Report

**Track:** D — Canonical Mismatch & Tech Debt Report
**Verdict:** `TRACK_D_CANONICAL_MISMATCH_TECH_DEBT_READY`
**Pack:** `PROJECT_FULL_RUNTIME_FEATURE_REALITY_AUDIT_WITH_TEST_ASSET_REGISTRY`

## 10 Mismatch identificati

### 🔴 HIGH severity (3)

#### 1. `MISMATCH_NO_STAMINA_VIOLATION`
- **Canonical:** `NO_STAMINA_SYSTEM`
- **Stato attuale:** Legacy stamina-cost gating ancora presente in 5 backend route + 5 frontend screen.
- **Backend evidence:**
  - `combat.py:48,50,109,111,211,213` (`$inc stamina -N`)
  - `cosmetics.py:95,97` (`$inc stamina -15`)
  - `economy.py:50,51,52,71,95`
  - `gvg.py:235,237,239` (`$inc stamina -12`)
  - `raids.py:70,72` (`$inc stamina -10`)
- **Frontend evidence:** `events.tsx`, `gvg.tsx`, `shop.tsx`, `tower.tsx`, `treasury.tsx`
- **Impatto:** Combat/cosmetics/GvG/raids/events bloccati da stamina cost NON più nel design canonico.
- **Recommendation:** `PROJECT_NO_STAMINA_REMEDIATION_PACK` (P0 release blocker). Sostituire stamina con cooldown / daily-attempts / no-cost.
- **Release blocker:** ✅ true

#### 2. `MISMATCH_BENCHMARK_16_MODES_NOT_FULLY_IMPLEMENTED`
- **Canonical:** 16 live/special modes canonical
- **Stato attuale:** Solo 4-5 modalità scaffold/prototype. 9+ DESIGN_ONLY.
- **Missing:** Titanomachia, Assalto del Ragnarok, Crepuscolo dei Titani, Giudizio delle Stirpi, Prove del Pantheon, Sigilli degli Dei, Giudizio di Asgard, Cammino dell'Ade, Scala dell'Olimpo, Troni dell'Eclissi, Abisso del Colosso, Fame del Behemoth, Furie del Pantheon.
- **Recommendation:** Implementazione iterativa con TEST placeholder kit (Track E + F).
- **Release blocker:** false (soft-launch acceptable, ma serve chiarezza LOCKED vs COMING_SOON).

#### 3. `MISMATCH_AUDIO_MISSING_GLOBAL`
- **Canonical:** Asset Pipeline VFX/audio placeholder
- **Stato attuale:** Nessuna directory `frontend/assets/audio/`. Zero SFX/music wiring.
- **Recommendation:** Track E schema TEST audio + Track F P3 polish.
- **Release blocker:** ✅ true

### 🟡 MEDIUM severity (3)

#### 4. `MISMATCH_SERVER_PROFILE_PARTIAL`
- Canonical: server profiles with S1 default migration gated (SLC G)
- Stato: preview gated; multi-shard live non implementato.
- Recommendation: pack **SLC_H release candidate gate**.
- Release blocker: ✅ true

#### 5. `MISMATCH_VFX_STATUS_ICON_PIPELINE_PARTIAL`
- Canonical: VFX/status icon pipeline traceable
- Stato: catalogs presenti, ma VFX live combat rendering parziale.
- Recommendation: combat polish pack (P3).

#### 6. `MISMATCH_STORY_CONTENT_MISSING`
- Canonical: Story core loop functional
- Stato: `story.tsx` scaffold; no chapter content, no cutscenes.
- Recommendation: story content + voice/cutscene placeholder kit.
- Release blocker: ✅ true

### 🟢 LOW severity (3)

#### 7. `MISMATCH_BORE_GAIA_LEGACY` — **status: resolved_validated** (Borea inert baseline + Gaia canonical axis OK)
#### 8. `MISMATCH_PLACEHOLDER_PRETENDING_FINAL` — Track E backfill
#### 9. `MISMATCH_RUNES_NOT_IMPLEMENTED` — pack RUNES_FOUNDATION quando prioritario

### ✅ ALIGNED / NONE severity (1)

#### 10. `MISMATCH_ARTIFACT_LEGACY_POST_LOCK` — `ARTIFACT_MUTATION_LOCK_STATUS = 423` applied, banner hidden, Stage 8 canary internal-only — **status: aligned**.

## Counts
```
total_mismatches      = 10
high_severity         = 3
medium_severity       = 3
low_severity          = 3
none_aligned          = 1
release_blockers      = 4 (stamina, audio, server_profile, story)
```

## Verdict
`TRACK_D_CANONICAL_MISMATCH_TECH_DEBT_READY` — 10 mismatch identificati, severità classificate, remediation pack proposti. Nessuna rimozione di lock. Audit-only.
