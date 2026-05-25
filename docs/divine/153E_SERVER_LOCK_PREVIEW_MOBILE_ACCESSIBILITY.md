# 153E — Server Lock Preview Mobile / Accessibility

**Verdict:** `TRACK_E_SERVER_LOCK_PREVIEW_MOBILE_ACCESSIBILITY_READY`

## Mobile checks
- `SafeAreaView` + `ScrollView` per safe scroll
- Viewports verificati staticamente: 390x844 (iPhone 12-14), 360x800 (Galaxy S21)
- `serverRow` `minHeight: 56px` — readable & non-actionable

## Accessibility checks
- `accessibilityLabel="Indietro"` su back button
- `accessibilityRole="button"` su back button
- `accessibilityRole="header"` su banner
- `accessibilityLabel` descrittivo su ogni server row: `Server {name}, selezione disabilitata`
- `accessibilityState={{disabled: true}}` su ogni row
- 0 TouchableOpacity per selezione server (touch targets non implicano switching)

## Polish raccomandato (non bloccante)
- back button 40×40 — sotto la HIG iOS 44×44; coerente con altri preview screens. Futuro polish pack.

## No fake QA
- 0 fake mobile screenshot verification
