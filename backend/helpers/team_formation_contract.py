"""HOTFIX E — TeamFormation V1 Contract centralizzato (read-only).

Centralizza:

  1. la **forma canonica V1** di ogni slot salvato:
       {"user_hero_id", "canonical_id", "col", "row"}
  2. il **parsing legacy** (starter `{slot_index, user_hero_id}`,
     pre-V1 ambiguo `{hero_id, col, row}`) → normalizzazione a V1
     **on-read**, senza scritture DB;
  3. la **validazione save V1** (ownership user_hero_id, cross-check
     canonical_id == user_heroes.hero_id, no duplicates, cap dim);
  4. i **blocker codes** che backend e frontend devono usare.

ZERO DB writes. ZERO chiamate runtime esterne. Solo funzioni di
parsing / lookup helper + costanti. Importato sia da
`backend/routes/v96_team_formation.py` sia da
`backend/helpers/real_player_snapshot.py` sia dai validator HOTFIX E.

Reference Pack 87/88/125 (intoccati, solo letti).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# ── Contract metadata ──────────────────────────────────────────────────────
TEAM_FORMATION_CONTRACT_VERSION = "hotfix_e_team_formation_v1"

# Backend team size cap. NON aumentato da HOTFIX E (Pack 125 cap = 6).
TEAM_FORMATION_V1_MAX_MEMBERS = 6

# Grid coords range (3x3 visiva). Backward-compat: col/row ∈ [0,2].
TEAM_FORMATION_V1_COL_MIN = 0
TEAM_FORMATION_V1_COL_MAX = 2
TEAM_FORMATION_V1_ROW_MIN = 0
TEAM_FORMATION_V1_ROW_MAX = 2


# ── Blocker codes ──────────────────────────────────────────────────────────
# Tutti emessi da `/api/team/save-formation` (V1) o da
# `/api/team/get-formation` (normalize-on-read).
TEAM_FORMATION_V1_REQUIRED = "TEAM_FORMATION_V1_REQUIRED"
TEAM_FORMATION_USER_HERO_ID_REQUIRED = "TEAM_FORMATION_USER_HERO_ID_REQUIRED"
TEAM_FORMATION_CANONICAL_ID_REQUIRED = "TEAM_FORMATION_CANONICAL_ID_REQUIRED"
TEAM_FORMATION_OWNED_HERO_NOT_FOUND = "TEAM_FORMATION_OWNED_HERO_NOT_FOUND"
TEAM_FORMATION_SERVER_SCOPE_MISMATCH = "TEAM_FORMATION_SERVER_SCOPE_MISMATCH"
TEAM_FORMATION_CANONICAL_MISMATCH = "TEAM_FORMATION_CANONICAL_MISMATCH"
TEAM_FORMATION_DUPLICATE_USER_HERO = "TEAM_FORMATION_DUPLICATE_USER_HERO"
TEAM_FORMATION_DUPLICATE_CELL = "TEAM_FORMATION_DUPLICATE_CELL"
TEAM_FORMATION_TOO_MANY_MEMBERS = "TEAM_FORMATION_TOO_MANY_MEMBERS"
TEAM_FORMATION_LEGACY_AMBIGUOUS = "TEAM_FORMATION_LEGACY_AMBIGUOUS"


# ── slot_index → (col, row) ────────────────────────────────────────────────
# Convenzione documentata (mirror di frontend/app/(tabs)/battle.tsx):
#   slot_index = col*3 + row  (col 0..2, row 0..2).
# Usata SOLO per leggere legacy starter formation `{slot_index, user_hero_id}`
# creata da `POST /api/psp/starter/claim` (Pack 87).
def slot_index_to_grid(slot_index: int) -> Tuple[int, int]:
    si = max(0, min(8, int(slot_index)))
    col = si // 3
    row = si % 3
    return (col, row)


# ── V1 normalization (on-read) ─────────────────────────────────────────────
def normalize_slot_to_v1(
    entry: Dict[str, Any],
    owned_by_user_hero_id: Optional[Dict[str, Dict[str, Any]]] = None,
    owned_by_canonical_id: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Normalizza un singolo slot a V1.

    Input legacy supportati:
      A. {"user_hero_id": ..., "slot_index": int}                 (Pack 87 starter)
      B. {"user_hero_id": ..., "col": int, "row": int}            (Pack 125+)
      C. {"hero_id": ..., "col": int, "row": int}                 (pre-V1 ambiguo)
      D. {"user_hero_id": ..., "canonical_id": ..., "col", "row"} (V1 nativo)

    Per il caso C, `hero_id` può significare owned-id (= user_heroes.id) OPPURE
    canonical-id (= user_heroes.hero_id). Usiamo i due lookup map per
    disambiguare:
      - se matcha owned_by_user_hero_id → trattato come owned id legacy;
      - se matcha owned_by_canonical_id univocamente → owned + canonical
        derivati;
      - se matcha owned_by_canonical_id in modo ambiguo (multipli) → error
        blocker `TEAM_FORMATION_LEGACY_AMBIGUOUS`.

    Ritorna (slot_v1_dict, None) on success, (None, blocker_code) on failure.
    NESSUN DB read qui: i lookup map sono passati dal chiamante.
    """
    if not isinstance(entry, dict):
        return (None, TEAM_FORMATION_V1_REQUIRED)
    owned_by_user_hero_id = owned_by_user_hero_id or {}
    owned_by_canonical_id = owned_by_canonical_id or {}

    user_hero_id: Optional[str] = entry.get("user_hero_id")
    canonical_id: Optional[str] = entry.get("canonical_id")
    legacy_hero_id: Optional[str] = entry.get("hero_id")

    # Caso ambiguo: hero_id sostituiva entrambi nei record pre-V1.
    if not user_hero_id and legacy_hero_id:
        # Tentativo 1: hero_id == owned user_heroes.id (legacy v1).
        if legacy_hero_id in owned_by_user_hero_id:
            user_hero_id = legacy_hero_id
            uh_doc = owned_by_user_hero_id[legacy_hero_id]
            canonical_id = canonical_id or uh_doc.get("hero_id")
        # Tentativo 2: hero_id == user_heroes.hero_id (canonical), match univoco.
        elif legacy_hero_id in owned_by_canonical_id:
            matches = owned_by_canonical_id[legacy_hero_id]
            if len(matches) == 1:
                uh_doc = matches[0]
                user_hero_id = uh_doc.get("user_hero_id") or uh_doc.get("id")
                canonical_id = canonical_id or uh_doc.get("hero_id")
            else:
                return (None, TEAM_FORMATION_LEGACY_AMBIGUOUS)
        else:
            return (None, TEAM_FORMATION_OWNED_HERO_NOT_FOUND)

    if not user_hero_id:
        return (None, TEAM_FORMATION_USER_HERO_ID_REQUIRED)

    # Derive canonical_id se non presente.
    if not canonical_id:
        uh_doc = owned_by_user_hero_id.get(user_hero_id)
        if uh_doc:
            canonical_id = uh_doc.get("hero_id")
    if not canonical_id:
        return (None, TEAM_FORMATION_CANONICAL_ID_REQUIRED)

    # Derive col/row da: campi diretti → slot_index → (0,0) fallback documentato.
    col = entry.get("col")
    row = entry.get("row")
    if col is None or row is None:
        si = entry.get("slot_index")
        if isinstance(si, int):
            col, row = slot_index_to_grid(si)
        else:
            # Senza coords valide: blocker (refuse-by-default).
            return (None, TEAM_FORMATION_V1_REQUIRED)
    try:
        col = max(TEAM_FORMATION_V1_COL_MIN, min(TEAM_FORMATION_V1_COL_MAX, int(col)))
        row = max(TEAM_FORMATION_V1_ROW_MIN, min(TEAM_FORMATION_V1_ROW_MAX, int(row)))
    except Exception:
        return (None, TEAM_FORMATION_V1_REQUIRED)

    return (
        {
            "user_hero_id": str(user_hero_id),
            "canonical_id": str(canonical_id),
            "col": col,
            "row": row,
        },
        None,
    )


