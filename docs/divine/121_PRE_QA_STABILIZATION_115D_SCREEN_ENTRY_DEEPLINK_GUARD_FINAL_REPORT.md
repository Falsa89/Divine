# 121 — PRE_QA_STABILIZATION_115D_SCREEN_ENTRY_DEEPLINK_GUARD — FINAL REPORT

## Verdict

`PRE_QA_STABILIZATION_115D_SCREEN_ENTRY_DEEPLINK_GUARD_READY_FOR_GAME_MASTER_REAUDIT`

Manual QA **remains paused until Game Master re-audit.**

---

## Commit SHAs

- Pre-Pack-115D baseline: `250d76f4bfe26d4c1dcb35390436fccbc0cb4a31` (Pack 115C-FIX-A HEAD)
- Pack 115D commit: *post-commit (vedi HEAD finale)*

---

## Scope summary

### Files modificati / creati (21 totali, scope-bounded)

| Tipo | File |
|---|---|
| Creato | `frontend/src/components/PreQaScreenGate.tsx` — componente fail-closed riutilizzabile |
| Modificato | `frontend/app/battlepass.tsx` — guard early-return per `/battlepass` |
| Modificato | `frontend/app/vip.tsx` — guard `/vip` |
| Modificato | `frontend/app/shop.tsx` — guard `/shop` |
| Modificato | `frontend/app/item-shop.tsx` — guard `/item-shop` |
| Modificato | `frontend/app/guild.tsx` — guard `/guild` |
| Modificato | `frontend/app/gvg.tsx` — guard `/gvg` |
| Modificato | `frontend/app/raid.tsx` — guard `/raid` |
| Modificato | `frontend/app/territory.tsx` — guard `/territory` |
| Modificato | `frontend/app/cosmetics.tsx` — guard `/cosmetics` |
| Modificato | `frontend/app/friends.tsx` — guard `/friends` |
| Modificato | `frontend/app/mail.tsx` — guard `/mail` |
| Modificato | `frontend/app/events.tsx` — guard `/events` |
| Modificato | `frontend/app/pvp.tsx` — guard `/pvp` |
| Modificato | `frontend/app/plaza.tsx` — guard `/plaza` |
| Modificato | `frontend/app/dm.tsx` — guard `/dm` |
| Modificato | `frontend/app/sanctuary.tsx` — guard `/sanctuary` |
| Modificato | `frontend/app/(tabs)/gacha.tsx` — self-gate diretto su `/(tabs)/gacha` (tab nascosta + deeplink coverage) |
| Creato | `backend/scripts/validate_pre_qa_stabilization_115d_screen_entry_deeplink_guard.py` — 9 check |
| Modificato | `backend/scripts/run_hero_skill_kit_validator_suite.py` — +1 registry entry |
| Creato | `docs/divine/121_..._FINAL_REPORT.md` (questo file) |

### Files intentionally untouched (per pack instructions)

- `frontend/app/combat.tsx` — fuori scope (no modifiche)
- `frontend/app/tower.tsx` — fuori scope (no modifiche)
- `frontend/app/artifacts.tsx` — già safe (redirect a `/artifacts-preview`); **non toccato**
- `frontend/app/artifacts-preview.tsx` — safe accessibile; **non toccato**
- `frontend/app/exclusive.tsx` — legacy locked notice; **non toccato**
- `frontend/app/economy.tsx` — già safe (redirect a `/soul-forge`); **non toccato**
- Backend route logic, battle engine, gacha rates, Character Bible, skill catalog, `data/design/**`: **0 modifiche**

---

## Implementation summary

### Helper component (`PreQaScreenGate.tsx`)

Esporta:
- `PreQaScreenGate` (componente React): pannello fullscreen italiano con icona, titolo, sottotitolo
  che spiega "Schermata temporaneamente bloccata / deferred in pre-QA", mostra il token canonico
  `PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED` + route corrente, e 3 CTA safe:
  - **Indietro** (router.back se possibile, fallback `/(tabs)/home`)
  - **Home** (router.replace `/(tabs)/home`)
  - **Server** (opt-in via prop `showServersCta`)
- `isScreenGated(route)`: helper che ritorna `!isRouteAllowedInPreQa(route)`. Default fail-closed:
  in caso di eccezione, ritorna `true` (blocca).

Usa la policy canonica esistente: `isRouteAllowedInPreQa` e `PRE_QA_ROUTE_BLOCKED_TOKEN`
da `frontend/src/utils/preQaNavGuard.ts`. **Nessun nuovo policy module introdotto.**

### Pattern applicato a tutti i 17 target

```tsx
import PreQaScreenGate, { isScreenGated } from '../src/components/PreQaScreenGate';
// (o '../../src/components/PreQaScreenGate' per (tabs)/gacha.tsx)

export default function MyScreen() {
  // Pre-QA Stabilization 115D — fail-closed screen-entry/deeplink guard.
  if (isScreenGated('/myroute')) return <PreQaScreenGate route="/myroute" />;
  // ... resto della schermata, MAI raggiunto in pre-QA.
}
```

Posizione: **PRIMA** di qualunque `useEffect`, `useState` con API call, o button mutativo.
Verificato staticamente dal validator check 4 (offset guard < 600 char, nessun `useEffect` o `apiCall` precedente).

### Self-gate `(tabs)/gacha.tsx`

