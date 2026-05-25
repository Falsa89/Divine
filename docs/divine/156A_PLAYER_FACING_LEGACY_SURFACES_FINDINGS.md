# 156A — Player-Facing Legacy Surfaces Findings (Track A)

Pack: `PROJECT_PLAYER_FACING_LEGACY_SURFACES_LOCK_AND_AUDIT_PACK`
Verdetto: `TRACK_A_MOBILE_QA_AND_REPO_FINDINGS_CONSOLIDATION_READY`
Modalità: audit-only (zero scritture DB / zero modifiche economy).

## Sintesi
- 8 findings da mobile QA reale dell'utente
- 9 findings da audit della repo pubblica
- 1 critical (artifact live endpoints esposti) + 7 high + 4 medium

## Cross-reference
File canonico: `/app/data/design/mobile_qa/project_player_facing_legacy_surfaces_findings_v1.json`.
Validator: `validate_player_facing_legacy_surfaces_findings_v1.py`.

## Classificazioni
- ok: daily-hub, servers (locked), battle
- ux_bug: safe-previews (tap senza navigazione)
- legacy_surface: shop, battlepass, artifacts live, menu dev/legacy entries
- economy_risk: gacha rates premium 5★/6★, x10 osservata 4 mitici + 3 leggendari
- data_visibility_risk: heroes list non filtrata

## Track follow-up
- Track B: fix navigation-only safe-previews
- Track C: artifact/constellation surface audit
- Track D: gacha rate sanity
- Track E: shop/IAP readiness
- Track F: battle pass audit
- Track G: heroes/menu legacy audit
- Track H: completion + next pack order