def normalize_team_formation_to_v1(
    team_formation: List[Dict[str, Any]],
    owned_by_user_hero_id: Optional[Dict[str, Dict[str, Any]]] = None,
    owned_by_canonical_id: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Normalizza l'intera team_formation a V1 con normalize-on-read.

    Ritorna `(v1_slots, warnings)`:
      - `v1_slots`: lista di slot canonicalizzati. Ordine preservato.
      - `warnings`: lista di `{index, blocker, raw_entry}` per slot che non
        è stato possibile normalizzare (refuse-by-default, non scartiamo
        silenziosamente: il chiamante decide se bloccare l'intera read).
    """
    v1: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    if not isinstance(team_formation, list):
        return ([], [{"index": -1, "blocker": TEAM_FORMATION_V1_REQUIRED, "raw_entry": team_formation}])
    for i, entry in enumerate(team_formation):
        slot, err = normalize_slot_to_v1(entry, owned_by_user_hero_id, owned_by_canonical_id)
        if slot:
            v1.append(slot)
        else:
            warnings.append({"index": i, "blocker": err or TEAM_FORMATION_V1_REQUIRED, "raw_entry": entry})
    return (v1, warnings)


# ── V1 save validation ─────────────────────────────────────────────────────
def validate_v1_team_for_save(
    slots: List[Dict[str, Any]],
    owned_by_user_hero_id: Dict[str, Dict[str, Any]],
    server_id: str,
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, Any]]]:
    """Valida `slots` (lista già in forma V1) per `POST /api/team/save-formation`.

    Returns `(validated_slots, None)` on success, `(None, err)` on failure
    where `err` = `{"blocker": "<CODE>", "detail": ...}`.
    """
    if not isinstance(slots, list):
        return (None, {"blocker": TEAM_FORMATION_V1_REQUIRED})
    if len(slots) > TEAM_FORMATION_V1_MAX_MEMBERS:
        return (None, {
            "blocker": TEAM_FORMATION_TOO_MANY_MEMBERS,
            "max": TEAM_FORMATION_V1_MAX_MEMBERS,
            "received": len(slots),
        })
    seen_user_hero_ids: set = set()
    seen_cells: set = set()
    out: List[Dict[str, Any]] = []
    for i, s in enumerate(slots):
        if not isinstance(s, dict):
            return (None, {"blocker": TEAM_FORMATION_V1_REQUIRED, "index": i})
        uh_id = s.get("user_hero_id")
        canonical_id = s.get("canonical_id")
        col = s.get("col")
        row = s.get("row")
        if not uh_id:
            return (None, {"blocker": TEAM_FORMATION_USER_HERO_ID_REQUIRED, "index": i})
        if not canonical_id:
            return (None, {"blocker": TEAM_FORMATION_CANONICAL_ID_REQUIRED, "index": i})
        if col is None or row is None:
            return (None, {"blocker": TEAM_FORMATION_V1_REQUIRED, "index": i})
        owned = owned_by_user_hero_id.get(str(uh_id))
        if not owned:
            return (None, {
                "blocker": TEAM_FORMATION_OWNED_HERO_NOT_FOUND,
                "user_hero_id": uh_id,
                "index": i,
            })
        # Server-scope: il record owned deve essere sul server_id richiesto.
        # Tolleriamo `_qa_seed` (cross-server) come da Pack 125 policy.
        owned_sid = owned.get("server_id")
        if owned_sid != server_id and not owned.get("_qa_seed"):
            return (None, {
                "blocker": TEAM_FORMATION_SERVER_SCOPE_MISMATCH,
                "user_hero_id": uh_id,
                "owned_server_id": owned_sid,
                "requested_server_id": server_id,
                "index": i,
            })
        # Cross-check canonical_id vs user_heroes.hero_id.
        owned_canonical = owned.get("hero_id")
        if owned_canonical and str(owned_canonical) != str(canonical_id):
            return (None, {
                "blocker": TEAM_FORMATION_CANONICAL_MISMATCH,
                "user_hero_id": uh_id,
                "owned_canonical": owned_canonical,
                "submitted_canonical": canonical_id,
                "index": i,
            })
        if uh_id in seen_user_hero_ids:
            return (None, {
                "blocker": TEAM_FORMATION_DUPLICATE_USER_HERO,
                "user_hero_id": uh_id,
                "index": i,
            })
        cell = (col, row)
        if cell in seen_cells:
            return (None, {
                "blocker": TEAM_FORMATION_DUPLICATE_CELL,
                "cell": {"col": col, "row": row},
                "index": i,
            })
        seen_user_hero_ids.add(uh_id)
        seen_cells.add(cell)
        out.append({
            "user_hero_id": str(uh_id),
            "canonical_id": str(canonical_id),
            "col": int(col),
            "row": int(row),
        })
    return (out, None)


__all__ = [
    "TEAM_FORMATION_CONTRACT_VERSION",
    "TEAM_FORMATION_V1_MAX_MEMBERS",
    "TEAM_FORMATION_V1_REQUIRED",
    "TEAM_FORMATION_USER_HERO_ID_REQUIRED",
    "TEAM_FORMATION_CANONICAL_ID_REQUIRED",
    "TEAM_FORMATION_OWNED_HERO_NOT_FOUND",
    "TEAM_FORMATION_SERVER_SCOPE_MISMATCH",
    "TEAM_FORMATION_CANONICAL_MISMATCH",
    "TEAM_FORMATION_DUPLICATE_USER_HERO",
    "TEAM_FORMATION_DUPLICATE_CELL",
    "TEAM_FORMATION_TOO_MANY_MEMBERS",
    "TEAM_FORMATION_LEGACY_AMBIGUOUS",
    "slot_index_to_grid",
    "normalize_slot_to_v1",
    "normalize_team_formation_to_v1",
    "validate_v1_team_for_save",
]
