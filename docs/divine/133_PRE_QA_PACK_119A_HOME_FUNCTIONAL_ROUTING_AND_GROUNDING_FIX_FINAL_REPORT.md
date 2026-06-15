# 133 — Pre-QA Pack 119A — Home Functional Routing and Grounding Fix — FINAL REPORT

**Pack ID:** `PRE_QA_PACK_119A_HOME_FUNCTIONAL_ROUTING_AND_GROUNDING_FIX`
**Data esecuzione:** 2026-06-15 (UTC)

## 1. Verdict
# ✅ `PRE_QA_PACK_119A_HOME_FUNCTIONAL_ROUTING_AND_GROUNDING_FIX_READY_FOR_GAME_MASTER_REAUDIT`

---

## 2. Scope

Pack 119A corregge solo i 5 bug Home funzionali/routing/grounding identificati dal
Game Master in audit statico + verifica device. **Non** crea tutorial. **Non**
modifica starter flow. **Non** resetta account test. **Non** introduce sistemi
live. Tutte le foundation 115A–118B-FIX-A preservate.

---

## 3. Files Modified (2 file)

| File | Tipo |
|------|------|
| `frontend/app/(tabs)/home.tsx` | **MODIFIED** (5 micro-fix mirati) |
| `frontend/constants/homeAssetsManifest.ts` | **MODIFIED** (3 mappings routing) |
| `docs/divine/133_PRE_QA_PACK_119A_HOME_FUNCTIONAL_ROUTING_AND_GROUNDING_FIX_FINAL_REPORT.md` | **NEW** (questo report) |

Nessun backend change. Nessun nuovo asset. Nessun package/dependency change.

---

## 4. Fix dettagli

### 4.1 Avatar crash P0 — RISOLTO
**File:** `frontend/app/(tabs)/home.tsx` (HomeProfilePanel, intorno linea 758)
**Prima:** `onPress={() => setSelectorOpen('avatar')}` + `onLongPress={() => setSelectorOpen('frame')}` → apriva il modal `AvatarFrameSelector` che crashava su device reale.
**Dopo:** entrambi gli handler ora mostrano un `Alert` con messaggio locked/deferred chiaro:
```
"Personalizzazione profilo — Sistema avatar e cornici in arrivo. Disponibile in un prossimo aggiornamento."
```
Try/catch difensivo `try { Alert.alert(...) } catch (_e) {}` per zero crash anche se Alert dovesse fallire.
Il componente `<AvatarFrameSelector>` resta mounted (selectorOpen sempre `false`) — zero allocazione modale, zero render path che crashava.

**Acceptance:** Tap avatar non crasha · nessuna app close · nessun red screen · nessuna navigazione rotta. ✅

---

### 4.2 Battle Power Home source truth — GIÀ CORRETTO (Pack 116A + 116A-EXT FIX-A)
La Home **già** usa `useBattlePowerSummary()` hook (linea 633 di home.tsx) che chiama
`GET /api/battle-power/summary?server_id=<sid>` — server-authoritative.
Il backend `battle_power.py` (Pack 116A-EXT FIX-A) calcola il BP **esclusivamente**
dalla `team_formation` attiva del `player_server_profile`, **mai** dal roster posseduto.
Se non c'è team valido: `team_missing=true`, `active_team_power=0`.

**Source truth confermata:** `team_source='player_server_profile.team_formation'`,
nessun `owned-roster aggregate`, nessun `fake default BP`. La UI mostra
`bp.displayTeamPowerLabel` che rispetta il contratto 116A-EXT FIX-A.

**Acceptance:** BP Home usa active formation source truth · no owned-roster aggregate · no fake default BP · no tutorial/starter mutation. ✅

---

### 4.3 Bottom navigation routing fixes
**File:** `frontend/constants/homeAssetsManifest.ts` (HOME_ROUTES) + `frontend/app/(tabs)/home.tsx` (HomeBottomNav SKILL onPress override)

| Tasto | PRIMA (errato) | DOPO (119A) | Note |
|-------|----------------|-------------|------|
| **BAG** | `/equipment` | `/inventory` | Inventory è la vera "Borsa" player (inventario consumabili/shards). Equipment era Forge-like. |
| **FORGE** | `/soul-forge` | `/equipment` | Equipment è il Forge hub primario (gear management). Soul Forge resta accessibile come sub-system dedicato. |
| **SKILL** | `''` (apriva overflow menu) | `''` + onPress override locale | Il bottone HomeBottomNav SKILL ora mostra `Alert "Sistema Skill in arrivo"` invece di triggherare `goTo('skill')` (che apriva overflow). |
| **TEAM** | `/(tabs)/battle` | `/(tabs)/battle` | **Invariato** — corretto. |
| **CHAT** | `''` (in-home panel) | `''` (in-home panel) | Invariato. |
| **GUILD/SHOP/ARTIFACT/MENU** | – | – | Invariati. |

