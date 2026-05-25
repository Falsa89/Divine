# 149F — FRONTEND NAVIGATION RISK & MISSING LINKS MATRIX

## Track F — `PROJECT_FRONTEND_B_TRACK_F`

**Verdict:** `TRACK_F_FRONTEND_NAVIGATION_RISK_AND_MISSING_LINKS_MATRIX_READY`

## Navigation risk matrix (8 aree)

| Area | Risk | Note |
|---|---|---|
| Tab navigation | low | 5 tab stabili |
| Menu sezioni | low | 5 categorie, 35 voci |
| Combat flow | medium | combat.tsx 1848 LOC |
| Hero training breadcrumb | medium | mancanza breadcrumb |
| Economy hub | medium | shop/economy/item-shop relazione |
| Safe previews | low | hub Pack Z funzionante |
| Server selection | medium | 503 su select pu\u00f2 confondere |
| Dev/admin gating | **high_for_polish** | sprite-test/dev-combat-qa-lab visibili in menu prod |

## Missing links (5)

1. hero-detail → hero-encyclopedia (link diretto)
2. combat post-battle → hero-detail nuovi eroi
3. gacha reveal → team formation
4. battlepass → daily checklist (oggi inesistente)
5. main home → /safe-previews (solo via menu Altro)

## Stato globale

`navigation_health = good_with_known_gaps` — `broad_refactor_required = false`.

## Validator

`validate_project_frontend_b_navigation_risk_matrix_v1.py` → **PASS**.
