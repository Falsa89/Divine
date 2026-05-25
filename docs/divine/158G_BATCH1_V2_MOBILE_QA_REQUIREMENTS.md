# 158G — Post-Lock Mobile QA & Regression Requirements (Track G)

Verdetto: `TRACK_G_POST_LOCK_MOBILE_QA_AND_REGRESSION_REQUIREMENTS_READY`

## Checklist QA (9 aree)
1. **gacha**: banner artifact/constellation invisibili; premium/targeted badge IN REVISIONE; pulsanti disabilitati.
2. **artifacts**: deep link a `/artifacts` mostra loading + redirect a `/artifacts-preview`.
3. **shop**: banner lock; tap COMPRA → nessuna richiesta network.
4. **item-shop**: banner lock; tap card → nessun modal quantità.
5. **battlepass**: banner lock; PREMIUM “IN REVISIONE”; Riscuoti non attivo.
6. **vip**: banner lock; Riscuoti Gemme VIP non visibile.
7. **soul_forge**: eroi 4★+ con badge 🔒; Tutti seleziona solo 1–3★; modal conferma con breakdown; typed CONFERMA per rischio.
8. **menu**: assenza Sprite Test / Combat QA Lab; Artefatti & Costellazioni → /artifacts-preview.
9. **regression**: /heroes, /battle, /servers, /events, /achievements, /mail invariati; nessuna nuova chiamata API mutativa introdotta.

L'utente è invitato a eseguire la QA mobile reale su tutti questi punti dopo il restart Expo.
