# 89 · Home Battle Flow & Real Battlefield Preview Audit

## Studio read-only del vecchio flusso Home
Ispezionate (sola lettura) le visual preview screens esistenti:
- `frontend/app/story-visual-battle-sandbox.tsx`
- `frontend/app/generic-visual-battle-runner-preview.tsx`
- `frontend/app/training-visual-preview.tsx`, `arena-visual-preview.tsx`, `boss-visual-preview.tsx`, `tower-visual-preview.tsx`, `story-visual-preview.tsx`
- Asset disponibili: `frontend/assets/backgrounds/*.png`, `frontend/assets/placeholders/heroes/<role>/combat_base.png`.

## Tratti del vecchio Home-connected battle visual flow
- Background regionale a tutta schermata (Nordic/Celtic/Egypt/Greek/Japanese).
- Layout a 2 lati: **player sinistra, enemy destra**.
- Sprite `combat_base.png` per ogni unità, scelto per role placeholder.
- Griglia/slot 3 unità per lato; lato player fino a 4 in Boss.
- HP bar sotto allo sprite, indicatore di turno/azione.

## Strategia rescue v89
- Riusare le immagini già esistenti (NO final asset import, NO Character Bible link).
- Mappare ogni alias dei payload v86 a un role -> sprite placeholder ufficiale.
- Mappare ogni mode a uno dei background regionali.
- Mantenere visual layer v87 (HP bar, turn highlight) e experience layer v88 (autoplay/pause/speed/hints/toast/summary).

## Vincoli
- `db_writes=0`, `reward_live=false`, `endpoint_live=false`, `battle_engine_authoritative=false`.
- MD5 lock 8/8 intatti. Nessuna mutazione di Character Bible/hero roster.
