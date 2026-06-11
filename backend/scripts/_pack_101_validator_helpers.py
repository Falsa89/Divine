#!/usr/bin/env python3
"""Pack 101 — helper module per estrarre il body di una funzione async nested."""
import re


def extract_async_fn_body(src: str, name: str) -> str:
    """Estrae il corpo di una specifica async def, anche se nested.

    Cerca da `async def <name>(` fino al prossimo decoratore `@router.` (allo
    stesso livello di indentazione) o fine file.
    """
    idx = src.find(f'async def {name}(')
    if idx < 0:
        return ''
    # Determina indent
    line_start = src.rfind('\n', 0, idx) + 1
    indent = src[line_start:idx]
    # Cerca prossimo `<indent>@router.` o `<indent>async def ` o EOF
    rest = src[idx:]
    # Match successivo decoratore o async def allo stesso livello
    next_match = re.search(rf'(?m)^{re.escape(indent)}(@router\.|async def |def )', rest[1:])
    if next_match:
        end = next_match.start() + 1  # +1 perché abbiamo skippato il primo char
        return rest[:end]
    return rest