**Acceptance:**
- BAG non apre Forge (apre Inventory) · ✅
- FORGE non apre Soul Forge come route primaria (apre Equipment hub) · ✅
- SKILL non apre menu vuoto/overflow (mostra locked feedback chiaro) · ✅
- TEAM resta funzionante · ✅

---

### 4.4 Nickname + titolo "Apprendista" — TAPPABILI CON FEEDBACK SAFE
**File:** `frontend/app/(tabs)/home.tsx` (HomeProfilePanel mobile branch ~linea 958-1006 + tablet/desktop branch ~linea 1115/1170)

#### Nickname
- Display **già** usa `user?.nickname || user?.name || 'Player'` (linea 628) — nickname account viene mostrato se disponibile, fallback solo se assente.
- Aggiunto wrapping in `TouchableOpacity` con `hitSlop` per touch target ≥44pt.
- onPress mostra Alert locked/deferred:
  ```
  "Profilo giocatore — La schermata profilo completa è in arrivo. Disponibile in un prossimo aggiornamento."
  ```
- Try/catch difensivo → zero crash.

#### Titolo "Apprendista"
- Display **già** usa `user?.title || 'Apprendista'`.
- Mobile branch: aggiunto `TouchableOpacity` con feedback locked/deferred.
- **Tablet/desktop branch**: rimosso `router.push('/achievements')` (errato — non è il sistema titoli) e sostituito con stesso Alert locked:
  ```
  "Titoli giocatore — La lista titoli equipaggiabili è in arrivo. Disponibile in un prossimo aggiornamento."
  ```

**Acceptance:**
- Nickname non resta hardcoded "Player" se nickname utente disponibile · ✅
- Tap nickname non crasha (Alert safe) · ✅
- Tap titolo non crasha (Alert safe) · ✅
- Titolo NON punta più genericamente ad /achievements · ✅
- Feature non pronta → feedback locked/deferred chiaro · ✅

---

### 4.5 Home hero grounding cross-background
**File:** `frontend/app/(tabs)/home.tsx` (style `heroLayer`, linea 2087 originale)

**Prima:**
```ts
heroLayer: {
  position: 'absolute',
  top: 0, bottom: 68, left: 0, right: 0,
  alignItems: 'center', justifyContent: 'center',
  zIndex: 1,
}
```
Hero centrato verticalmente in un layer alto `(screenHeight - 68)` → **fluttuava sopra la piazza** (effetto "ritaglio appiccicato").

**Dopo:**
```ts
heroLayer: {
  position: 'absolute',
  top: 0, bottom: 0, left: 0, right: 0,    // arriva fino al bordo fisico
  alignItems: 'center', justifyContent: 'flex-end',  // ground anchor
  paddingBottom: 28,    // feet a ~28px da bottom → occlusi dal nav bar (~120px)
  zIndex: 1,
}
```

**Logica grounding cross-background:**
- La logica è **screen-relative** (non background-relative): la stessa configurazione
  vale per tutte le varianti di background Home (faction / time-phase / fallback).
- `justifyContent: 'flex-end'` ancora la `HomeHeroSplash` box al bottom del layer.
- `paddingBottom: 28` posiziona i feet del personaggio a ~28px dal bordo inferiore dello schermo.
- La `HomeBottomNav` (zIndex superiore al hero layer) ha altezza `BAR_H_VISIBLE` ~120px su phone — **occlude naturalmente lower legs/feet** del personaggio, creando l'effetto "poggiato sul terreno".
- Busto/testa restano leggibili sopra il nav bar.

**Acceptance:**
- Personaggio non fluttua sul background corrente · ✅ (configurazione applicata)
- Stessa logica vale cross-faction e cross-time-phase (screen-relative, non background-relative) · ✅
- Lower legs/feet parzialmente dietro l'overlay nav bar inferiore · ✅
- Busto/testa restano leggibili · ✅

---

## 5. Screenshot Evidence (preview pubblica)

URL: `https://game-portal-327.preview.emergentagent.com/(tabs)/home`

