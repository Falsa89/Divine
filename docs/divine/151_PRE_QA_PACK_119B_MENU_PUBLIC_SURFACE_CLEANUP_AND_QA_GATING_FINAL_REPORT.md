# Pack 119B — Menu Public Surface Cleanup & QA Gating — Final Report

> **Codice pack:** `PRE_QA_PACK_119B_MENU_PUBLIC_SURFACE_CLEANUP_AND_QA_GATING`
> **Tipo:** Pulizia label/menu + QA gating + safe area bottom padding
> **Scope:** SOLO `frontend/app/(tabs)/menu.tsx` + `frontend/src/utils/preQaNavGuard.ts`
> **No-touch:** backend, combat runtime, gacha/shop/reward/DB, tutorial/onboarding,
> nessun refactor largo, no nuove feature.

## 0. Numerazione del report

L'ultimo report PRE_QA della sequenza era `139_PRE_QA_PACK_119A_FIX_F_...`.
I numeri 140–150 risultano già occupati da report di altri progetti paralleli
(`PROJECT_R`, `PROJECT_S`, `PROJECT_T`, `PROJECT_U`, `PROJECT_V`, `PROJECT_W`,
`PROJECT_X`, `PROJECT_Y`, `PROJECT_Z`, `PROJECT_FRONTEND_B`,
`PROJECT_FRONTEND_C`). Per non sovrascrivere report esistenti, questo report
adotta il prossimo numero libero: **151**.

## 1. Obiettivi del pack

1. Nascondere la sezione **"Battle Preview QA v88"** dal menu player-facing.
2. Rimuovere label tecniche player-facing (es. "Renderer reale V90", "TEST",
   "QA") dalle voci visibili al giocatore.
3. Pulire il **doppione** tra **Battaglia** e **Battle Preview** (mostrare
   solo la Battaglia reale wired al renderer canonico).
4. Nascondere o mettere in **gating** i cataloghi interni (Skill, Sistemi in
   preparazione).
5. Correggere "Hub Anime (Soul Forge)" in **"Forgia dell'Anima"**.
6. Spostare **"Fucina di Efesto"** fuori dalla categoria **Combattimento**
   verso **Progressione**.
7. Aggiungere/verificare **padding bottom / safe area** nel menu scrollabile
   affinché la bottom nav non copra l'ultima voce.
8. Eseguire validator suite, ripulire repo hygiene e committare in sicurezza
   con `git add -- <file>`.

## 2. Modifiche applicate

### 2.1 `frontend/app/(tabs)/menu.tsx`

#### 2.1.1 Label tecniche rimosse dalla copy player-facing

| Voce / Categoria | Prima | Dopo |
| --- | --- | --- |
| Categoria principale "Battaglia" | `Battaglia (Renderer Reale v90)` | `Battaglia` |
| Voce in Combattimento | `Torre degli Inferi (TEST)` | `Torre degli Inferi` |
| Voce in Economia | `Hub Anime (Soul Forge)` | `Forgia dell'Anima` |

Marker tecnici come `v90`, `(TEST)`, `Hub Anime`, `(Soul Forge)` sono stati
rimossi dalle stringhe player-facing. I commenti tecnici interni (incluso
`Renderer reale v90`, `pre-battle-lobby v91_FIXED`) restano nei commenti del
file per audit e tracciamento storico, ma **non sono più esposti al giocatore**.

#### 2.1.2 Doppione Battaglia ⇄ Battle Preview

La categoria duplicata `Battle Preview QA (v88) — Wireframe Deprecato v90` è
ora nascosta dal menu pubblico tramite **gating canonico** (vedi §2.2):
`PRE_QA_BLOCKED_CATEGORIES` include questo titolo. Le route legacy
`/playable-mode-battle-preview*` restano accessibili come deep link interno
QA, ma non appaiono più nel menu del giocatore.

L'unica entry "Battaglia" visibile è quella wired alla **Pre-Battle Lobby
canonica** (`/pre-battle-lobby?mode=...`) che instrada al renderer reale.

#### 2.1.3 Cataloghi interni gated

Le voci dei cataloghi interni sono dichiarate nel sorgente per backward
compatibility con i deep link QA, ma vengono filtrate dal menu player-facing
tramite `PRE_QA_BLOCKED_PLAYER_ROUTES` in `preQaNavGuard.ts`:

- `/skill-status-vfx-catalogs` — Catalogo Skill & Status
- `/hero-skill-kits-catalog` — Kit Skill Eroi
- `/safe-previews` — Sistemi in preparazione
- `/playable-mode-battle-preview` — Battle Preview wireframe (deprecato v88/v90)

#### 2.1.4 Spostamento "Fucina di Efesto"

La voce **"Fucina di Efesto"** (route `/equipment`) è stata rimossa dalla
categoria **Combattimento** e collocata nella categoria **Progressione**, in
linea con la sua natura di hub forging/equipaggiamento (non è una modalità di
combattimento).

#### 2.1.5 Safe area / padding bottom della ScrollView

Nuovo calcolo runtime del `paddingBottom` della `ScrollView` del menu:

```tsx
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const TAB_BAR_HEIGHT = 58;            // == st.tabBar.height in (tabs)/_layout.tsx
const MENU_BOTTOM_SAFETY_MARGIN = 38; // copre indicator + ombra

const insets = useSafeAreaInsets();
const _menuListPaddingBottom =
  insets.bottom + TAB_BAR_HEIGHT + MENU_BOTTOM_SAFETY_MARGIN;

<ScrollView
  contentContainerStyle={[s.list, { paddingBottom: _menuListPaddingBottom }]}
  showsVerticalScrollIndicator={false}
>
```

