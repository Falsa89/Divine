# NEW_HERO_IMPORT_CHECKLIST — RM1.18 Standard

> **Scopo**: standard operativo per l'importazione di un nuovo eroe locale
> nel gioco. Deriva dalle lezioni apprese con Berserker (RM1.17-N → RM1.17-S)
> e Hoplite. Ogni nuovo eroe DEVE seguire questo processo per evitare la
> ri-emergere dei bug storici (crop sul volto, preload mancante, motion
> duplicata, scale non coerente, background null su tie fazione, ecc.).
>
> **Non** applicabile: eroi remoti (image_url da CDN/Mongo senza asset locali).
> Un eroe puramente remoto può esistere in DB senza bisogno di questo checklist.

---

## 0. Principi fondamentali

- **Il volto è la priorità.** Qualunque framing UI (Home, card, detail, preview,
  fullscreen) DEVE mostrare il volto senza crop sulla fronte/testa.
- **Il contract è l'unica fonte di verità.** Nessuna logica per-hero deve
  vivere dentro i componenti UI. Tutto va in `HERO_CONTRACTS`.
- **Nessun fallback su altri eroi.** Un nuovo eroe non può ereditare asset
  da Hoplite, Berserker o placeholder.
- **Il battle runtime è sacro.** Se l'eroe usa runtime sheets, `BattleSprite`
  NON deve applicare motion esterna (dash/pulse/rotation/collapse/aura).
- **Coerenza di scale.** Il body del nuovo eroe in battle deve avere
  altezza ~ 99% rispetto a Hoplite/Berserker di riferimento.

---

## 1. Asset checklist

### 1.1 Cartella canonica
```
frontend/assets/heroes/<hero_id>/
```
`<hero_id>` è l'ID canonico (es. `norse_berserker`, `greek_hoplite`, `egyptian_anubis`).

