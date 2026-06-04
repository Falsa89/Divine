# 97 — Physical Mobile QA Checklist

## Pack

`MEGA_RELEASE_ACCELERATION_46_v97`

## Stato

QA fisico **MANUAL_QA_REQUIRED**, non eseguito automaticamente nel container. Nessun fake PASS.

## Checklist Android device

- [ ] Build dev/test su Android device fisico (API 26+)
- [ ] Avvio app senza crash
- [ ] Login guest funzionante
- [ ] Session restore dopo riavvio app
- [ ] Logout
- [ ] Logout-all (v97)
- [ ] Refresh token rotation trasparente
- [ ] Delete account request soft
- [ ] Privacy status visibile
- [ ] Formation fetch authenticated
- [ ] Battle engine smoke (almeno 1 simulazione)
- [ ] Live/Guild QA Hub accessibile
- [ ] Live Announcements QA sandbox
- [ ] War event avatar previews
- [ ] Guild War sandbox
- [ ] Contextual bot chat demo (UI)
- [ ] Performance under low memory device

## Checklist iOS device

- [ ] Build TestFlight su iOS device fisico
- [ ] Avvio app senza crash
- [ ] Login guest funzionante
- [ ] **Login Apple visibile** (iOS-only)
- [ ] Session restore
- [ ] Logout, logout-all, refresh token rotation
- [ ] Delete account request soft
- [ ] Privacy status
- [ ] Formation fetch authenticated
- [ ] Battle engine smoke
- [ ] Live/Guild QA Hub
- [ ] Live Announcements QA sandbox
- [ ] War event avatar previews
- [ ] Guild War sandbox
- [ ] Contextual bot chat demo
- [ ] Background/foreground transitions

## 15 modes smoke

Story, Tower, Arena, Training, Raid, Event, Guild Live, Guild War, Guild Raid, World Boss, Faction Boss, Territory, Crepuscolo Titani, Assalto Ragnarok, Summer Invasion.

## Blockers internal alpha

1. Esecuzione fisica Android.
2. Esecuzione fisica iOS (TestFlight).
3. Real provider credentials (per Google/Apple end-to-end).