Razionale del valore:

- `insets.bottom` → safe area reale del device (home indicator iOS, gesture
  bar Android). Su device senza notch/home indicator vale 0, e il calcolo
  resta coerente con il fallback.
- `TAB_BAR_HEIGHT = 58` → allineato 1:1 con `st.tabBar.height` definito in
  `frontend/app/(tabs)/_layout.tsx`. Documentato in commento del menu per
  evitare drift visivo.
- `MENU_BOTTOM_SAFETY_MARGIN = 38` → copre l'`activeIndicator` (2px) + ombra
  + margine fisiologico per scroll naturale.

Somma totale tipica: ~96 px su device con home indicator, ~96 px su device
senza (perché `TAB_BAR_HEIGHT + MENU_BOTTOM_SAFETY_MARGIN = 96`). Allineato
al fallback richiesto dall'utente (`insets.bottom + 96` equivalente).

Il `paddingBottom: 70` statico nello `StyleSheet` resta come **fallback
ultimo-livello** (es. se l'hook safe-area non fosse disponibile per qualsiasi
ragione di runtime), ma viene **sempre sovrascritto a runtime** dal calcolo
sopra tramite `contentContainerStyle` array merge.

### 2.2 `frontend/src/utils/preQaNavGuard.ts`

`PRE_QA_BLOCKED_PLAYER_ROUTES` esteso con le route Pack 119B:

```ts
// Pre-QA Pack 119B — Catalog/internal/dev-only routes nascoste dal menu pubblico.
'/skill-status-vfx-catalogs',
'/hero-skill-kits-catalog',
'/safe-previews',
'/playable-mode-battle-preview',
```

`PRE_QA_BLOCKED_CATEGORIES` esteso con la categoria deprecated:

```ts
// Pre-QA Pack 119B — sezione deprecated Battle Preview wireframe (v88/v90).
'Battle Preview QA (v88) \u2014 Wireframe Deprecato v90',
```

Le route restano fisicamente nel filesystem (deep link interno QA), ma il
menu pubblico le filtra via `isRouteAllowedInPreQa()`.

## 3. Validazione

### 3.1 Repo hygiene sweep

```text
python3 backend/scripts/sweep_repo_hygiene.py
→ fs: __pycache__ rimosse = 0
→ fs: .pyc/.pyo rimossi    = 0
→ git: pycache/pyc/pyo tracciati = 0
→ clean = True
```

✅ Nessun artefatto compilato Python da pulire o staged accidentalmente.

### 3.2 Pre-QA Safety Validator Suite

```text
python3 backend/scripts/run_pre_qa_safety_validator_suite.py
================ PRE-QA SAFETY SUITE — RIASSUNTO ================
  totali:  24
  PASS:    24
  FAIL:    0
  SKIPPED: 0
  backend_up: True
  verdict: PRE_QA_SAFETY_SUITE_PASS
=================================================================
```

✅ Tutti i 24 validator pre-QA passano (incluso il validator legacy
`Pack 110 Menu Cleanup`, che certifica routes/categorie ancora bloccate e flag
`EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE` di default OFF).

### 3.3 Validator menu cleanup specifico

```text
python3 backend/scripts/validate_pre_qa_stabilization_110_menu_cleanup.py
[v110 PRE_QA_110_MENU_CLEANUP] OK twelve_routes_blocked qa_categories_hidden flags_default_off
```

✅ Le 12 route legacy unsafe e le categorie QA restano bloccate; flag pre-QA
di default OFF.

### 3.4 TypeScript

`npx tsc --noEmit -p .` non riporta errori per `frontend/app/(tabs)/menu.tsx`
o `frontend/src/utils/preQaNavGuard.ts`. Gli errori TS pre-esistenti su
`app/(tabs)/home.tsx` e `app/combat.tsx` non sono toccati da questo pack e
sono fuori scope.

### 3.5 Frontend liveness

`curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/` → `200`.
Expo si avvia senza errori dopo `sudo supervisorctl restart expo`.

## 4. Vincoli rispettati

- ✅ Solo `frontend/app/(tabs)/menu.tsx` + `frontend/src/utils/preQaNavGuard.ts`
- ✅ Nessuna modifica backend (zero file backend toccati)
- ✅ Nessuna modifica al combat runtime
- ✅ Nessuna modifica a gacha/shop/reward/DB writes
- ✅ Nessuna feature tutorial/onboarding aggiunta
- ✅ Nessun refactor largo
- ✅ Nessun `git add -A` — commit usa `git add -- <path>` esplicito
- ✅ Repo hygiene clean (0 pyc/pycache staged)
- ✅ Validator suite obbligatoria eseguita: 24/24 PASS

## 5. File modificati (commit list)

```text
git add -- frontend/app/(tabs)/menu.tsx
git add -- frontend/src/utils/preQaNavGuard.ts
git add -- docs/divine/151_PRE_QA_PACK_119B_MENU_PUBLIC_SURFACE_CLEANUP_AND_QA_GATING_FINAL_REPORT.md
```

## 6. Verdict

**`PRE_QA_PACK_119B_MENU_PUBLIC_SURFACE_CLEANUP_AND_QA_GATING_READY_FOR_GAME_MASTER_REAUDIT`**

Il menu player-facing è ora pulito da label tecniche, ha gating canonico per
cataloghi interni e sezioni QA, "Fucina di Efesto" è in Progressione,
"Forgia dell'Anima" sostituisce "Hub Anime (Soul Forge)", e la ScrollView
applica safe-area + altezza reale della bottom tab bar per garantire che
nessuna voce resti coperta dalla nav.