### 1.2 Portrait/UI assets (obbligatori)
- [ ] `splash.jpg` o `splash.png` (2:3 portrait, risoluzione minima 512×768)
- [ ] `transparent.png` (solo se l'eroe può apparire come Home hero o overlay)
- [ ] `card.png` (opzionale: se assente, `card` variant ripiega su `splash`)
- [ ] `detail.png` (opzionale: se assente, `detail` variant ripiega su `splash`)
- [ ] `fullscreen.png` (opzionale: se assente, `fullscreen` variant ripiega su `splash`)

### 1.3 Battle assets (obbligatori se l'eroe ha un rig di battaglia)
- [ ] `combat_base.png` (idle di fallback)
- [ ] `source_sheets/idle_source.png` (solo se `useRuntimeSheets: true`)
- [ ] `source_sheets/attack_source.png`
- [ ] `source_sheets/skill_source.png`
- [ ] `source_sheets/hit_source.png`
- [ ] `source_sheets/death_source.png`
- [ ] `runtime/idle_sheet.png` (repackato dalla pipeline)
- [ ] `runtime/attack_sheet.png`
- [ ] `runtime/skill_sheet.png`
- [ ] `runtime/hit_sheet.png`
- [ ] `runtime/death_sheet.png`
- [ ] `runtime/battle_animations.json` (vedi §5)
- [ ] `runtime/_debug_<hero_id>_runtime_preview.png` (validazione visiva)
- [ ] `runtime/_debug_<hero_id>_vs_reference_scale.png` (confronto scale)

### 1.4 Vietato
- Posizionare asset in cartelle random della root
- Riutilizzare cartelle di altri eroi
- Usare l'immagine di un altro eroe come fallback
- Copiare vecchi debug asset dentro `runtime/`

---

## 2. Contract checklist — `HERO_CONTRACTS` entry

File: `frontend/components/ui/hopliteAssets.ts`

### 2.1 Identità
- [ ] `id` canonico coerente con la cartella asset
- [ ] `crop.sourceAspect` corretto (`'portrait'` | `'square'` | `'landscape'`)

### 2.2 Variants obbligatorie
- [ ] `variants.splash`
- [ ] `variants.portrait`
- [ ] `variants.card`
- [ ] `variants.detail`
- [ ] `variants.fullscreen`
- [ ] `variants.transparent` (se l'eroe è eleggibile come Home hero)
- [ ] `variants.combat_base`
- [ ] `variants.idle/attack/skill/hit/death` (SOLO se `battle.useStateSprites=true`
      e NON usa runtime sheets)

### 2.3 UI contract obbligatorio (tutti e 5 gli slot)
- [ ] `ui.home`
- [ ] `ui.card`
- [ ] `ui.detailIcon`
- [ ] `ui.selectedPreview`
- [ ] `ui.fullscreen` con `verticalPriority: true`

Ogni slot DEVE specificare: `variant`, `resizeMode`, `focusY`, `scale`.

### 2.4 Battle contract
- [ ] `battle.defaultState`
- [ ] `battle.useRuntimeSheets` (true/false)
- [ ] `battle.useStateSprites` (false se runtime sheets)
- [ ] `battle.removeDefaultGlow` (true di default per nuovi eroi,
      false solo per eroi con aura intenzionale come Hoplite)
- [ ] `battle.useLegacyDefaultMotion` (false se runtime sheets)
- [ ] `battle.runtimeRenderScale` (tarato vs Hoplite/Berserker)
- [ ] `runtimeSheets.{idle,attack,skill,hit,death}` popolati se
      `useRuntimeSheets: true`

---

## 3. UI framing rules

### 3.1 Regole assolute
- Il volto è sempre visibile. NON si taglia la fronte/testa.
- Se `cover` + `focusY` taglia il volto su qualsiasi aspect, usa `contain`.
- Se `contain` rende l'eroe troppo piccolo, regola `scale` per-slot nel
  contract, MAI con CSS hardcoded nei componenti.

### 3.2 Screen coperti
Ogni eroe con UI contract è automaticamente renderizzato correttamente in:
- `HomeHeroSplash.tsx` (slot `home`)
- `components/AnimatedHeroPortrait.tsx` (slot `card`, usato da heroes.tsx)
- `app/hero-collection.tsx` (slot `card`)
- `app/(tabs)/heroes.tsx` pannello preview destro (slot `selectedPreview`)
- `app/hero-detail.tsx` header 80×80 (slot `detailIcon`)
- `app/hero-viewer.tsx` fullscreen (slot `fullscreen` con `verticalPriority`)

### 3.3 Vietato
- `RNImage resizeMode='cover'` raw per eroi con UI contract
- Fix per-eroe hardcoded dentro i singoli componenti
- Placeholder letter fallback quando esiste un asset valido

---

## 4. Fullscreen viewer standard

`frontend/app/hero-viewer.tsx`:
- [ ] Lock `PORTRAIT_UP` su mount via `ScreenOrientation.lockAsync`
- [ ] Restore `LANDSCAPE` su unmount nel cleanup `useEffect`
- [ ] Web: short-circuit (`Platform.OS === 'web'`) senza lock
- [ ] Nessuna caption/nome/stelle sotto l'immagine
- [ ] Nessuna label o testo decorativo
- [ ] `resizeMode='contain'` di default
- [ ] Sfondo nero safe
- [ ] Tap/back chiude il viewer

Acceptance per device reale: aprire hero-viewer deve ruotare il device in
portrait; tornare indietro ripristina landscape.

---

## 5. Battle runtime standard

### 5.1 Requisiti runtime sheets
Se `battle.useRuntimeSheets: true`:
- [ ] Tutte e 5 le animazioni presenti (idle/attack/skill/hit/death)
- [ ] `BattleSprite` usa il branch runtime sheet PRIMA di static/legacy
- [ ] `BattleSprite` NON applica motion esterna (nessun dash, pulse, rotate,
      aura, collapse) — `RuntimeSheetSprite` ha l'ownership esclusiva
- [ ] Background trasparente (no white/black baked)
- [ ] Cell size stabile (no jitter)
- [ ] Non-loop animations holdano l'ultimo frame visibile
- [ ] `runtimeRenderScale` tarato visivamente vs Hoplite/Berserker reference

### 5.2 Metadata `runtime/battle_animations.json`

Schema obbligatorio:
```json
{
  "heroId": "<hero_id>",
  "version": 1,
  "frameWidth": 256,
  "frameHeight": 256,
  "animations": {
    "idle":   { "frames": 6,  "columns": 6,  "rows": 1, "fps": 10, "loop": true,  "sha256": "..." },
    "attack": { "frames": 8,  "columns": 8,  "rows": 1, "fps": 18, "loop": false, "sha256": "..." },
    "skill":  { "frames": 12, "columns": 6,  "rows": 2, "fps": 20, "loop": false, "sha256": "..." },
    "hit":    { "frames": 4,  "columns": 4,  "rows": 1, "fps": 16, "loop": false, "sha256": "..." },
    "death":  { "frames": 10, "columns": 5,  "rows": 2, "fps": 12, "loop": false, "sha256": "..." }
  }
}
```

### 5.3 Regole visive
- No frame vuoti animati
- No text labels nei runtime sheets
- Feet/bottom anchor stabile (no drift verticale)
- No glow di default (a meno che il contract lo dichiari esplicitamente)

---

## 6. Battle preload standard

File: `frontend/app/(tabs)/combat.tsx` (o `frontend/app/combat.tsx`)

- [ ] `getHeroBattlePreloadAssets(heroId, heroName, image)` chiamato per ogni
      eroe in `teamA` e `teamB`
- [ ] Runtime sheets inclusi nel preload se presenti
- [ ] Combat_base fallback incluso
- [ ] Background preload preservato
- [ ] Hoplite preload preservato
- [ ] Battle phase NON inizia finché i required asset locali non sono
      caricati

Acceptance: il nuovo eroe non appare mai blank all'inizio della battle;
nessun sprite pop-in tardivo.

---

## 7. Battle background standard

Resolver background con fallback deterministico:
1. Campaign/story context → background campagna
2. Team faction majority resolver
3. Tie fazione → fallback deterministico:
   1. `teamA[0].faction`
   2. `teamB[0].faction`
   3. Qualunque faction nota nelle due squadre
   4. Gradient fallback SOLO se nessuna faction nota

Vietato:
- Background null in team misti comuni
- Risultato random al tie
- Dark fallback quando esiste una faction nota

---

## 8. Selected detail panel / scroll standard

File: `frontend/app/(tabs)/heroes.tsx`

- [ ] Il bottone `DETTAGLIO` è FUORI dalla `ScrollView` (sticky bottom)
- [ ] Il body ha `paddingBottom ≥ altezza tab bar` (58px + safe area)
- [ ] La `ScrollView` non snappa indietro prima del click
- [ ] Funziona per portrait heroes alti (selectedPreview fino a 170px)
- [ ] Funziona per cards piccole (50-80px)

Mandatory per future portrait heroes con `ui.selectedPreview.resizeMode='contain'`.

---

## 9. Safety checklist pre-merge

Prima di mergeare un nuovo eroe:
- [ ] Hoplite battle comportamento invariato (verificare con battle test manuale)
- [ ] Berserker battle comportamento invariato
- [ ] Home splash Hoplite/Berserker invariati
- [ ] DETTAGLIO button raggiungibile per tutti gli eroi
- [ ] `tsc --noEmit` clean sui file modificati
- [ ] Metro bundle senza errori di risoluzione asset
- [ ] Backend/DB NON modificati (unless explicit task)

---

## 10. Template pronto

Vedi `NEW_HERO_CONTRACT_TEMPLATE` esportato da
`frontend/components/ui/hopliteAssets.ts`. È un oggetto `HeroAssetContract`
già strutturato con i valori sicuri di default; copiarlo, rinominarlo e
compilarlo con gli asset del nuovo eroe.

## 11. Validator helper

Per validare programmaticamente un contract esiste
`validateHeroContract(heroId)` in `hopliteAssets.ts`:

```ts
import { validateHeroContract } from './components/ui/hopliteAssets';

const warnings = validateHeroContract('egyptian_anubis');
if (warnings.length > 0) {
  console.warn('[HeroContract]', warnings);
}
```

Ritorna un array di stringhe con i problemi rilevati. Array vuoto = OK.

---

_Documento creato: RM1.18 (Giugno 2025). Da mantenere aggiornato ad ogni
nuovo eroe importato._
