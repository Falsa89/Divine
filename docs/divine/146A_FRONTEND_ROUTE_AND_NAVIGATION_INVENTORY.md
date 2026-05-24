# 146A — FRONTEND ROUTE & NAVIGATION INVENTORY

## Track A — `PROJECT_X_TRACK_A`

**Verdict:** `TRACK_A_FRONTEND_ROUTE_AND_NAVIGATION_INVENTORY_READY`

## 1. Obiettivo

Produrre un inventario canonico read-only di tutte le route, screen e voci di navigazione del frontend Expo.

## 2. Tab bar (`/app/frontend/app/(tabs)/_layout.tsx`)

| Tab | Label | Icon | Note |
|---|---|---|---|
| `home` | Home | ⌂ | tab bar nascosta — usa custom BottomNav |
| `heroes` | Eroi | ⚔️ | visibile |
| `battle` | Battaglia | 🔥 | visibile |
| `gacha` | Evoca | ⭐ | visibile |
| `menu` | Menu | ☰ | visibile |

## 3. Root routes (45 screen)

`index`, `combat`, `hero-detail`, `hero-viewer`, `hero-collection`, `hero-encyclopedia`, `hero-training`, `hero-skill-kits-catalog`, `divine-weapons-catalog`, `skill-status-vfx-catalogs`, `synergy-codex`, `affinity-gifts-preview`, `collection-synergies-preview`, `story`, `tower`, `pvp`, `raid`, `gvg`, `sanctuary`, `equipment`, `exclusive`, `artifacts`, `soul-forge`, `cosmetics`, `achievements`, `battlepass`, `treasury`, `economy`, `inventory`, `item-shop`, `shop`, `vip`, `guild`, `player-faction`, `plaza`, `dm`, `mail`, `friends`, `rankings`, `servers`, `events`, `territory`, `select-home-hero`, `sprite-test`, `dev-combat-qa-lab`.

## 4. Voci di menu (34) per categoria

- **Combattimento** (5): Storia, Torre, Arena PvP, Fucina di Efesto, Oggetti Esclusivi
- **Progressione** (7): Collezione Eroi, Addestramento Eroico, Santuario, Artefatti & Costellazioni, Soul Forge, Aure & Cosmetici, Achievement, Battle Pass
- **Economia** (7): Tesoreria, Economia & Negozi, Inventario, Negozio Oggetti, Negozio, VIP, Sprite Test
- **Sociale** (7): Gilda & Fazioni, Fazione del Giocatore, Guerra tra Gilde, Raid Cooperativi, Conquista Territori, Piazza Comunitaria, Messaggi
- **Altro** (8): Classifiche, Posta, Amici, Seleziona Server, Eventi Giornalieri, Combat QA Lab (DEV), Catalogo Skill & Status, Kit Skill Eroi

## 5. Screen dev/admin only

- `/dev-combat-qa-lab`
- `/sprite-test`

## 6. Screen senza dipendenze backend

- `/affinity-gifts-preview`
- `/collection-synergies-preview`
- `/sprite-test`

## 7. Screen con dipendenze backend (estratto principale)

Vedi `project_x_frontend_route_inventory_v1.json` per la mappa completa endpoint-screen.

## 8. Screen dead / unreachable / legacy

Nessuno rilevato.

## 9. Validator

`validate_project_x_frontend_route_inventory_v1.py` → **PASS**.
