# 152F — Track F: Frontend Lock / Preview Recommendation

**Verdict:** `TRACK_F_SERVER_PROFILES_FRONTEND_LOCK_OR_PREVIEW_RECOMMENDATION_READY` · audit-only

## Opzioni valutate (5)
| Option | Player safety | UX impact | Recommended |
|---|---|---|---|
| keep_visible_unchanged | MEDIUM | LOW | ❌ |
| hide_from_menu | HIGH | MEDIUM | ❌ |
| **convert_to_locked_preview** | HIGH | LOW | ✅ |
| move_to_dev_admin_only | HIGH | LOW | ❌ |
| keep_with_warning_banner | MEDIUM | LOW | ❌ |

## Raccomandazione
**convert_to_locked_preview** — pattern identico a `/artifacts-preview`, `/housing-preview`. Zero mutation. Zero UX cliff.

### Copy proposto
- **Titolo:** "Selezione Server (Anteprima)"
- **Body:** "La selezione del server è in fase di aggiornamento. Resterai sul server attuale finché la nuova esperienza Server Profiles non sarà disponibile."
- **Badge:** 🔒 In arrivo
- **Action buttons:** *(nessuno)*

## Recommended next pack
`PROJECT_SERVER_PROFILES_UI_LOCK_PREVIEW_PACK`
