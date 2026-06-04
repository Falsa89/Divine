# 450 — v72 P3 Polish Carry-forward (v74)

Pack: `MEGA_RELEASE_ACCELERATION_23_v74`

## 3 finding P3 in carry-forward (da v72->v73->v74)

1. `p3_alpha_preview_hub_copy_shortening`
2. `p3_first_session_state_label_line_height_margin`
3. `p3_alpha_preview_hub_qa_priority_ordering`

## Decisione v74

- apply_now: false
- aggregate_into_future_polish_batch: true
- target_batch: `future_polish_batch_v75_or_later`
- is_blocker: false
- safe_to_fix_later: true
- db_writes: 0

## Motivazione

v74 e' focalizzato su menu exposure apply + closed alpha kickoff gate. Polish P3 non e' blocker e puo' essere applicato in un polish batch dedicato (sicuro, UI-only) in v75+.