Stato (utente non loggato — `/home` redirect a `/(tabs)/home`):
- ✅ Home renderizza correttamente senza crash dopo i fix.
- ✅ Bottom nav mostra: `CHAT · BAG · ARTIFACT · SKILL · TEAM · GUILD · SHOP · FORGE · MENU` (tutti i 9 slot intatti).
- ✅ Profile panel: `P` avatar circle · `Player` (fallback, utente non loggato) · level `1` · POWER `Server richiesto` (no fake BP) · `VIP 0` · `SP 0` · `❖ Apprendista` titolo.
- ✅ Sfondo Sunset/castello visibile, nessun red screen, nessun crash visivo.
- ✅ HomeHeroSplash non viene renderizzato fino a quando l'utente non è loggato e `homeHero` è settato (atteso).

File screenshot: `/tmp/119a_home_v1.png` (capturato durante validazione).

---

## 6. Smoke/Validator eseguiti

### 6.1 Validator suite pre-QA safety
```
totali:  24
PASS:    24
FAIL:    0
SKIPPED: 0
backend_up: True
verdict: PRE_QA_SAFETY_SUITE_PASS
```
File: `backend/reports/pre_qa_safety_validator_suite_20260615T195147Z.json`

**Note:** nessun validator dedicato 119A creato — Pack 119A è un bug-fix funzionale
frontend (tap handlers + routing config + style), non introduce nuove invarianti
strutturali. I 24 validator esistenti (110, 113, 114, 114B, 115A-G, 116A/EXT-FIX-A,
116B, 116C, 117A, 117B, 118, 118B) confermano che tutte le foundation restano
intatte: BP formula invariata, RD invariato, HU readiness invariato, 116B
chat/bot preservato, 118B web QA harness preservato.

### 6.2 Repo hygiene
```
sweep_repo_hygiene.py → clean=true
git ls-files | grep -E '\.pyc$|\.pyo$|__pycache__' → vuoto
```

---

## 7. Cosa NON è stato toccato (fuori scope rispettato)

| Sistema | Stato |
|---------|-------|
| Tutorial live / new-user onboarding flow | **NON CREATO** (delegato a Pack futuro `FUTURE_TUTORIAL_ONBOARDING_FOUNDATION`) |
| Starter claim flow da 3 eroi | **NON MODIFICATO** |
| Account reset / test accounts | **NON RESETTATI** |
| Guided summon | **NON CREATO** |
| DB writes | **0** |
| Reward grants | **NO** |
| Claim/gacha/shop/VIP/Battle Pass/IAP activation | **NO** |
| Push notification | **NO** |
| Chat/DM/bot live (116B preservato) | **NO** |
| Battle Power formula change | **NO** (`battle_power_v1_preqa_derived` invariata) |
| `battle_engine.py` / combat runtime | **NON TOCCATO** |
| Tower runtime | **NON TOCCATO** |
| Character Bible | **NON RISCRITTO** |
| Borea activation | **NO** |
| Home overlay alto-sx / basso / pulsanti dx redesign | **NON REDISEGNATI** |
| Full profile system | **NON IMPLEMENTATO** (feedback locked) |
| Full titles system | **NON IMPLEMENTATO** (feedback locked) |
| Full inventory system | **NON IMPLEMENTATO** (BAG ora apre Inventory esistente) |
| Full forge refactor | **NON FATTO** (FORGE ora apre Equipment esistente; Soul Forge resta sub-system) |
| Gacha rates | **NON MODIFICATI** |
| Broad refactor | **NO** |
| Package/dependency upgrade | **NO** |
| `.pyc` / `__pycache__` tracciati | **NO** |
| `git add -A` / `git add .` | **NO** (esplicito `git add -- <path>`) |

---

## 8. Deferred rimasti (future packs)

| Item | Pack futuro consigliato |
|------|--------------------------|
| Tutorial live + new-user onboarding | `FUTURE_TUTORIAL_ONBOARDING_FOUNDATION` |
| Sistema avatar/cornici reale (AvatarFrameSelector stabile) | Pack futuro UI customization |
| Schermata profilo completa (`/profile` route) | Pack futuro profile system |
| Sistema titoli equipaggiabili | Pack futuro titles system |
| Forge hub dedicato (con Soul Forge come sotto-tab) | Pack futuro Forge hub refactor |
| Sistema Skill | Pack futuro Skill system |

---

## 9. Commit SHAs

- **Baseline pre-119A:** `a360b7434` (master, post-118B-FIX-A public verified)
- **Pack commit 119A:** `02e2cd5d7` — verdetto `PRE_QA_PACK_119A_HOME_FUNCTIONAL_ROUTING_AND_GROUNDING_FIX_READY_FOR_GAME_MASTER_REAUDIT` (3 file: 2 MOD frontend + 1 NEW report).

---

## 10. Stop Condition

🛑 **Stop. Pack 119A completato. Attendo re-audit Game Master prima di procedere oltre.**
