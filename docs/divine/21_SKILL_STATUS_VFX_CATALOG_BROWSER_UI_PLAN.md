# RM1.25-D — Skill / Status / Icon / VFX Internal Catalog Browser UI

## Objective
Create a mobile-first read-only screen that lets the team inspect the inert Skill/Status/Icon/VFX catalogs exposed by RM1.25-C.

This is a browser/inspection UI only. It must not connect catalogs to battle runtime, HP bar runtime, live skill activation, live status activation, or VFX runtime.

## Source API
Use only these GET endpoints:

- `/api/skill-status-vfx/catalogs/summary`
- `/api/skill-status-vfx/catalogs/skill-progression`
- `/api/skill-status-vfx/catalogs/status-effects`
- `/api/skill-status-vfx/catalogs/status-icons`
- `/api/skill-status-vfx/catalogs/vfx`
- `/api/skill-status-vfx/catalogs/skill-examples`

Do not import `/app/data/design/skill_status_vfx_catalogs/*.json` directly in frontend code.

## Proposed frontend

Create:

- `/app/frontend/app/skill-status-vfx-catalogs.tsx`

Add menu entry in:

- `/app/frontend/app/(tabs)/menu.tsx`

Suggested label:

- `📚 Catalogo Skill & Status`

Suggested route:

- `/skill-status-vfx-catalogs`

## Required UI sections

1. Summary
   - Counts and runtime flags.
   - Must show `battle_runtime_attached=false`, `ui_runtime_attached=false`, `vfx_runtime_attached=false`.
2. Progressione Skill
   - Rarity -> skill slots.
   - Must clearly show 1★ basic only, 2★ passive base, 3★ skill 1, 4★ passive advanced, 5★ skill 2, 6★ ultimate.
3. Status Effect
   - Status cards/list grouped by category.
   - Search by `status_id`/name/category.
4. Icone Status
   - Metadata cards: icon_key, priority, color family, stack/duration overlay flags.
5. VFX Modulari
   - Group by type/status if possible.
   - Show VFX entries and readability notes.
6. Esempi Skill
   - Show skill examples, targeting summary and presentation_flow summary.

## Safety

- No DB writes.
- No migrations.
- No battle engine changes.
- No frontend HP bar changes.
- No runtime activation.
- No Borea activation.
- No asset changes.

## Smoke requirements

- Page renders on mobile viewport.
- Menu entry works.
- API calls are GET-only.
- Console has no new React error overlay.
- Existing `/api/heroes` remains 100.
- Borea remains hidden.

## Report required

Respond with:

1. Files installed from ZIP
2. Files created/modified by implementation
3. Requirements validator output
4. Frontend smoke results
5. API/network smoke results
6. Safety checks
7. Explicit confirmation that this is read-only UI and not connected to battle/HP bar runtime