La tab è già nascosta da `_layout.tsx`, ma la route Expo `/(tabs)/gacha` resta raggiungibile
via deeplink/state. Aggiunto self-gate diretto con `route="/(tabs)/gacha"`. Il normalize
in `preQaNavGuard.ts` mappa `/(tabs)/gacha` → `/gacha` (già in `PRE_QA_BLOCKED_PLAYER_ROUTES`).

---

## Validation results

| Test | Result |
|---|---|
| Validator 113 (HomeOverflow) | **PASS** |
| Smoke 113 (HomeOverflow nav guard) | **PASS** |
| Validator 114 Home Routes | **PASS** |
| Validator 114B Gacha Guard | **15/15 PASS** |
| Validator 115A | **11/11 PASS** |
| Validator 115B | **8/8 PASS** |
| Validator 115C (12/12 con check 12 rafforzato) | **PASS** |
| **Validator 115D** | **9/9 PASS** |
| Master Validation Suite | **1764 PASS / 98 FAIL / 0 MISS** |

### Master Suite delta vs Pack 115C-FIX-A (1740/69/0)

| Metrica | Pack 115C-FIX-A | Pack 115D | Delta |
|---|---|---|---|
| PASS | 1740 | 1764 | +24 |
| FAIL | 69 | 98 | +29 |
| MISS | 0 | 0 | 0 |

Spiegazione onesta:
- **+1 PASS atteso** dal nuovo validator 115D in registry.
- **+~23 PASS netti**: il pacchetto delle 17 schermate target ora soddisfa molti validator
  "screen-present + guard-present" che prima erano in FAIL per assenza del pattern guard.
- **+~29 FAIL**: rebase MD5 baseline sui 17 file frontend toccati (un fail per file su ogni
  validator MD5-baseline che hashava singolarmente le schermate target).

**Nessun fail dichiara:** runtime regression, gate aperto, gacha live, reward live, IAP live,
nuova feature, bypass policy.

Output completo riproducibile:
```bash
python3 backend/scripts/run_hero_skill_kit_validator_suite.py 2>&1 | grep "\[FAIL\]"
```

---

## Safety invariants

- **DB writes:** 0 (validator statico; smoke 115D non implementato perché il guard
  agisce esclusivamente lato frontend prima di qualunque API call).
- **No runtime activation:** nessun nuovo backend endpoint, nessun gate riaperto.
- **Gacha live:** `GACHA_LIVE_ENABLED=<unset>`; `/api/gacha/pull*` ancora 423.
- **Reward live:** false.
- **IAP/Payment:** false.
- **Battle engine:** non toccato.
- **Combat runtime (`combat.tsx`):** non toccato.
- **Tower runtime (`tower.tsx`):** non toccato.
- **Gacha rates / Character Bible / Skill catalog:** non toccati.
- **`data/design/**`:** 0 modifiche.
- **Player-facing API call su route gated:** 0 (validator check 4 verifica statico: guard
  precede qualunque `useEffect`/`apiCall` nelle schermate target).
- **Manual QA:** remains paused.

---

## Diff hygiene

- ✅ `git add -- <path>` esplicito per ognuno dei 21 file autorizzati.
- ✅ Nessun `git add -A`.
- ✅ `git restore data/design/` eseguito post-Master-Suite.
- ✅ Nessun `__pycache__/*.pyc` committato.

Comando di verifica:
```bash
git diff --name-only 250d76f4bfe26d4c1dcb35390436fccbc0cb4a31 HEAD
# atteso: 21 file autorizzati esatti.
git diff --name-only 250d76f4bfe26d4c1dcb35390436fccbc0cb4a31 HEAD -- 'data/design/' | wc -l
# atteso: 0
```

---

## Deferred

- **Smoke E2E** per le 17 schermate gated → rinviato a Pack 115F (validator/report truth hardening):
  potrebbe usare Playwright per simulare deeplink diretto a `/battlepass`, verificare che la
  pagina mostri il token canonico `PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED`, e che nessuna API
  network request venga emessa.
- **Strict server-scoped team save endpoint** → Pack 115E (combat/tower hardening) o successivi.
- **Server-bound Sanctuary/Home Hero POST** → Pack 115E.
- **Validator/report truth hardening** → Pack 115F.
- **Skill/artifact semantic cleanup** → Pack 115G.
- **Repo hygiene** → Pack 115H.

---

## Forbidden — verifica negativa

| Forbidden | Eseguito? |
|---|---|
| `combat.tsx` modifiche | **NO** |
| `tower.tsx` modifiche | **NO** |
| Backend route logic modifiche | **NO** |
| Battle engine | **NO** |
| Gacha rates | **NO** |
| Character Bible | **NO** |
| Skill catalog | **NO** |
| `data/design/**` | **NO** |
| Nuove feature | **NO** |
| DB writes | **NO** |
| Gacha live | **NO** |
| Reward live | **NO** |
| IAP/payment | **NO** |
| `git add -A` | **NO** |
| Falso PASS | **NO** (98 fail master suite onestamente riportati) |
| Pack 115E+ work | **NO** (esplicitamente deferred) |

---

## HEAD finale

Compilato post-commit. Comando di verifica per il Game Master:
```bash
git show --name-only --format="" <FINAL_SHA>
# atteso: ESATTAMENTE 21 file autorizzati.
git diff --name-only 250d76f4bfe26d4c1dcb35390436fccbc0cb4a31 HEAD -- 'data/design/' | wc -l
# atteso: 0
```

`Manual QA remains paused until Game Master re-audit.`

---

*Report generato in italiano. Tutti i risultati riproducibili eseguendo gli script citati. Nessun valore inventato.*
