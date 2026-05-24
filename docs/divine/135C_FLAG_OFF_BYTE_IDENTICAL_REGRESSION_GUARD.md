# 135C — FLAG OFF BYTE-IDENTICAL REGRESSION GUARD

**Pack**: `PROJECT_M` — Track C
**Verdict**: `TRACK_C_FLAG_OFF_BYTE_IDENTICAL_REGRESSION_GUARD_READY`
**Marker JSON**: `/app/data/design/status_effects/project_m_flag_off_byte_identical_regression_v1.json`
**Validator**: `/app/backend/scripts/validate_project_m_flag_off_byte_identical_regression_v1.py`

## Fixture deterministica

- `random.seed(42)` prima della costruzione dei team.
- 2 team di 3 personaggi sintetici (`c0..c2` vs `c10..c12`), stats incrementali (`attack=100+i`, `defense=50+i`, `hp=1000+i*10`).
- `simulate_battle(team_a, team_b, max_turns=5)`.

## Stable payload

I campi stabili usati per il confronto byte-identical:

```
winner
turns
final_hp_a (sorted list of (id, current_hp))
final_hp_b (sorted list of (id, current_hp))
```

Nessuna normalizzazione di campi gameplay; solo l'ordinamento per `id` per stabilità deterministica della rappresentazione.

## Risultato

```
stable: {"final_hp_a": [["c0", 0], ["c1", 141], ["c2", 1020]],
          "final_hp_b": [["c10", 0], ["c11", 390], ["c12", 1120]],
          "turns": 5, "winner": null}
sha256: d951767a72b54b339eb660f6308d72c943a9a9e318539f639ce9fc7f416d3725
```

Pre-patch e post-patch coincidono **byte-identical**.

## Conformità ai guardrail

- ✅ No fake normalization hiding gameplay changes.
- ✅ No DB write.
- ✅ Test in-process, isolato.
