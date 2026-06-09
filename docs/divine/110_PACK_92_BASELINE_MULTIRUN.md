# Pack 92 — Baseline Multirun (pre-modifiche)

3 esecuzioni consecutive di `python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py`:

| Run | pass | fail | miss | required_fail |
|-----|------|------|------|---------------|
| 1   | 1490 | 29   | 0    | 0             |
| 2   | 1490 | 29   | 0    | 0             |
| 3   | 1490 | 29   | 0    | 0             |

`deterministic=true`. Stop conditions (REQUIRED>0, MISS>0, OPTIONAL>30, regressioni Pack 77/80/81/82/83/84/85/86/87/88/89/90/91) **non scattate**.
