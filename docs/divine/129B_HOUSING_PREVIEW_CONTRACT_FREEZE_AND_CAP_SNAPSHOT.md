# 129B — Housing Preview Contract Freeze & Cap Snapshot (Track B)

**Verdict:** `TRACK_B_HOUSING_PREVIEW_CONTRACT_FROZEN_INERT`

## Contract freeze
- Endpoint: `/api/housing/preview`
- Default GET = 503 con `HOUSING_PREVIEW_ENABLED` unset.
- Envelope flag-ON: zero-bonus, `live_bonus_applied=False`,
  `db_writes=False`, `combat_mutation=False`.
- `housing_bonus_resolver_stub` NOT imported dal route.
- 0 DB writes nel modulo.

## Housing cap snapshot v1
7 sub-strutture:
1. **per_room** — hp/atk/def_pct max 1.5, crit_pct max 0.5.
2. **category** — buff_room / defense_room / crit_room aggregate caps.
3. **item** — per item max 0.5pp, max 6 item per room.
4. **bonus** — types_allowed = {hp_pct, atk_pct, def_pct, crit_pct}; types_forbidden = {flat_damage, true_damage, crit_dmg_pct, crit_resist_pct}.
5. **mode** — global_roster=true, battle_inheritance=false, pvp_application=false, pve_application_gated=true.
6. **master_cap** — hp/atk/def_pct 5.0, crit_pct 2.0, aggregate 10.0.
7. **vip_vault_secondary_cap** — secondario sotto master_cap (verificato).

## Vincoli rispettati
- NO Housing live bonus; NO DB writes; NO battle/account stat mutation;
  NO frontend/UI.
