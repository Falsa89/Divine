# 181E — VIP Locked UI Preview Policy

**Track:** E — Locked UI Preview Policy
**Verdict:** `TRACK_E_VIP_LOCKED_UI_PREVIEW_POLICY_READY`
**Pack:** `PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION`

## Decisione strategica
- `frontend_vip_modified_in_this_pack`: **`false`**
- **Rationale:** Design contract per modernization futura. L'implementation UI segue in un sub-pack dedicato con autorizzazione esplicita dell'utente. Mantenere `vip.tsx` MD5 invariato minimizza regression risk.

## Future Implementation — Allowed Changes (guarded)
1. Migliorare copy: "VIP — Aura Divina" con tier badges 0..10 preview
2. Mostrare tier ladder preview con locked pills sui tier 1-10
3. Mostrare benefit list (cosmetic + convenience) per tier con explicit lock label
4. Price placeholder (`<<VIP_TIER_X>>`) per crystals required
5. Link a `/shop` preview (still locked)
6. Accessibility: min touch targets **44pt iOS / 48dp Android**
7. Mobile layout: **SafeAreaView + ScrollView**; no fixed positioning; no `KeyboardAvoidingView` (no input)

## Future Implementation — Forbidden Changes (hard)
- Active claim button bypassing `VIP_LOCKED_V2`
- Active buy-tier button (VIP è spend-based, non purchased; tier upgrades vengono da IAP crystal packs)
- `apiCall` a `/api/vip/claim-daily` mentre `VIP_LOCKED_V2`
- IAP SDK import
- Real product ID literal
- Direct ledger write
- Countdown < 60s
- Hidden price
- Hidden tier benefit
- Removal o weakening di `VIP_LOCKED_V2`

## Locked State Invariants (richiesti dopo qualunque modifica futura)
```
VIP_LOCKED_V2_must_remain_true   = true
claim_button_disabled            = true
no_buy_tier_button_visible       = true
lock_banner_visible              = true
no_live_api_call_on_press        = true
```

## Copy Proposals IT
| Field | Copy IT |
|---|---|
| `page_title` | VIP — Aura Divina |
| `lock_banner` | VIP in preparazione. Il sistema di spesa reale (IAP) e i benefit non sono ancora attivi. |
| `tier_0_label` | VIP 0 — Visitatore |
| `tier_n_locked_pill` | Bloccato — in preparazione |
| `claim_button_label_locked` | Disponibile presto |
| `benefit_list_locked_note` | Benefit anteprima — non riscuotibili ora. |
| `discount_note` | Sconto su pacchetti Cristalli fino al 20% a VIP 10 (anteprima). |

## Accessibility Requirements
- `min_touch_target_pt`: 44 (iOS)
- `min_touch_target_dp`: 48 (Android)
- `screen_reader_labels_present`: `true`
- `high_contrast_locked_pill_color`: `true`

## Mobile Layout Requirements
- `safe_area_view_required`: `true`
- `scrollview_or_flashlist_required`: `true`
- `no_fixed_positioning`: `true`
- `keyboard_avoiding_view_needed`: `false`

## Verdict
`TRACK_E_VIP_LOCKED_UI_PREVIEW_POLICY_READY` — `vip.tsx` MD5 invariato in questo pack. Policy completo per future modernization sub-pack.
